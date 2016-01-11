# -*- coding: utf-8 -*-
import ambry.bundle


class FixEnt11(object):
    """ The Entities 11 file is malformed. It has commas in the name fiel
    but no quotes, so readers see the line as having too many columns. """
    
    def __init__(self, bundle, source, url):
        self._bundle = bundle
        self._source = source
        self._url = url
        

        
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
                head = row[:header_len-1]
                tail = [str(e) for e in row[header_len-1:] ]
                row =  head + [','.join(tail) ]
            
            yield row
    
class Bundle(ambry.bundle.Bundle):
    pass

