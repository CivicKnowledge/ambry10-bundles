# -*- coding: utf-8 -*-
import ambry.bundle
  

class Bundle(ambry.bundle.Bundle):
    
    
    def foo(self):
        from operator import itemgetter
        
        p =  self.partition(table="counties")
        ig = itemgetter(*p.headers)
        
        #with p.reader as r:   
        #    print { row['geoid']:row['name'] for row in r}
         
        x = dict( [row.row for row  in p.select( headers=('gvid', 'mid_name')) ])
        print x