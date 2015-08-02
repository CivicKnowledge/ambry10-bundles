import ambry.bundle 


class Bundle(ambry.bundle.Bundle):
    
    def mkschema(self):
        """Create the 2009 geofile schema from the configuration in the upstream bundle. """
        from ambry.orm.file import File
   
        t = self.dataset.new_table('geoschema')
        st = self.dataset.new_source_table('geoschema')
        
        s = self.source('geofile_schema')
 
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
        
        year = 2009

        for span in [1,3]:
            source_name = 'dnlpage{}{}'.format(year,span)
            source = self.source(source_name)
                
            entries = scrape_urls_from_web_page(source.url)['sources']
            s = self.session
            for k,v in entries.items():
            
                d = {
                    'name': k.lower()+"_{}{}".format(year,span),
                    'source_table_name': 'geoschema',
                    'dest_table_name': 'geoschema',
                    'filetype': 'fixed',
                    'file': 'g2009.*\.txt',
                    'encoding': 'latin1',
                    'time': year, 
                    'grain': span, 
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

  
    def add_5yr_sources(self):
        from ambry.orm import DataSource, File
        from ambry.util import scrape_urls_from_web_page
        import os
        
        year = 2009
        span = 5

        source_name = 'dnlpage{}{}'.format(year,span)
        source = self.source(source_name)

        self.log("Loading from {}".format(source.url))

        state_entries = scrape_urls_from_web_page(source.url)['links']
        s = self.session
        for state_name, parts in state_entries.items():
            if state_name.endswith('/'):
                state_name = state_name.replace('/','')
                url = parts['url']
                
                for suffix, size in (('All_Geographies_Not_Tracts_Block_Groups', 'L'), 
                                     ('Tracts_Block_Groups_Only', 'S')):
                    gurl = os.path.join(url, suffix)
                    table_urls = scrape_urls_from_web_page(gurl)['sources']
                    for k, v in table_urls.items():
                        if k.startswith('g20095'):
                            self.log('Found: {}'.format(k))
                            d = {
                                'name': k+size,
                                'source_table_name': 'geoschema',
                                'dest_table_name': 'geoschema',
                                'filetype': 'fixed',
                                'file': 'g2009.*\.txt',
                                'encoding': 'latin1',
                                'time': year, 
                                'grain': span, 
                                'url': v['url']
                            }
            
                            ds = self._dataset.source_file(d['name'])
                            if ds:
                                ds.update(**d)
                            else:
                                ds = DataSource(**d)
                                ds.d_vid = self.dataset.vid

                            s.merge(ds)
                            
                            
                
        
        
            