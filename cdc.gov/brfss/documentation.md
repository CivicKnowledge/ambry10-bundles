
# {{about.title}}

{about_summary}

##  Column Names Changes

There are two column names that overlap with other columns: 

  * _PSU. The value is identical to SEQNO
  * IDATE. The value is covers the three fields IMONTH, IDAY and IYEAR
  
These two columns are excluded. 

## Other Changes

There are many fields like IMONTH, IDAY and IYEAR, that are listed in the codebook as CHAR, when they appear to be INT. These are integers in the schema. 

## Converting codebook to source_schema.csv
WARNING: this will replace your existing source_schema.csv!
1. Install pdftohtml
2. Execute
```bash
python source_schema.py
```



