# -*- coding: utf-8 -*-
import ambry.bundle


class Bundle(ambry.bundle.Bundle):

    def meta_source_schema(self):
        """Read the spec from the HTML file, and bergest it with the descriptions
        from the codebook.txt file. 

        Does *not* use the converted SPSS label file

        """
        
        
        
        b = self.library.bundle(self.bundle('code_bundle').ref)
        m = b.import_lib()
        
        specs = m.get_specs(self)
    
        m.meta_source_schema(self, specs)