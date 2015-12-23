# -*- coding: utf-8 -*-
import ambry.bundle
from ambry.etl import RowGenerator

class GenerateVars(RowGenerator):
    
    def __iter__(self):
        import requests
        
        
        api_source = self._bundle.source('api')
        
        self._bundle.log("!!!! {}".format(self._source.name))
        
        def make_url(f):
            return "{}/{}".format(api_source.url, f)

        headers = {'Ocp-Apim-Subscription-Key': api_source.account.secret}

        url = make_url('metadata')

        self._bundle.log(url)

        r = requests.get(url, headers=headers)

        r.raise_for_status()

        from operator import itemgetter
        ig = None
        
        for i, row in enumerate(r.json()):
            if not ig: # Ensure that every row has values in the same order
                header = row.keys()
                yield header
                ig = itemgetter(*header)
                
            yield ig(row)
            
class Bundle(ambry.bundle.Bundle):
    
    def test_api(self):
        import requests
        
        s = self.source('api')
        print s.url
        print s.account.secret
        
        def make_url(f):
            return "{}/{}".format(s.url, f)

        headers = {'Ocp-Apim-Subscription-Key': s.account.secret}

        url = make_url('metadata')

        self.log(url)

        r = requests.get(url, headers=headers)

        r.raise_for_status()

        import json
        print json.dumps(r.json(), indent = 4)
        

