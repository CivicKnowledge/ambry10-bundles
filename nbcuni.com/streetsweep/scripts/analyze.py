
from ambry_sources.mpf import MPRowsFile
from address_parser import Parser
import cPickle as pickle
import csv

import dateutil.parser


from address_parser import Parser
parser = Parser()

with open('sweeps.pkl', 'rb') as f:
    rows = pickle.load(f)
    
# Year and months that the city claims the GPS system was not working
claimed_exclusions = "2015-01 2015-02 2015-03 2015-04 2014-11 2014-10 2014-09 2014-08 2014-07".split()
    
with open('ticket-not-swept-dates.csv', 'w') as f:
    w = csv.writer(f)
    w.writerow(('date','number','street','tickets', 'address', 'claimed_no_gps'))
    
    for (date, street, swept, ticketed, claimed_no_gps) in rows:
        
        key = (date, street)
    
        ym = date[:7] # Just the year and month
    
        if ticketed and not swept:
            ps = parser.parse(street)
            row = (date, ps.number.number, ps.road.name+' '+ps.road.suffix, 
            ticketed, 
            "{} {} {}, San Diego, CA"
                .format(ps.number.number,ps.road.name,ps.road.suffix),
            claimed_no_gps                       
            )
            
            w.writerow(row)

from collections import defaultdict
counts = defaultdict(int)
      
for (date, street, swept, ticketed)  in rows:

    if ticketed and not swept:
        ps = parser.parse(street)
        full_address = "{} {} {}, San Diego, CA".format(ps.number.number,
                                         ps.road.name,ps.road.suffix)
        
        counts[full_address] += ticketed
        
            
with open('ticket-not-swept-counts.csv', 'w') as f:
    w = csv.writer(f)
    w.writerow(('address', 'count'))
    
    for (full_address, count ) in counts.items():
        w.writerow((full_address, count))
        
        

        

            

