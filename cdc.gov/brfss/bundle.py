# -*- coding: utf-8 -*-
import ambry.bundle


class Bundle(ambry.bundle.Bundle):

    text_file_name = 'codebook_text.txt'

    # _PSU is alias for SEQNO, IDATE is alias for year, month, date. Should skip both.
    VARIABLES_TO_SKIP = ('_PSU', 'IDATE')

    # Columns listed here exist in the html but not in pdf.
    COLUMNS_TO_SKIP = (
        '2259-_FRTLT1',
        '2260-_VEGLT1',
    )

    # Some descriptions are hard to obtain. Set them manually.
    DESCRIPTIONS = {
        'CTELNUM1': 'Is this (phone number)?',
        '_PRACE1': 'Preferred race category',
        '_AGE80': 'Imputed Age value collapsed above 80',
    }
    
    # Variables listed here may have description less then 8.
    SHORT_DESCRIPTION = [
    ]

    NO_SPACE_DESCRIPTION = {
        'DROCDY3_': 'Drink-occasions-per-day',
    }
    

    def manual_fixes(self, specs):

        MANUAL_FIXES = {
            # There are really complicated vars, so it's easier to add them by hands.
            'BLOODCHO': {
                'type': 'Num',
                'start': 95,
                'end': 95,
                'position': specs['BLOODCHO']['position'],
                'width': 1,
                'description': 'Blood cholesterol is a fatty substance found '
                               'in the blood. Have you EVER had your blood cholesterol checked?'
            },
            'PSATEST1': {
                'type': 'Num',
                'start': 404,
                'end': 404,
                'position': specs['PSATEST1']['position'],
                'width': 1,
                'description': 'Have you EVER HAD a PSA test?'
            },
            'CARERCVD': {
                'type': 'Num',
                'start': 344,
                'end': 344,
                'position': specs['CARERCVD']['position'],
                'width': 1,
                'description': 'In general, how satisfied are you with the health '
                               'care you received? Would you say'
            }
        }
    


    def meta_convert_pdf(self):
        """Download and convert the PDF file to text
        
        
        """
        import io
        import json
        from ambry.util.text import generate_pdf_pages

        url = self.source('datadict').url

        pdf_file_name = 'CODEBOOK13_LLCP.pdf'
        
        pdf_path = self.build_fs.getsyspath(pdf_file_name)

        if not self.build_fs.exists(pdf_file_name):
            self.log("Download the PDF file")
            response = requests.get(url)
            assert response.status_code == 200
            self.build_fs.setcontents(pdf_file_name, response.content)
        
        if not self.build_fs.exists(self.text_file_name):
            self.log("Convert the PDF to text. This is really slow")
            with open(pdf_path) as f:
                self.build_fs.setcontents(self.text_file_name, '\n'.join(generate_pdf_pages(f,logger=self.logger)))


    def get_specs(self):
        """ Returns list with column specs, scraped from an HTML page """

        url = self.source('columnlist').ref
    
        response = requests.get(url)
    
    
        assert response.status_code == 200, \
            'Download error: status_code: {}, text: {}'.format(response.status_code, response.text)

        bf = BeautifulSoup(response.text)
        tables = bf.select('table')
        assert len(tables) == 1
        table = tables[0]
        specs = {}
        position = 1

        for i, tr in enumerate(table.select('tr')):
            if i == 0:
                assert 'Is header'
                continue
            row = [' '.join(x.strings) for x in tr.select('td')]
            assert len(row), 3
            start, var_name, width = row
            position = position
            if var_name in VARIABLES_TO_SKIP:
                continue
            if '{}-{}'.format(start, var_name) in COLUMNS_TO_SKIP:
                continue

            assert var_name not in specs
            specs[var_name] = {
                'start': int(start),
                'width': int(width),
                'position': position}
            position += 1
            
        return specs

        
    def yield_lines(self):
        """Yield interesting lines from the converted text file"""

        self.meta_convert_pdf()

        for line in self.build_fs.getcontents(self.text_file_name).splitlines():
            line = line.strip()
            if not line:
                continue
              
            line = line.replace('SAS Variable Name:', 'Varname:')
            words = line.split()
            
            if words[0] in ('Section:', 'Column:','Description:','Prologue:','Varname:', 'Type:'):
                yield line
            
    def yield_records(self):
        """Yield records, converted from lines"""
        recs = []
        rec = {}
        
        seen = set()
        
        for l in self.yield_lines():
            
            if not ':' in l:
                self.error('Bad line: {}'.format(l))
                continue
            
            k, v = l.split(':', 1)
               
            if rec and k == 'Section' and v.strip() not in seen:
                yield rec
                rec = {}
                seen.add(v)
                
            rec[k.lower()] = v.strip()
            
         
    def footest(self):
        
        for l in self.yield_lines():
            if 'Section:' in l:
                print l 
                