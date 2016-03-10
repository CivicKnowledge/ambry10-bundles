# -*- coding: utf-8 -*-
import ambry.bundle


class Bundle(ambry.bundle.Bundle):
    pass
    
    def dump_dict(self):
        
        rows = []
        
        for row in self.partition(table='codes'):
            rows.append(
                [row.ck_numeric_code,
                row.text_code, 
                row.census_table_code,
                row.hci_race_eth_name,
                row.description])



