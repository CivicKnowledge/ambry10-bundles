# -*- coding: utf-8 -*-
import ambry.bundle
from ambry.etl import RowGenerator

class GenerateVars(RowGenerator):
    
    def __iter__(self):
        import requests
        
        api_source = self._bundle.source('api')

        def make_url(f):
            return "{}/{}".format(api_source.url, f)

        headers = {'Ocp-Apim-Subscription-Key': api_source.account.decrypt_secret()}

        url = make_url('metadata')

        self._bundle.log(url)

        r = requests.get(url, headers=headers)

        r.raise_for_status()

        from operator import itemgetter
        ig = None
        
        for i, row in enumerate(r.json()):
            if not ig: # Ensure that every row has values in the same order
                header = row.keys()
                yield header
                ig = itemgetter(*header)
              
                
            yield ig(row)

headers = [
        ('geoname', str, None, 'Common name of geographic region'), 
        ('geotype', str,None, ' Name of the type of geographic region'),
        ('geoid', str, None, 'Identification number for the geographic region'),
        ('supressed', str,None,  'If True, estimates for this region have been supressed'),
        ('suppresed_reason', str,None,  'The reason that a estimate is supressed'), 
        ("population", int,'^cvt_pop_str', 'Population estimate for the geographic region. A value of 0 indicates a population less than 500'),
        ("estimate", float,None, 'Measurement estimate'), 
        ("SE", float, None, 'Standard error in the measure estimate'),
        ("CI_LB95", float, None, 'Lower bound on the 95% confidence interval'),
        ("CI_UB95", float, None, 'Upper bound on the 95% confidence interval'),
        ("CV", float,None, 'Coefficient of variation of the measurement estimate.'),
        ("MSE", float, None, 'Mean Squared Error')]
           

class GenerateDataRows(RowGenerator):
    
    def __iter__(self):
        import requests

        api_source = self._bundle.source('api')

        def make_url(f, v):
            return "{}/{}/{}".format(api_source.url, f, v)

        request_headers = {'Ocp-Apim-Subscription-Key': api_source.account.decrypt_secret()}

        url = make_url('variable', self._source.name.upper())

        self._bundle.log(url)

        r = requests.get(url, headers=request_headers)

        r.raise_for_status()

        d = r.json()[0]

        row_headers = [h[0].lower() for h in headers]

        yield row_headers

        for drow in d['geographies']:
            row = [drow['geoName'], drow['geoTypeId'],drow['geoId'],
                   drow['isSuppressed'], drow['suppressionReason']]
            row += drow['attributes']
         
            #d =  dict(zip(row_headers, row))

            yield row
        
          
class Bundle(ambry.bundle.Bundle):
    
    def edit_pipeline(self, pl):
        """Alter the pipeline to add the final routine and the custom partition selector"""
        
        from ambry.etl import SelectPartition
        
        # No longer needed, now that the table descriptions have been extracted
        #pl.final = [self.edit_descriptions]
        
        pl.select_partition = [SelectPartition(
        'dict(table=source.dest_table.name,'
        'segment=source.sequence_id,'
        'grain=row.geotype if \'geotype\' in row else None)'
        )]
        return pl
    
    def cvt_pop_str(self, v):
        """Turn string codes into numbers"""
        
        if v == 'Pop. < 500':
            return 0
        else:
            return v
            
    def parse_geoid(self, row):
        from geoid.census import County, Zcta, Place, Sldl, Sldu, Cdcurr, State
        from geoid.civick import GVid
      
        if row.geotype == 'ZCTA':
             return Zcta.parse(row.geoid.zfill(5)).convert(GVid)
             
        elif row.geotype == 'COUNTIES':
             return County.parse(row.geoid.zfill(5)).convert(GVid)
             
        elif row.geotype == 'CITIES':
             return Place.parse(row.geoid.zfill(7)).convert(GVid)
             
        elif row.geotype == 'CONGRESS':
             return Cdcurr.parse(row.geoid.zfill(4)).convert(GVid)
             
        elif row.geotype == 'SENATE':
             return Sldu.parse(row.geoid.replace('SS','').zfill(5)).convert(GVid)
             
        elif row.geotype == 'ASSEMBLY':
             return Sldl.parse(row.geoid.replace('SA','').zfill(5)).convert(GVid)
             
        elif row.geotype == 'STATE':
            return State.parse('06').convert(GVid)
             
   
        return None
        
            
    def meta_make_schema(self):
        
        variables = self.partition(table='variables')
        
        for row in variables:
            
            t = self.new_table(name=row.name, description="{}: {}".format(row.label, row.responselabel),
                                summary=row.description)

            for name, dtype, transform, desc in headers:
                c = t.add_column(name, datatype=dtype.__name__, description = desc, transform = transform)
                c.transform = transform
            
        self.commit()
        
        from ambry.orm import File
        bsf = self.build_source_files.file(File.BSFILE.SCHEMA)
        bsf.objects_to_record()
        bsf.record_to_fs()
          
    def meta_add_sources(self):
        from ambry.orm.exc import NotFoundError
    
        variables = self.partition(table='variables')
        
        for row in variables:
            try:
                ds = self.source(row.name.lower())

            except NotFoundError:
                
                ds = self._dataset.new_source(row.name.lower(), 
                    reftype='generator',ref='GenerateDataRows',
                    header_lines = [0],
                    dest_table_name = row.name.lower()
                )
            self.commit()

        self.build_source_files.sources.sync_out()
        
        
    def meta_add_gvid(self):
        """Add the gvid to the schema"""
        
        for t in self.tables:
            
            t.add_column('gvid', datatype='civick.GVid', description='GVid version of geoid', 
                         transform='^parse_geoid')
                         
        self.commit()
        
        from ambry.orm import File
        bsf = self.build_source_files.file(File.BSFILE.SCHEMA)
        bsf.objects_to_record()
        bsf.record_to_fs()
            
        
        
        
