import ambry.bundle 


class Bundle(ambry.bundle.Bundle):
    
    def mkschema(self):
        from ambry.orm.file import File
   
        t = self.dataset.new_table('geoschema')
        st = self.dataset.new_source_table('geoschema')
        
        for s in self.sources:
            print s
            p = self.library.partition(s.ref)
            for row in p.stream(as_dict = True):

                if  row['year'] != 2009:
                    continue
                    
                if row['name'].lower().strip() == 'blank':
                    continue
               
                self.logger.info(row['name'])
                
                
                t.add_column(row['name'].lower().strip(), 
                        datatype = 'varchar',
                        description = row['description'])
                
                st.add_column( source_header = row['name'].lower().strip(), position = row['seq'],
                        datatype = str,
                        start = row['start'], width = row['width'], 
                        description = row['description'])

        self.commit() 
        
        self.build_source_files.file(File.BSFILE.SOURCESCHEMA).objects_to_record()
        self.build_source_files.file(File.BSFILE.SCHEMA).objects_to_record()
        self.do_sync(force='rtf')
        
    def add_sources(self):
        from ambry.orm import DataSource, File
        from ambry.util import scrape_urls_from_web_page
                
        entries = scrape_urls_from_web_page('http://www2.census.gov/acs2009_1yr/summaryfile/Entire_States/')['sources']
        s = self.session
        for k,v in entries.items():
            
            d = {
                'name': k.lower(),
                'source_table_name': 'geofile',
                'dest_table_name': 'geofile',
                'url': v['url']
            }
            
            ds = self._dataset.source_file(d['name'])
            if ds:
                ds.update(**d)
            else:
                ds = DataSource(**d)
                ds.d_vid = self.dataset.vid

            s.merge(ds)
            
        s.commit()
            
        self.build_source_files.file(File.BSFILE.SOURCES).objects_to_record()
        self.do_sync(force='rtf')
        
            