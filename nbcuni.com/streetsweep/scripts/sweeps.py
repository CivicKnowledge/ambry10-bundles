
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
              mkstreet(ps.number.number+100, ps.road.name, ps.road.suffix),
              mkstreet(ps.number.number+200, ps.road.name, ps.road.suffix),
              mkstreet(ps.number.number+300, ps.road.name, ps.road.suffix)
          ]
    
    if ps.number.number >= 100:
        streets.append(mkstreet(ps.number.number-100, ps.road.name, ps.road.suffix))
        
    if ps.number.number >= 200:
        streets.append(mkstreet(ps.number.number-200, ps.road.name, ps.road.suffix))
        
    if ps.number.number >= 300:
        streets.append(mkstreet(ps.number.number-300, ps.road.name, ps.road.suffix))
    
    for street in streets:
        for date in dates:
            key = (date.isoformat(), street)
            d[key][0] +=1
        
for street, dates in tickets_acc.items():
    for date in dates:
        key = (date.isoformat(), street)
        d[key][1] +=1

# Year and months that the city claims the GPS system was not working
claimed_exclusions = "2015-01 2015-02 2015-03 2015-04 2014-11 2014-10 2014-09 2014-08 2014-07".split()
 

rows = []
from collections import defaultdict
counts = defaultdict(int)
for (date, street), (swept, ticketed) in d.items():
    claimed_no_gps = 'Y' if date[:7] in claimed_exclusions else 'N'
    rows.append((date, street, swept, ticketed, claimed_no_gps))
    counts[street] += swept
          
print "DUmp sweeps pickle"
with open('sweeps.pkl', 'wb') as f:
    pickle.dump(rows, f)
   

print "Write sweeps.csv"
import csv
with open('sweeps.csv','wb') as f:
    w = csv.writer(f)
    w.writerow(('date', 'street', 'swept', 'ticketed','claimed_no_gps'))
    w.writerows(rows)
    
print "write sweeps-claimed-no-gps"
with open('sweeps-claimed-no-gps.csv','wb') as f:
    w = csv.writer(f)
    w.writerow(('date', 'street', 'swept', 'ticketed','claimed_no_gps'))
    for row in rows:
        if row[4] == 'Y':
            w.writerow(row)

print "Write sweeps-counts"
import csv
with open('sweep-counts.csv','wb') as f:
    w = csv.writer(f)
    w.writerow(('street','sweepcount'))
    w.writerows(counts.items())
    