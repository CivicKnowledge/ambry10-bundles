# -*- coding: utf-8 -*-
# Ambry Bundle Library File
# Use this file for code that may be imported into other bundles

def make_request(bundle, path):
    import requests

    import os.path
    
    headers = {
     'X-HIW-API-Key': bundle.library.account('healthindicators.gov').secret,
     'Accept': 'application/json'
    }

    root_url = bundle.source('api').url

    url = root_url.strip('/') + '/' + path.strip('/')

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    return r.json()
    
class GenerateHIWDataRecords(object):
    """Generate data for a path in the HIW API"""
    
    columns = None
    
    path = None
    
    def __init__(self, bundle, source, args={}):
        self._source = source
        self._bundle = bundle
        self._args = args
        
    def __iter__(self):
        from operator import itemgetter
        
        ig = itemgetter(*self.columns)
        
        for page in range(1,20):
            r = make_request(self._bundle, self.path.format(page=page, **self._args))
            
            assert r['Status'] == 'Success'
            
            if r['DataLength'] == 0:
                break
            
            if page == 1:
                yield self.columns
        
            for i, e in enumerate(r['Data']):
                
                if i > 500 and self._bundle.limited_run:
                    break
                
                yield ig(e)