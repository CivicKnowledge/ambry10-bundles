# -*- coding: utf-8 -*-
import ambry.bundle

from ambry.util import memoize
from ambry.etl import Pipe, RowProxy


class CountNonNullRows(Pipe):
    """Count runs of non empty rows, to detect the break before a state or county name"""

    def process_header(self, headers):
        self.row_proxy = RowProxy(headers)

        self.bundle.non_null_row_count = 0 

        return headers

    def process_body(self, row):

        if not bool(self.row_proxy.set_row(row).state_county_city.strip()):
            self.bundle.non_null_row_count = 0
        else:
            self.bundle.non_null_row_count += 1
            
        return row

class Bundle(ambry.bundle.Bundle):
    pass

    def init(self):
        self.non_null_row_count = 0 
        self.last_county = None
        self.city_name = None

    @memoize
    def county_map(self):
        return { row.name.lower():row.gvid for row in self.dep('counties') if row.statefp == 6}
      
    @memoize
    def place_map(self):
        return { row.name.lower():row.gvid for row in self.dep('places') if row.statefp == 6}
      
    def to_float(self, v):
        return float(v)
      
    def geotype(self, row):
        
        try:
            return row.gvid.geoid.level
        except:
            return None
    
    def geoid(self, row):
        
        try:
            return row.gvid.acs
        except:
            return None
    
    
    def name_to_gvid(self, row):
        from geoid.civick import GVid
    
        v = row.state_county_city.lower()
        self.city_name = None
        
        if v == 'california':
            from  geoid.civick import State
            return State(6)
        elif v == 'balance of county':
            return None
        elif self.non_null_row_count == 1:
            self.last_county = row.state_county_city
            return GVid.parse(self.county_map()[v])
            
        else:
            self.city_name = row.state_county_city
            return GVid.parse(self.place_map().get(v))
    
      
        
    
        
  