
from ambry_sources.mpf import MPRowsFile
from address_parser import Parser
import cPickle as pickle

from address_parser import Parser
parser = Parser()

with open('gps_dump.pkl', 'rb') as f:
    gps_acc = pickle.load(f)

with open('tickets.pkl', 'rb') as f:
    tickets_acc = pickle.load(f)

from collections import defaultdict

d = defaultdict(lambda : [0,0])

def mkstreet(number, name, suffix):
    return "{} {} {}".format(number,name, suffix)

# Create a dict of date/street pairs, then mark them for if the pair
# was swept, then if the pair was ticketed
for base_street, dates in gps_acc.items():
    ps = parser.parse(base_street)
    
    # Expand each street block to the 100 block before and after, to deal 
    # with possible missing GPS reverse-geocodes
    streets = [mkstreet(ps.number.number, ps.road.name, ps.road.suffix),
              mkstreet(ps.number.number+100, ps.road.name, ps.road.suffix)]
    
    if ps.number.number >= 100:
        streets.append(mkstreet(ps.number.number-100, ps.road.name, ps.road.suffix))
    
    for street in streets:
        for date in dates:
            key = (date.isoformat(), street)
            d[key][0] +=1
        
for street, dates in tickets_acc.items():
    for date in dates:
        key = (date.isoformat(), street)
        d[key][1] +=1

rows = []
for (date, street), (swept, ticketed) in d.items():
        rows.append((date, street, swept, ticketed))
        
        
with open('sweeps.pkl', 'wb') as f:
    pickle.dump(rows, f)
        