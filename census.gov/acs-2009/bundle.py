 # -*- coding: utf-8 -*-
import ambry.bundle 
from ambry.util import memoize

from ambry.etl import SourcePipe

raise Exception("Convert this bundle's methods to pipes that create the data sets"
" for tables & slices in one phase, then used those tables in the build phase. ")

class Bundle(ambry.bundle.Bundle):

    _states = None

    def init(self):
        
        self.url_root = self.source('root_5').url
        
        self.small_url_template = "{root}/{state_name}_Tracts_Block_Groups_Only.zip"
        self.large_url_template = "{root}/{state_name}_All_Geographies_Not_Tracts_Block_Groups.zip"
        
        self.year = self.metadata.about.time
        self.release = self.metadata.build.release
        
        

    @property
    @memoize
    def states(self):
        """Return tuples of states, which can be used to make maps and lists"""
        
        if not self._states:
        
            self._states = []
        
            ts = self.dep('states')
        
            for row in ts.stream(as_dict = True):
                if row['component'] == '00':
                    self._states.append((row['stusab'], row['state'], row['name'] ))
                    
        p =  self.partition(table="counties")

        x = dict( [row.row for row  in p.select( headers=('gvid', 'mid_name')) ])
        print x
                    
        return self._states

    def tables_list(self,  add_columns = True):
        from collections import defaultdict
        from ambry.orm.source import DataSource
        from ambry.util import init_log_rate
        
        def prt(v): print v
        
        lr = init_log_rate(prt)

        ts = self.dep('table_sequence')

        states = list(self.states)

        tables = defaultdict(lambda: dict(table=None, universe = None, columns = []))

        year = self.metadata.about.time
        release = self.metadata.build.release

        table_id = None
        seen = set()
        ignore = set()
        
        #name, universe, description, columns
        
        i = 0
        
        for row in ts.stream(as_dict = True):

            if int(row['year']) != int(year) or int(row['release']) == int(release):
                continue
            
            if row['table_id'] in ignore:
                continue

            if int(row['sequence_number'] ) > 117:
                # Not sure where the higher sequence numbers are, but they aren't in this distribution. 
                continue

            table_name = row['table_id']

            if row['start_position']:
                
                if table_name in seen:
                    ignore.add(table_name)
                    continue
                else:
                    seen.add(table_name)
                
                start = int(float(row['start_position']))
                length = int(row['total_cells_in_table'])
                slc = "2,3,5,{}:{}".format(start, start+length)
        
                tables[table_name] = dict(
                    name = row['table_id'],
                    universe=None,
                    description=row['table_title'].title(),
                    columns=[],
                    data = dict(
                        sequence = int(row['sequence_number']),
                        start=start, 
                        length=length, 
                        slice = slc
                    )
                )
                
            elif 'Universe' in row['table_title']:
                tables[table_name]['universe'] = row['table_title'].replace('Universe: ','').strip()
                
            elif add_columns:
                tables[table_name]['columns'].append(dict(
                    name=table_name+"{:03d}".format(int(row['line'])),
                    description=row['table_title'], datatype = 'integer')
                    )
                
        return tables
        
    def make_table(self,  name, universe, description, columns, data):
        
        t = self.new_table(name, description = description.title(), universe = universe.title(),
                           data = data)

        header_cols = [
            #('FILEID','File Identification',6 ),
            #('FILETYPE','File Type',6),
            ('STUSAB','State/U.S.-Abbreviation (USPS)',2 ),
            ('CHARITER','Character Iteration',3 ),
            #('SEQUENCE','Sequence Number',4 ),
            ('LOGRECNO','Logical Record Number',7 )
        ]
        
        for name, desc, size in header_cols:
            t.add_column(name, description = desc, size = size)
           
        for col in columns:
            t.add_column( **col )
        
    def create_tables(self):
        import pprint
        
        self.log("Deleteting old tables and partitions")
        self.dataset.delete_tables_partitions()
        
        self.commit()

        tables = self.tables_list()
        
        self.log("Creating {} tables".format(len(tables)))
        
        lr = self.init_log_rate(100)
        
        for i, table_id in enumerate(sorted(tables.keys())):

            d = tables[table_id]
            
            lr(table_id)
            
            self.make_table( **d )
            
        self.commit()
            
    def table_sources(self, table):
        
        from ambry.orm import TransientDataSource
        
        table_name = table.name
        start = table.data['start']
        length = table.data['length']
        sequence = table.data['sequence']
    
        sources  = []
   
        for stusab, state_id, state_name in self.states:

            slc = "2,3,5,{}:{}".format(start, start+length)

            file = "e{}{}{}{:04d}000.txt".format(self.year,self.release,stusab.lower(),sequence)

            for url_template in [self.small_url_template, self.large_url_template]:
                
                url = url_template.format(root=self.url_root, state_name=state_name).replace(' ','')
        
                sources.append(TransientDataSource(
                                # Must have id to make segments in SelectPartition
                                id = int(table.sequence_id) * 100 + int(state_id), 
                                name='{}_{}'.format(stusab, table_name), 
                                filetype = 'csv', 
                                url = url, 
                                dest_table_name = table_name,
                                file = file, 
                                time=self.year, 
                                space = stusab, 
                                segment = slc))
          
        return sources
  
    def create_jobs(self):
        
        from ambry.etl import Pipeline, PrintEvery, PrintRows, Slice, AddDestHeader
        from ambry.dbexceptions import ConfigurationError
  
        self.dataset.delete_partitions()
  
        skip_sequence = set()
  
        for table in self.dataset.tables:
            sources = self.table_sources(table)
            
            self.build(sources=sources)
                    
                
    def run_tables(self):
        from ambry.etl import Pipeline, PrintEvery, PrintRows, Slice, AddDestHeader
        from ambry.dbexceptions import ConfigurationError
  
        skip_sequence = set()
  
        for table in self.dataset.tables:
 
            if sequence in skip_sequence:
                continue
            
            for source in sources:
                
                self.log("Starting: {} {}".format(source.name, source.file))

                pl = Pipeline(bundle = self, 
                              source = [ self.source_pipe(source)],
                              body = [
                                  Slice,
                                  AddDestHeader],
                              last = [PrintRows(print_at='end')]
                )
            
                try:
                    pl.run()
                except ConfigurationError as e:
                    self.error("Failed {}".format(e))
                    skip_sequence.add(sequence)
                    break
                except Exception as e:
                    self.error("Failed {}".format(e))
                    skip_sequence.add(sequence)
                    raise
                    break
             
           

    def generate_sources(self):
        from ambry.etl.rowgen import source_pipe
        from ambry.etl.pipeline import Pipeline, Slice, PrintRows, PrintEvery
        
        for s in self.refs:
            if s.urltype == 'template':

                pl = Pipeline(bundle = self, 
                              source = [self.source_pipe(s)],
                              last = PrintEvery
                )
                

                pl.run()
                    

    


