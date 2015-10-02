
from ambry_sources.mpf import MPRowsFile
from address_parser import Parser
import cPickle as pickle

import time

f = MPRowsFile('/Users/eric/proj/virt/ambry10/library/build/nbcuni.com/streetsweep/nbcuni.com/streetsweep-0.0.1/tickets.mpr')

parser = Parser()

start = time.time()
s = 0 
from collections import defaultdict
acc = defaultdict(set)
with f.reader as r:
    for i, row in enumerate(r, 1):

        adr = row.locationdesc1
        if adr:
            ps = parser.parse(adr)
            dt = row.issuedate
            if ps.number.number > 0 and dt:
                number = int(ps.number.number / 100) * 100
                
                key = "{} {} {}".format(number, ps.road.name, ps.road.suffix)
                print row
                acc[key].add(dt)
        
        if i % 10000 == 0:
          
            print i, len(acc), round( float(i) / ( time.time() - start), 2) 

with open('tickets.pkl', 'wb') as f:
    pickle.dump(acc, f)
        