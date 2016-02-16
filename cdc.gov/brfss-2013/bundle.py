# -*- coding: utf-8 -*-
import ambry.bundle


class Bundle(ambry.bundle.Bundle):
    
    
    def illegal_to_none(self, v):
        """ Converts '4 7' value from hlthcvrg field, on row 127231, to None. """

        try:
            return inv(v)
        except:
            return None

            
    def meta_source_schema(self):
        """Read the spec from the HTML file, and bergest it with the descriptions
        from the codebook.txt file. 

        Does *not* use the converted SPSS label file

        """
        from ambry.build import meta_source_schema, get_specs
        
        specs = get_specs(self)
    
        meta_source_schema(self, self)
    