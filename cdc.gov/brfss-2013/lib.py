# -*- coding: utf-8 -*-
# Ambry Bundle Library File
# Use this file for code that may be imported into other bundles

# _PSU is alias for SEQNO, IDATE is alias for year, month, date. Should skip both.


def get_specs(bundle):
    """ Returns list with column specs, scraped from an HTML page """
    import requests
    from bs4 import BeautifulSoup

    url = bundle.source('columnlist').ref

    response = requests.get(url)

    assert response.status_code == 200, \
        'Download error: status_code: {}, text: {}'.format(response.status_code, response.text)

    bf = BeautifulSoup(response.text)
    tables = bf.select('table')
    assert len(tables) == 1
    table = tables[0]
    specs = {}
    position = 1

    specs = []

    for i, tr in enumerate(table.select('tr')):

        if i == 0:
            assert 'Is header'
            continue
     
            
        row = [' '.join(x.strings) for x in tr.select('th')+tr.select('td')]
        assert len(row) == 3
       
        start, var_name, width = row
        position = position

        specs.append({
            'name': var_name,
            'start': int(start),
            'width': int(width),
            'position': position})
            
        position += 1

    return specs
        
    
def yield_lines(bundle):
    """Yield interesting lines from the converted text file"""

    f = bundle.source_fs.getcontents(bundle.source('codebooktxt').ref)
    
    f = f.replace('SAS Variable Name:', '\nVarname:')\
    .replace('Calculated Variables Type:','\nCalcVarType:')\
    .replace('Type:','\nType:')

    for line in f.splitlines():
        line = line.strip()
        if not line:
            continue
          
        words = line.split()
        
        if words[0] in ('Section:', 'Column:','Description:','Prologue:','Varname:', 'Type:'):
            yield line
        
def yield_records(bundle):
    """Yield records, converted from lines. Each rec is a dict of values. """
    recs = []
    rec = {}
    
    seen = set()
    
    for l in yield_lines(bundle):
        
        if not ':' in l:
            bundle.error('Bad line: {}'.format(l))
            continue
            
        k, v = l.split(':', 1)
      
        if k == 'Section':
            continue
      
        if rec and k == 'Type' and v.strip() not in seen:
            yield rec
            rec = {}
            seen.add(v)
        
        if k == 'Column':
            if '-' in v:
                start, end = v.split('-')
                rec['start'] = int(start)
                rec['end'] = int(end)
            else:
                try:
                    rec['start'] = int(v.strip())
                except ValueError as e:
                    pass # Hell, I don't know ... 
                
        else:
            rec[k.lower()] = v.strip()
            
def columns(bundle, specs):
    """Read the spec from the HTML file, and merges it with the descriptions
    from the codebook.txt file. 

    Does *not* use the convered SPSS label file

    """
    from ambry.build import yield_lines, yield_records

    descriptions = {e['varname']:e for e  in yield_records(bundle) }
        
    cols = {}
    
    for s in specs: 
        if s['name'] not in cols: # Because there are duplicates
            cols[s['name']] = s
            
            cols[s['name']]['description'] = descriptions.get(s['name'],{}).get('description')
            
    return sorted(cols.values(), key=lambda e: e['start'])
    
def read_labels(bundle): 
    """Read the variable labels ( descriptions ) from an SPSS file
    
    Currently unused
    """
    import re

    p = re.compile(r'_column\((?P<colid>\d+)\)\s+(?P<datatype>[^\s]+)\s+(?P<name>[^\s]+)\s+(?P<format>%\d+\w)(?:\s+\"(?P<description>[^\"]+)\")?')
    
    f = bundle.source_fs.getcontents(bundle.source('labels').ref)
    
    labels = []
    
    for l in f.splitlines():
        l = l.strip()
        if not l.startswith('_column'):
            continue
            
        m = p.match(l)
        labels.append(m.groupdict())

    return labels
    
def meta_source_schema(bundle, specs):
    """Read the spec from the HTML file, and bergest it with the descriptions
    from the codebook.txt file. 

    Does *not* use the converted SPSS label file

    """
 
    bundle.dataset.source_tables[:] = []
    bundle.commit() 
    
    t = bundle.dataset.new_source_table('brfss')
    
    for i,c in enumerate(columns(bundle, specs),1):
        t.add_column(source_header=c['name'],
                     dest_header=c['name'].lower(),
                     position=i,
                     datatype=int,
                     description=c['description'],
                     start = c['start'],
                     width=c['width']
                     )
               
    bundle.build_source_files.sourceschema.objects_to_record()      
    bundle.commit()
        
    