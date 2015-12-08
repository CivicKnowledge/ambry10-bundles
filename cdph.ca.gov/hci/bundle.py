# -*- coding: utf-8 -*-
import ambry.bundle

class Bundle(ambry.bundle.Bundle):
    
    
    def catch_dbz(self, row,  v):
        """On row 96767 of the Alameda Neighbohoor CHange file there is a
        very large value that looks like a divide-by-nearly-zero error"""

        if row.difference == 0:
            return None
        else:
            return v
        
        
    def version_date(self, v):
        """Deal with wacky version dates, like: 14APR13:10:31:45"""
        
        from dateutil import parser
        from xlrd.xldate import  xldate_as_datetime
          
        try:
            v =  parser.parse("{}-{}-{}".format(v[0:2],v[2:5],v[5:7])).date()
        except:
            v = xldate_as_datetime(v, 0).date()
            
        return v  
        
    def do_row(self, row, v, accumulator):
        
        # These value are mostly the same for every row, I think. 
        accumulator[row.ind_id] = row.ind_definition
       
        return v
        
    def do_final(self, pl):
         
        from ambry.etl import CastColumns
        
        caster = pl[CastColumns]
        
        table = caster.source.dest_table
        
        table.description = ','.join( '{}: {}'.format(k, v) 
                     for k, v in caster.accumulator.items())
        
        
        
        
    def edit_pipeline(self, pl):
        
        pl.final.append(self.do_final)
        return pl