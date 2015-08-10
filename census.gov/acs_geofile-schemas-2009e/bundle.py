import ambry.bundle 
from ambry.etl import SourcePipe
from ambry.util import memoize

class AugmentTableMeta(SourcePipe):

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