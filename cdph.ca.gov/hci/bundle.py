# -*- coding: utf-8 -*-
import ambry.bundle


class Bundle(ambry.bundle.Bundle):
    
    
    def dump_headers(self):
        
        h = []
        
        for t in self.dataset.source_tables:    
            h.append( [t.name]+[c.source_header for c in t.columns])
            
        
        import json
        print json.dumps(h)
            
        
        
        
        
    
    def cluster(self):
        
        from ambry.etl import ClusterHeaders
        
        ch = ClusterHeaders(self)
        
        ch.cluster()

