# -*- coding: utf-8 -*-
import ambry.bundle


class Bundle(ambry.bundle.Bundle):
    
    def na_is_null(self,v):
        
        if v == 'NA':
            return None
            
        return v
        
        
    def add_state(self,v):
        
        return 'CA'
        
    def augment_schema(self):
        
        dd = { e.variable_name.lower().strip() :e.definition for e in self.partition(table='dictionary') }
        
        for c in self.table('hdi').columns:
            if c.name in dd:
                c.description = dd.get(c.name)
            else:
                self.log("No description for '{}'".format(c.name))
            
            
        self.commit()
        
        self.build_source_files.schema.objects_to_record()
        
        self.commit()
        
        

