
# Check the min and max dates for GPS records and tickets, to make sure the overlap. 

from ambry_sources.mpf import MPRowsFile
from address_parser import Parser
import cPickle as pickle

from address_parser import Parser
parser = Parser()

print 'Loading'

with open('gps_dump.pkl', 'rb') as f:
    gps_acc = pickle.load(f)

with open('tickets.pkl', 'rb') as f:
    tickets_acc = pickle.load(f)
    

print "GPS Min", min(date for base_street, dates in gps_acc.items() for date in dates)   
print "GPS Max", max(date for base_street, dates in gps_acc.items() for date in dates)

print "Tik Min", min(date for street, dates in tickets_acc.items() for date in dates)
print "Tik Max", max(date for street, dates in tickets_acc.items() for date in dates)