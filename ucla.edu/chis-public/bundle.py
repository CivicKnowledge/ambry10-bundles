# -*- coding: utf-8 -*-
import ambry.bundle

class Bundle(ambry.bundle.Bundle):
         
    def get_groups(self):
    
        pdd = ProcessDataDict(self, self.source('chis13dd_adult'))
        
        for group in pdd:
            print group
        
        
class ProcessDataDict(object):
    
    def __init__(self, bundle, source):
        self._bundle = bundle
        self._source = source
        self._library = self._bundle.library
    
        self._url = source.url
      
    def cmd_exists(self, cmd):
        import subprocess
        return subprocess.call("type " + cmd, shell=True, 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0
        
    def download(self):
        
        import requests
        import subprocess
        import os.path
        from ambry_sources.fetch import download
        
        if not self.cmd_exists('pdftohtml'):
            self.fatal("pdftohtml program does not exist")
              
        pdf_file_name, dt = download(self._url, self._library.download_cache)
        xml_file_name =  os.path.split(pdf_file_name)[-1].replace('.pdf', '' )
    
        pdf_path = self._library.download_cache.getsyspath(pdf_file_name)
        xml_path = self._bundle.build_fs.getsyspath(xml_file_name)
    
        if not os.path.exists(xml_path+".xml"):
            call_args = ['pdftohtml', '-xml', pdf_path, xml_path]
            process = subprocess.Popen(call_args)
            if process.wait() != 0:
                print('Errors while converting pdf to xml.')
            
        return xml_path+'.xml'
    
    
    def _generate_text(self):
        """Read the XML file and generate text strings. """
   
        import os
        import os.path
        from lxml import etree
        from StringIO import StringIO
        
        fn = self.download()
        
        with open(fn) as f:
            response = f.read()
            
        try:
            parser = etree.XMLParser(ns_clean=True, recover = True)
            tree   = etree.parse(StringIO(response), parser)
            
            for r in tree.findall('.//text'):
                yield r.text
     
        except etree.XMLSyntaxError:
            print 'XML parsing error.'
            
    
    def _generate_groups(self):
        """Read test strings from generate_text() and group along variables boundaries. """
        group = None
    
        for t in self._generate_text():  
             
            if t:
             
                t = t.strip()
            
                if group is None and t == 'VARNAME:':
                    group = []         
               
                if group is not None:
                    group.append(t)
                    
                if group is not None and t == 'NOTES:':
                    yield group
                    group = None
    
    def cut(self, g, tag, extend = False):
        """From the group array g, cut out the tag and return the editied group and the 
        value after the tag."""
        
        try:
            p = g.index(tag)
          
            
            # If the next entry doe snot have a ':', it may be 
            # a continuiation of this one
            if extend and ':' not in g[p+2] and len( g[p+1]) > 50:
                return g[:p]+g[p+3:], g[p+1]+' '+g[p+2]
            else:
                return g[:p]+g[p+2:], g[p+1]
            
        except ValueError:
            return g, None
        except IndexError:
            if tag not in ('NOTES:', 'INPUT VAR:'): # Usually has nothing after it. 
                
                self._bundle.error("Index error in group '{}' for tag '{}' ".format(g, tag))
            return g, None
        
    def remove(self, g, tag):
        
        try:
            g.remove(tag)
        except ValueError:
            pass
        

    def __iter__(self):
        """Read groups, which are actually arrays, and convert them to dicts. """
        import tabulate
        
        
        for g in self._generate_groups():
            
            self.remove(g, 'INPUT VAR: NA')
            self.remove(g, 'MEAN STATISTICS')
            
            try:
                notes_pos = g.index('NOTES:')
                g, notes = (g[:notes_pos], g[notes_pos+1:])
            except ValueError:
                pass
            
            g, varname = self.cut(g, 'VARNAME:')
            g, label = self.cut(g, 'LABEL:')
            g, universe = self.cut(g, 'UNIVERSE:', extend = True)
            g, qname11 = self.cut(g, 'QNAME11:')
            g, qname13 = self.cut(g, 'QNAME13:')
            g, qname14 = self.cut(g, 'QNAME14:')
            
            g, min_ = self.cut(g, 'MIN')
            g, max_ = self.cut(g, 'MAX')
            g, mean = self.cut(g, 'MEAN')
            g, n = self.cut(g, 'N')
            
            g, input_var = self.cut(g, 'INPUT VAR:')
            if g[-1] == 'INPUT VAR:':
                g.pop()
            
            #['code','val','freq','pct']
            codes = []
            if g and g[0] == 'FREQ':
                headers, g =  g[:3], g[3:]
               
                for i in range(int(len(g)/4)):
                    triple = g[:4]
                    g = g[4:]
                    codes.append(triple)
            
            yield dict(
                name = varname, 
                label = label,
                universe = universe,
                codes = codes, 
                n = n,
                mean = mean, 
                min = min_, 
                max = max_,
                input_var = input_var, 
                notes = notes
            )
              
            
            