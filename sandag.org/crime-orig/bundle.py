# -*- coding: utf-8 -*-
import ambry.bundle


class Bundle(ambry.bundle.Bundle):
    pass



    def geocode(self):
        from ambry.util.geocoders import DstkGeocoder
        
        
        
        def address_gen():
            """Produce blocks addresses that are randomized within the 100 block, 
            if possible, and return the original address if it isn't """
            
            from random import randint
            from address_parser import Parser
            
            parser = Parser()
            
            p = self.partition(table='crimeb')
            
            for row in p:
                
                if not row.block_address:
                    continue

                ba = str(row.block_address).replace('EL CAM', 'El Camino')

                ps = parser.parse(ba)

                if ps and ps.number.number and ps.number.number > 0:
                    ps.number.number = \
                        int( round(ps.number.number, -2)) + \
                        randint(0,100)

                    street_num = str(ps)
                else:
                    street_num = ba.replace('BLOCK', '')
                    

                city = row.city
                
                if not row.city and row.agency != 'SHERRIF':
                    city = row.agency
                
                if not city:
                    city = ''
                
                zipcode = ', {}'.format(row.zipcode) if row.zipcode else ''
                
                address = '{} {} CA{}'.format(street_num, city, zipcode)
                
                yield (address,row)
                
                 
        dstk_gc = DstkGeocoder(self.library.services['dstk'], address_gen())
                      
        for output in dstk_gc.geocode():
            input_address, result, row = output
            
            print input_address, result
            
            
            
