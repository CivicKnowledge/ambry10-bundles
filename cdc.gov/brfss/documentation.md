
# {about_title}

{about_summary}

##  Column Names Changes

There are two column names that are duplicated:

  * _FRTLT1
  * _VEGLT1
  
The scond occurance of each are renamed by appending '_2'

There are two column names that overlap with other columns: 

  * _PSU. The value is identical to SEQNO
  * IDATE. The value is covers the three fields IMONTH, IDAY and IYEAR
  
These two columns are excluded. 

## Other Changes

There are many fields like IMONTH, IDAY and IYEAR, that are listed in the codebook as CHAR, when they appear to be INT. These are integers in the schema. 



