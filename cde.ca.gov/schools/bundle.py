# -*- coding: utf-8 -*-
import ambry.bundle
from ambry.util import memoize

class Bundle(ambry.bundle.Bundle):
    
    @memoize
    def county_map(self):
        
        return { row.sos_code:row.copy() for row in self.dep('county_codes') }
        
        
    def sos_code(self, row):
        try:
            return int(row.cd_code[:2]) # In district table
        except KeyError:
            return int(row.cdscode[:2]) # In school table

    def fips_code(self, row):
        return self.county_map()[row.county_sos].fips_code
        
    def gvid_code(self, row):
        return self.county_map()[row.county_sos].gvid
