# -*- coding: utf-8 -*-
import ambry.bundle
from ambry.util import memoize

class FixEnt11(object):
    """ The Entities 11 file is malformed. It has commas in the name fiel
    but no quotes, so readers see the line as having too many columns. """
    
    def __init__(self, bundle, source, url):
        
        self._bundle = bundle
        self._source = source
        self._url = source.ref
        
        
    def __iter__(self):
        
        import unicodecsv as csv
        from contextlib import closing
        from ambry_sources import get_source
        from ambry.bundle.process import call_interval
        
        @call_interval(5)
        def progress(read_len, total_len):
            self._bundle.log('Downloading {}: {}'.format(self._source.url, total_len))

        spec = self._source.spec
        spec.urltype = 'zip'

        s = get_source(spec, self._bundle.library.download_cache,
                    account_accessor=self._bundle.library.account_accessor, callback=progress)

        encoding = self._source.spec.encoding or 'utf8'

        header = None
        header_len = None

        for i, row in enumerate(s):
            
            if i == 0:
                header = row
                header_len = len(row)
            
            if len(row) > header_len:
                head = list(row)[:header_len-1]
                tail = [str(e) for e in row[header_len-1:] ]
                row =  head + [','.join(tail) ]
            
            yield row
    
class Bundle(ambry.bundle.Bundle):
    
    @property
    @memoize
    def county_map(self):
        return { int(row.sos_code):dict(row) for row in self.dep('county_codes') }


    def star_is_not_a_number(self, v):
        if v == '*' or v == '**':
            return None
        else:
            return v
            
    def make_cds(self, row):
        
        return "{:02d}{:05d}{:07d}".format(int(row.co), int(row.dist), int(row.schl))

            

    grain_map={
        None: 'unknown',
        1: 'school',
        2: 'district',
        3: 'county',
        4: 'state'
    }

    def select_partition(self, source, row):
        
        from ambry.identity import PartialPartitionName
        
        return PartialPartitionName(table=source.dest_table_name, 
                                    time=source.time, 
                                    grain=self.grain_map[row.level_number])
        