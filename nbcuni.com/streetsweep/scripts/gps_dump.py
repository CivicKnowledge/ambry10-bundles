
from ambry_sources.mpf import MPRowsFile
from address_parser import Parser
import cPickle as pickle

import time

f = MPRowsFile('/Users/eric/proj/virt/ambry10/library/build/nbcuni.com/streetsweep/nbcuni.com/streetsweep-0.0.1/gps.mpr')

parser = Parser()

start = time.time()
s = 0 
from collections import defaultdict
acc = defaultdict(set)
with f.reader as r:
    for i, row in enumerate(r, 1):

        adr = row.strlocation
        if adr:
            ps = parser.parse(adr)
            dt = row.dttime.date()
            if ps.number.number > 0 and dt:
                number = int(ps.number.number / 100) * 100
                
                key = "{} {} {}".format(number, ps.road.name, ps.road.suffix)
                acc[key].add(dt)
        
        if i % 10000 == 0:
          
            print i, len(acc), round( float(i) / ( time.time() - start), 2) 

with open('gps_dump.pkl', 'wb') as f:
    pickle.dump(acc, f)
        