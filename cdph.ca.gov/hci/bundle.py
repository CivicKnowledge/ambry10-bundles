# -*- coding: utf-8 -*-
import ambry.bundle



class Bundle(ambry.bundle.Bundle):
    
    def edit_pipeline(self, pl):
        
        from ambry.etl import SelectPartition
        
    
        pl.final = [self.edit_descriptions]
        pl.select_partition = [SelectPartition(
        'dict(table=source.dest_table.name,'
        'segment=source.sequence_id,'
        'grain=row.geotype.lower())'
        )]
        return pl
  
        
    def na_is_none(self, v):
        
        if v == 'NA':
            return None
        else:
            return v
    
    def catch_dbz(self, row,  v):
        """On row 96767 of the Alameda Neighbohoor CHange file there is a
        very large value that looks like a divide-by-nearly-zero error"""

        try:
            if row.difference == 0:
                return None
        except KeyError:
            pass
            
        if v == 'NA':
            return None
        else:
            return v
        
    def version_date(self, v):
        """Deal with wacky version dates, like: 14APR13:10:31:45"""
        
        from dateutil import parser
        from xlrd.xldate import  xldate_as_datetime
          
        try:
            v =  parser.parse("{}-{}-{}".format(v[0:2],v[2:5],v[5:7])).date()
        except:
            v = xldate_as_datetime(v, 0).date()
            
        return v  
        
    def extract_desc(self, v, row, accumulator):
        """Extract the table description from the ind_definition field"""
        
        # These value are mostly the same for every row, I think. 
        accumulator[row.ind_id] = row.ind_definition
        return v
        
    def edit_descriptions(self, pl):
        """Extract the values added to the accumulator by extract_desc and add 
        them to the table description"""
         
        from ambry.etl import CastColumns
        
        caster = pl[CastColumns]
        
        table = caster.source.dest_table
        
        table.description = ','.join( u'HCI Indicator {}: {}'.format(k, v) 
                     for k, v in caster.accumulator.items())
                     
    def extract_geoid(self, v, row):
        
        from geoid.census import Place, County, State, Cosub, Tract, Zcta
        from geoid.civick import GVid
        
        CA_STATE = 6
        
        if row.geotype == 'PL':
            r = Place(CA_STATE, int(row.geotypevalue)).convert(GVid)
        elif row.geotype == 'CO':
            gt = row.geotypevalue
            assert int(gt[0:2]) == CA_STATE
            r = County(CA_STATE, int(gt[2:])).convert(GVid)
        elif row.geotype == 'CA':
            r = State(CA_STATE).convert(GVid)
        elif row.geotype == 'CD':
            r = Cosub.parse(row.geotypevalue).convert(GVid)
        elif row.geotype == 'CT':
            try:
                r = Tract.parse(row.geotypevalue).convert(GVid)
            except ValueError:
                r = Tract.parse('06'+row.geotypevalue).convert(GVid)
        elif row.geotype == 'ZC':
            r = Zcta.parse(row.geotypevalue).convert(GVid)
        elif row.geotype == 'NA': # Sub-state region, not a census area
            r = None
        elif row.geotype == 'RE': # Sub-state region, not a census area
            r = None
        else:
            self.error("Unknown geotype {} in row {}".format(row.geotype, row))
            r = None
    
        return r
        
    def meta_add_gvid(self):
        """A meta phase routine to add the gvid columns to every table"""
        
        for t in self.tables:
            t.add_column('gvid',datatype='census.GVid', 
                description='GVid version of the geotype and geotypeval',
                transform='^extract_geoid')
                
        self.commit()
        
        
        
        
        
                     
                     