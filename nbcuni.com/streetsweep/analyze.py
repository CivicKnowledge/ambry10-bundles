
from ambry_sources.mpf import MPRowsFile
from address_parser import Parser
import cPickle as pickle
import csv

from address_parser import Parser
parser = Parser()

with open('sweeps.pkl', 'rb') as f:
    rows = pickle.load(f)
    
with open('ticket-not-swept.csv', 'w') as f:
    w = csv.writer(f)
    w.writerow(('date','number','street','tickets'))
    for (date, street, swept, ticketed) in rows:
        if ticketed and not swept:
            ps = parser.parse(street)
            row = (date, ps.number.number, ps.road.name+' '+ps.road.suffix, ticketed)
            print row
            w.writerow(row)