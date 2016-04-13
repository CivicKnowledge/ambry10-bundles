# -*- coding: utf-8 -*-
import ambry.bundle


class Bundle(ambry.bundle.Bundle):
    pass


    def county_gvid(self, row):
        
        from geoid.civick import County
        
        return County(6, row.fips_code)