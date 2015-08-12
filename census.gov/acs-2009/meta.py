import ambry.bundle 
from ambry.util import memoize

from ambry.etl.rowgen import SourceRowGen

class TableGenerator(SourceRowGen):
    

    def _generate_sources(self):
        """Create source entry information, one for each table+state"""
        import os
        from ambry.orm.source import DataSource
    
        url_root = self.source.url

        ts = self.bundle.dep('table_sequence')

        for stusab, state_id, state_name in self.bundle.states:
            
            for row in ts.stream(as_dict = True):

                if (row['year'] == int(self.metadata.about.time) and
                    row['release'] == int(self.metadata.build.release) and
                    bool(row['start_position'])):
                    
                    start = int(float(row['start_position']))
                    length = int(row['total_cells_in_table'].split()[0])

                    slc = "0:6,{}:{}".format(start, start+length)
        
                    file = "e2009{}{}{:04d}000.txt".format(row['release'],stusab.lower(),row['sequence_number'])

                    url = self.url_template.format(root=url_root, state_name=state_name)
                
                    source = DataSource(name='{}_{}'.format(state_id, row['table_id']), 
                                    filetype = 'csv', url = url, source_table_name = row['table_id'],
                                    file = file, time=self.source.time, space = stusab, segment = slc)
                
                    yield state_id, state_name, source
                    
    def __iter__(self):
        
        from ambry.etl.pipeline import Slice
        
        for state_id, state_name, source in self._generate_sources():
            
            sp = self.bundle.source_pipe(source)
            self.bundle.log("Iterating over {}, {},  {}".format(source.source_table_name, source.file, source.segment))
            
            for row in sp:
                yield row
            
class SmallGeoTableGenerator(TableGenerator):
    """A row generator for the small geographies"""
    url_template = "{root}/{state_name}_Tracts_Block_Groups_Only.zip"

class LargeGeoTableGenerator(TableGenerator):
    """A row generator for the large geographies"""
    url_template = "{root}/{state_name}_All_Geographies_Not_Tracts_Block_Groups.zip"

class Bundle(ambry.bundle.Bundle):
    
    @property
    @memoize
    def states(self):
        """Return tuples of states, which can be used to make maps and lists"""
        ts = self.dep('states')
        
        for row in ts.stream(as_dict = True):
            if row['component'] == 0:
                yield  (row['stusab'], row['state'], row['name'] )

    def xtables(self, release):
        from collections import defaultdict
        from ambry.orm.source import DataSource
        from ambry.util import init_log_rate
        
        def prt(x):
            print x
        
        lr = init_log_rate(prt)
        
        root_source = self.source('root_'+str(release))
        url_root = root_source.url
        
        ts = self.dep('table_sequence')

        states = list(self.states)

        tables = defaultdict(list)
        
        for row in ts.stream(as_dict = True):

            if (row['year'] != int(self.metadata.about.time) or row['release'] != int(self.metadata.build.release)):
                continue

                start = int(float(row['start_position']))
                length = int(row['total_cells_in_table'].split()[0])
                slc = "0:6,{}:{}".format(start, start+length)
                

                for stusab, state_id, state_name in states:

                    file = "e2009{}{}{:04d}000.txt".format(row['release'],stusab.lower(),row['sequence_number'])

                    for url_template in ["{root}/{state_name}_Tracts_Block_Groups_Only.zip",
                                         "{root}/{state_name}_All_Geographies_Not_Tracts_Block_Groups.zip" ]:

                        url = url_template.format(root=url_root, state_name=state_name)
                
                        source = DataSource(name='{}_{}'.format(state_id, row['table_id']), 
                                        filetype = 'csv', url = url, source_table_name = row['table_id'],
                                        file = file, time=root_source.time, grain = release, space = stusab, segment = slc)
                
                        
                        tables[row['table_id']].append((source, state_id, state_name))
                        lr()
                    
        return tables      

    def tables(self):
        from collections import defaultdict
        from ambry.orm.source import DataSource
        from ambry.util import init_log_rate
        
        def prt(x):
            print x
        
        lr = init_log_rate(prt)

        ts = self.dep('table_meta')

        states = list(self.states)

        tables = defaultdict(list)

        year = self.metadata.about.time
        release = 5 # self.metadata.build.release

        for row in ts.stream(as_dict = True):

            if (int(row['year']) != int(year) or int(row['release']) != int(release)):
                continue
                
            tables[row['table_id']] = row
                

        print len(tables)



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
                    
    def foo_meta(self):
  
        print self.tables(5).keys()


    def foo(self):

        ts = self.dep('table_sequence')

        for row in ts.stream(as_dict = True):
            if row['year'] != 2009 or not bool(row['start_position']):
                continue 

            start = int(float(row['start_position']))
            length = int(row['total_cells_in_table'].split()[0])
        
            slice = "0:6,{}:{}".format(start, start+length)
        
            print row
