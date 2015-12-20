# -*- coding: utf-8 -*-
import ambry.bundle


class Bundle(ambry.bundle.Bundle):
    
    
    
    def init(self):
        from geoid.censusnames import geo_names
        from geoid.civick import GVid, County, State
        
        self.county_map = {}
        
        for (state, county), name in geo_names.items():
            if state == 6 and county != 0:
                short_name = name.replace(' County, California','')
                self.county_map[short_name] = County(state, county)
                
        self.county_map['STATEWIDE'] = State(6)
        
        
    def edit_pipeline(self, pl):
        """Alter the pipeline to add the final routine and the custom partition selector"""
        
        from ambry.etl import SelectPartition

        pl.select_partition = [SelectPartition('bundle.select_partition(source,row)')]
        
        return pl
        
    def select_partition(self, source, row):
        
        d = dict(table=source.dest_table.name,segment=source.sequence_id)
        
        if row.county == 'STATEWIDE':
            d['grain'] = 'state'
        else:
             d['grain'] = 'county'
             
        return d
        
    
    def extract_county(self, row):
        
        return  self.county_map.get(row.county)

