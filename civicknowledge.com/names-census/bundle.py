# -*- coding: utf-8 -*-
import ambry.bundle
  

class Bundle(ambry.bundle.Bundle):
    
    
    def make_dict(self):
        """An example of how to create a dict mapping from a bundle"""
        from operator import itemgetter
        
        p =  self.partition(table="counties")

        x = dict( [row.row for row  in p.select( headers=('gvid', 'mid_name')) ])
        print x