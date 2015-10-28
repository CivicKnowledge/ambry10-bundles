 # -*- coding: utf-8 -*-
import ambry.bundle 
from ambry.util import memoize


class Bundle(ambry.bundle.Bundle):

    _states = None

    def init(self):
        
        self.url_root = self.source('root_5').url
        
        self.small_url_template = "{root}/{state_name}_Tracts_Block_Groups_Only.zip"
        self.large_url_template = "{root}/{state_name}_All_Geographies_Not_Tracts_Block_Groups.zip"
        
        self.year = self.metadata.about.time
        self.release = self.metadata.build.release
        
    jam_map = {
        '.': 'm', # Missing or suppressed value
        ' ': 'g',
        None: 'N'
    }
    
    def jam_float(self,v,errors, row):
        """Convert jam values into a code in the jam_values field and write a None"""
        
        try:
            return float(v)
        except:
            if not 'jams' in errors:
                errors['jams'] = ''
                
            try:
                errors['jams'] += self.jam_map[v]
            except KeyError:
                self.error(row)
                raise
                
            return None
            
    def jam_values(self, errors, row):
        """Write the collected jam codes to the jam_value field."""
        
        jams =  errors.get('jams')
        
        # FIXME This is a bit fragile. The -5 is to remove the count of the non
        # data columns.         
        if jams == 'm'* (len(row) - 5): # All entries are missing
            return 'M' # save some space
        else:
            return jams
        
    @property
    @memoize
    def states(self):
        """Return tuples of states, which can be used to make maps and lists"""
        
        if not self._states:
        
            self._states = []
        
            with self.source('states').datafile.reader as r:
                for row in r.select( lambda r: r['component'] == '00'):
                    self._states.append((row['stusab'], row['state'], row['name'] ))
                    
        return self._states
        
    ##
    ## Create Tables
    ##
        
    def create_tables(self):

        self.log("Deleteting old tables and partitions")
        self.dataset.delete_tables_partitions()
        
        self.commit()

        tables = self.tables_list()
        
        self.log("Creating {} tables".format(len(tables)))
        
        lr = self.init_log_rate(100)
        
        for i, table_id in enumerate(sorted(tables.keys())):

            d = tables[table_id]
            
            lr(table_id)
            
            self.make_table( **d )
            
        self.commit()
        
        self.sync_out()
        

    def make_table(self,  name, universe, description, columns, data):
        
        t = self.new_table(name, description = description.title(), universe = universe.title(),
                           data = data)

        header_cols = [
            #('FILEID','File Identification',6 ),
            #('FILETYPE','File Type',6),
            ('STUSAB','State/U.S.-Abbreviation (USPS)',2 ),
            ('CHARITER','Character Iteration',3 ),
            ('SEQUENCE','Sequence Number',4 ),
            ('LOGRECNO','Logical Record Number',7 )
        ]
        
        for name, desc, size in header_cols:
            t.add_column(name, description = desc, size = size)
           
        seen = set()
           
        for col in columns:
            if col['name'] in seen:
                print col['name'],  "already in name;", seen
                raise Exception()
                
            t.add_column( transform='^jam_float', **col )
            
            seen.add(col['name'])
            
        t.add_column(name='jam_flags', datatype='str', transform='^jam_values',
              description='Flags for converted Jam values')
            

    def tables_list(self,  add_columns = True):
        from collections import defaultdict
        from ambry.orm.source import DataSource
        from ambry.util import init_log_rate
        
        def prt(v): print v
        
        lr = init_log_rate(prt)

        tables = defaultdict(lambda: dict(table=None, universe = None, columns = []))

        year = self.metadata.about.time
        release = self.metadata.build.release

        table_id = None
        seen = set()
        ignore = set()
        
        #name, universe, description, columns
        
        i = 0
        
        with self.source('table_sequence').datafile.reader as r:
            for row in r:
                

                if int(row['year']) != int(year) or int(row['release']) != int(release):
                    #print "Ignore {} {} != {} {} ".format(row['year'], row['release'], year, release)
                    continue
    
                if row['table_id'] in ignore:
                    continue

                if int(row['sequence_number'] ) > 117:
                    # Not sure where the higher sequence numbers are, but they aren't in this distribution. 
                    continue

                    
                i += 1

                table_name = row['table_id']

                if row['start']:
        
                    # Breaking here ensures we've loaded all of the columns for
                    # the previous tables. 
                    if self.test and i > 1000:
                        break
        
                    if table_name in seen:
                        ignore.add(table_name)
                        continue
                    else:
                        seen.add(table_name)
        
                    start = int(float(row['start']))
                    length = int(row['table_cells'])
                    slc = "2,3,4,5,{}:{}".format(start-1, start+length-1)

                    tables[table_name] = dict(
                        name = row['table_id'],
                        universe=None,
                        description=row['title'].title(),
                        columns=[],
                        data = dict(
                            sequence = int(row['sequence_number']),
                            start=start, 
                            length=length, 
                            slice = slc
                        )
                    )
        
                elif 'Universe' in row['title']:
                    tables[table_name]['universe'] = row['title'].replace('Universe: ','').strip()

                elif add_columns and row['is_column'] == 'Y':
                    
                    
                    col_name = table_name+"{:03d}".format(int(row['line']))
  
                    col_names = [ c['name'] for c in tables[table_name]['columns'] ]
                    if col_name  in col_names:
                        raise Exception("Already have {} in {}".format(col_name, 
                                        col_names))
  
                    tables[table_name]['columns'].append(dict(
                        name=col_name,
                        description=row['title'], datatype = 'float')
                        )
                
        
        return tables
 
    ##
    ##
    ##
 
    def create_jobs(self):
        
        from ambry.etl import Pipeline, PrintEvery, PrintRows, Slice, AddDestHeader
        from ambry.dbexceptions import ConfigurationError
  
        self.dataset.delete_partitions()
  
        skip_sequence = set()
  
        for table in self.dataset.tables:
        
            if table.name != 'b08526':
                continue
        
            sources = self.table_sources(table)

            if self.test:
                sources = sources[:10]

            self.log("Table {} with {} sources".format(table.name, len(sources)))
            
            self.ingest(sources=sources, update_tables = False)   

            self.build(sources=sources)
       
    def post_build(self, phase='build'):
        """After the build, update the configuration with the time required for
        the build, then save the schema back to the tables, if it was revised
        during the build."""

        try:
            self.build_post_unify_partitions()
        except Exception:
            self.set_error_state()
            self.commit()
            raise

        return True
       
    def post_everything(self):
        self.library.search.index_bundle(self, force=True)

        self.state = phase + '_done'

        self.log("---- Finished Build ---- ")


    def table_sources(self, table):
        """Create a set of transient sources for a single table, one for each of
        the 52 states and two URLs. """
        
        from ambry.orm import TransientDataSource
        
        table_name = table.name
        start = table.data['start']
        length = table.data['length']
        sequence = table.data['sequence']

        sources  = []
   
        for stusab, state_id, state_name in self.states:

            slc = "2,3,4,5,{}:{}".format(start-1, start+length-1)

            file = "e{}{}{}{:04d}000.txt".format(self.year,self.release,
                         stusab.lower(),sequence)

            for (size, url_template) in [('s', self.small_url_template), 
                                         ('l',self.large_url_template)]:
                
                url = url_template.format(root=self.url_root, state_name=state_name).replace(' ','')
        
                source = TransientDataSource(
                                # Must have id to make segments in SelectPartition
                                sequence_id = int(table.sequence_id) * 100 + int(state_id), 
                                name='{}_{}_{}_{}'.format(stusab, size, file, table_name), 
                                filetype = 'csv', 
                                reftype = 'zip',
                                url = url, 
                                dest_table_name = table_name,
                                file = file, 
                                time=self.year, 
                                space = stusab, 
                                start_line = 0, # No header
                                segment = slc) # The Slice pipe gets the slice from here. 
                                
                source._bundle = self
                
                sources.append(source)
          
        return sources
  

