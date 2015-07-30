import ambry.bundle 


class Bundle(ambry.bundle.Bundle):
    
    def mkschema(self):
        from ambry.orm.file import File
        
        t = self.dataset.new_source_table('geoschema')
        
        for s in self.sources:

            p = self.library.partition(s.ref)
            for row in p.stream(as_dict = True):
                
                if  row['year'] != 2009:
                    continue
                    
                if row['name'].lower().strip() == 'blank':
                    continue
               
                #self.logger.info(row['name'])
                t.add_column( source_header = row['name'], position = row['seq'],
                        datatype = str,
                        start = row['start'], width = row['width'], 
                        description = row['description'])
              
        self.commit() 
        
        self.build_source_files.file(File.BSFILE.SOURCESCHEMA).objects_to_record()
        self.do_sync(force='rtf')
                
                
            