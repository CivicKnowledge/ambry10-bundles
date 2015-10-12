# -*- coding: utf-8 -*-
import ambry.bundle
  

class Bundle(ambry.bundle.Bundle):
    
    
    def foo(self):
        from operator import itemgetter
        
        p =  self.partition(table="counties")

        x = dict( [row.row for row  in p.select( headers=('gvid', 'mid_name')) ])
        print x