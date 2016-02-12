# -*- coding: utf-8 -*-
import ambry.bundle

def dot_to_none(v):
    """ Convert dots to NULLs"""
    if isinstance(v, basestring) and v.strip() == '.':
        return None
    return v


def illegal_to_none(v):
    """ Converts '9 8   ' value from mrace field, on row 106343, to None. """
    
    try:
        return inv(v)
    except:
        return None
    
    if isinstance(v, basestring) and v == '9 8   ':
        return None
    return v


class Bundle(ambry.bundle.Bundle):
    
    def meta_source_schema(self):
        
        from ambry.build import meta_source_schema

        meta_source_schema(self)
        
    def add_descriptions(self):
        """Copy variable descriptions from the main BRFSS bundle"""
        
        b = self.library.dep('cdc.gov-brfss-2014')
        
        print b.identity

        descriptions = { c.name:c.description for c in b.table('brfss').columns}
        
        for c in self.table('brfss_county').columns:
            
            c.description = descriptions.get(c.name)
            
        b.build_source_files.schema.objects_to_records()
        b.commit()
        
        