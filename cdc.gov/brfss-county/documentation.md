
# {about_title}

{about_summary}

## Data Conversion

This conversion of the BRFSS County data converts the PERIOD '.' character in the ASCII file to a NULL. 

## Errors

One record, seqno == 2012001899, has an illegal value for mrace, of '9 8   '. The record has been retained, but with the mrace value set to NULL. 

## Caveats

The county data is based on the BRFSS MSSA structure, and the BRFSS is based on a sample of the population, so not all counties have data. As noted in the dataset FAQ, [some counties did not have enough responses in all of the sample classes](http://www.cdc.gov/brfss/smart/smart_faq.htm#5) to produce an estimate for the county. 