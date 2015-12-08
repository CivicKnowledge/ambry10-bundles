# -*- coding: utf-8 -*-
import ambry.bundle


class Bundle(ambry.bundle.Bundle):
    
    RSE_MAX = 100 # Maximum Relative std error
    
    def catch_dbz(self, v):
        """On row 96767 of the Alameda Neighbohoor CHange file there is a
        very large value that looks like a divide-by-nearly-zero error"""

        return min(v, self.RSE_MAX)
        
       
