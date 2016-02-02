# -*- coding: utf-8 -*-
import ambry.bundle



class Bundle(ambry.bundle.Bundle):
    pass


    def _ensure_pdf_converted(self):
        """ Finds xml of the converted pdf. If not found, downloads pdf and converts to xml. """
    
        import os
        import requests
        import subprocess
    
        url = self.source('datadict').url
    
        pdf_file_name = 'CODEBOOK13_LLCP.pdf'
        xml_file_name = 'CODEBOOK13_LLCP.xml'
    
        pdf_path = self.build_fs.getsyspath(pdf_file_name)
        xml_path = self.build_fs.getsyspath(xml_file_name)
    
        def cmd_exists(cmd):
            return subprocess.call("type " + cmd, shell=True, 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0
    
        if not cmd_exists('pdftohtml'):
            self.fatal("pdftohtml program does not exist")
    
        def convert():
            self.log('Converting codebook to xml. Please wait...')
            call_args = ['pdftohtml', pdf_path, xml_path, '-xml']
                      
            self.log("Running {}".format(call_args))
                      
            process = subprocess.Popen(call_args)
            if process.wait() != 0:
                self.log('Errors while converting pdf to xml.')

        if os.path.exists(xml_path):
            pass
        elif os.path.exists(pdf_path):
            # downloaded but not converted.
            convert()
        else:
            # no converted, no downloaded
            self.log('Downloading codebook. Please wait...')
        
            response = requests.get(url)
            assert response.status_code == 200
            self.build_fs.setcontents(pdf_file_name, response.content)
            
            convert()
