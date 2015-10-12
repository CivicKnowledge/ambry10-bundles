import ambry.bundle 
from ambry.etl import Pipe
from ambry.util import memoize

class AugmentTableMeta(Pipe):

    def __init__(self, bundle, source):
        super(AugmentTableMeta, self).__init__(bundle, source)

    def __iter__(self):

        pass

class Bundle(ambry.bundle.Bundle):
    
    
    @staticmethod
    def tc_caster(v):
        # Value has  an int, or "<int> CELL" or "<int> CELLS"

        try:
            return int(v)
        except ValueError:
            return int(v.split()[0])

    @property
    @memoize
    def table_spans(self):

        p = self.partition('census.gov-acs_geofile-schemas-2009e-table_sequence')  
        
        table_spans = {}
        
        for row in p.stream(as_dict = True):
            if bool(row['start_position']) and bool(row['start_position'].strip()):
                sp =  int(float(row['start_position']))

                # For the entries that have the word ' cell ' in them
                length = int(row['total_cells_in_table'].split()[0])
                    
                    
                table_spans[(row['table_id'], int(row['year']), int(row['release']) )] = (sp, length)
                
        return  table_spans
        
    def test_augment(self):
        
        self.log("Getting Spans")
        spans = self.table_spans
        
        p = self.partition('census.gov-acs_geofile-schemas-2009e-table_meta')  
        
        errors = set()
        
        for row in p.stream(as_dict = True):
            try:
                table_span = spans[(row['table_id'], int(row['year']), int(row['release']))]   
                
            except KeyError:
                print (row['table_id'], int(row['year']), int(row['release']))
                errors.add((int(row['year']), int(row['release'])))
                
        print errors
        
        
    def column_maps(self):
        from itertools import groupby
        from operator import attrgetter
        from collections import OrderedDict
        
        keyfunc = attrgetter('dest_table')
        for dest_table, sources in groupby(sorted(self.sources, key=keyfunc), keyfunc):
        
            sources = list(sources)
        
            n_sources = len(sources)
        
            columns = []

            for c in dest_table.columns:
                if c.name not in columns:
                    columns.append(c.name)
                
            for source in sources:
                for c in source.source_table.columns:
                    if c.name not in columns:
                        columns.append(c.name)
               
               
            columns = OrderedDict( (c,[''] * n_sources ) for c in columns )
            
            for i,source in enumerate(sources):
                source_cols = [ c.name for c in source.source_table.columns]
                
                for c_name, row in columns.items():
                    if c_name in source_cols:
                        row[i] = c_name
             
            fn = "colmap_{}.csv".format(dest_table.name)        
            
            with self.source_fs.open(fn,'wb') as f:
                import csv
                w = csv.writer(f)

                # FIXME This should not produce entries for non-table sources. 
                w.writerow([dest_table.name]+
                           [s.source_table.name for s in sources if s.dest_table ])

                for col_name, cols in columns.items():
                    w.writerow([col_name]+cols)
                    
            
    def load_column_maps(self):
            
        dest_tables = set([ s.dest_table_name for s in self.sources 
                        if s.dest_table ])
        
        with self.source_fs.open('colmap.csv', 'wb') as cmf:
            import csv
            w = csv.writer(cmf)
            
            w.writerow(('table','source','dest'))
        
            for dest_table_name in dest_tables:
                fn = "colmap_{}.csv".format(dest_table_name)  
            
                if not self.source_fs.exists(fn):
                    continue
                
                with self.source_fs.open(fn,'rb') as f:
                    import csv
                    r = csv.reader(f)
                
                    source_tables = next(r)
                    dtn = source_tables.pop(0)
                    assert dtn == dest_table_name
                
                    for row in r:
                        dest_col = row.pop(0)
                        for source, source_col in zip(source_tables, row):
                    
                            if source_col and dest_col != source_col:
                                w.writerow((source, source_col, dest_col))
 
                    
                    
                
                    
                
                
            
