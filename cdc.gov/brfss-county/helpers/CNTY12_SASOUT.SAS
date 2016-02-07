*****************************************************************************************
* FILE NAME:     CNTY12_SASOUT.SAS                                                      *
* DESCRIPTION:   THIS PROGRAM CONVERTS A STATES ASCII DATAFILE OF COMPLETES LOCATED AT  *
*                <DATAIN> FILEREF, INTO A SAS DATABASE STORED AT <DATAOUT> LIBREF       *
* REFERENCES:                                                                           *
* INPUT       DATAIN            FILEREF OF ASCII DATAFILE OF COMPLETES                  *
* FORMATS     FORMAT12.SAS7BCAT SAS FORMATS DATABASE                                    *
* OUTPUT      DATAOUT.SASDATA   SAS DATABASE VERSION OF ASCII DATA AS SPECIFIED IN      *
*                               <DATAIN> FILEREF                                        *
* UPDATED - 08/22/2013                                                                  *
*****************************************************************************************;
********************************
* Clear Output and Log Windows *
********************************;
DM OUTPUT 'clear' continue;
DM LOG    'clear' continue;
**********************************
* DEFINE SAS ENVIRONMENT OPTIONS *
**********************************;
OPTIONS PAGENO=1 NOFMTERR;
***************************************
* CLEAR EXISTING TITLES AND FOOTNOTES *
***************************************;
TITLE ;
FOOTNOTE ;
RUN ;
******************************************************************
* INSTRUCTIONS:                                                  *
* SPECIFY PATH OF WHERE ASCII DATAFILE IS STORED                 *
* SPECIFY PATH OF WHERE SAS DATASET IS TO BE STORED              *
* SPECIFY PATH OF WHERE SAS FORMAT LIBRARY IS STORED             *
* SPECIFY PATH OF WHERE THE FORMAT ASSIGNMET STATEMENT IS STORED *
******************************************************************;

*FILENAME DATAIN '<PATH OF INPUT STATE ASCII DATAFILE OF COMPLETES>' LRECL = 285 ;
*****************************************************************************
* EXAMPLE:                                                                  *
*       FILENAME DATAIN 'C:\BRFSS\2012\CNTY12.ASC' LRECL = 285              *
* NOTE: MAKE SURE THE ASTERISK IS REMOVED BEFORE THE WORD FILENAME AND      *
*       MAKE SURE THAT THE GREATER THAN AND LESS THAN SIGNS < > ARE REMOVED *
*       FROM THE FILENAME STATEMENT                                         *
*****************************************************************************;

*LIBNAME DATAOUT '<PATH OF PERMANENTLY STORED SAS DATASET VERSION OF DATAIN FILEREF>' ;
*****************************************************************************
* EXAMPLE:                                                                  *
*          LIBNAME DATAOUT 'C:\'                                            *
*          A SAS DATABASE WILL BE STORED AT C:\SASDATA.SAS7BDAT             *
* NOTE: MAKE SURE THE ASTERISK IS REMOVED BEFORE THE WORD LIBNAME AND       *
*       MAKE SURE THAT THE GREATER THAN AND LESS THAN SIGNS < > ARE REMOVED *
*       FROM THE LIBNAME STATEMENT                                          *
*****************************************************************************;

*LIBNAME LIBRARY '<PATH OF STORED SAS FORMAT12.SAS7BCAT>' ;
*****************************************************************************
* EXAMPLE:                                                                  *
*          LIBNAME LIBRARY 'C:\'                                            *
* NOTE: MAKE SURE THE ASTERISK IS REMOVED BEFORE THE WORD LIBNAME AND       *
*       MAKE SURE THAT THE GREATER THAN AND LESS THAN SIGNS < > ARE REMOVED *
*       FROM THE LIBNAME STATEMENT                                          *
*****************************************************************************;

*FILENAME FORMATIN '<PATH OF FORMAT ASSIGNMENT STATEMENT>' ;
*****************************************************************************
* EXAMPLE:                                                                  *
*          FILENAME FORMATIN 'C:\FORMATSTATEMENT.SAS'                       *
* NOTE: MAKE SURE THE ASTERISK IS REMOVED BEFORE THE WORD FILENAME AND      *
*       MAKE SURE THAT THE GREATER THAN AND LESS THAN SIGNS < > ARE REMOVED *
*       FROM THE FILENAME STATEMENT                                         *
*****************************************************************************;

DATA DATAOUT.SASDATA ;
INFILE DATAIN MISSOVER ;
INPUT
_STATE        1-2                     /* Record Identification */
FMONTH        3-4
DISPCODE      5-8
SEQNO         9-18
_PSU          19-28
GENHLTH       29                      /* Section 1: Health Status */
PHYSHLTH      30-31                   /* Section 2: Healthy Days - Health-Related Quality of Life */
MENTHLTH      32-33
POORHLTH      34-35
HLTHPLN1      36                      /* Section 3: Health Care Access */
PERSDOC2      37
MEDCOST       38
CHECKUP1      39
EXERANY2      40                      /* Section 4: Exercise */
CVDINFR4      41                      /* Section 5: Chronic Health Conditions */
CVDCRHD4      42
CVDSTRK3      43
ASTHMA3       44
ASTHNOW       45
CHCSCNCR      46
CHCOCNCR      47
CHCCOPD1      48
HAVARTH3      49
ADDEPEV2      50
CHCKIDNY      51
CHCVISN1      52
DIABETE3      53
LASTDEN3      54                      /* Section 6: Oral Health */
RMVTETH3      55
AGE           56-57                   /* Section 7: Demographics */
HISPANC2      58
MRACE         $59-64
ORACE2        65
VETERAN3      66
MARITAL       67
CHILDREN      68-69
EDUCA         70
EMPLOY        71
INCOME2       72-73
WEIGHT2       74-77
HEIGHT3       78-81
NUMHHOL2      82
RENTHOM1      83
SEX           84
PREGNANT      85
QLACTLM2      86                      /* Section 8: Disability */
USEEQUIP      87
SMOKE100      88                      /* Section 9: Tobacco Use */
SMOKDAY2      89
STOPSMK2      90
LASTSMK2      91-92
USENOW3       93
ALCDAY5       94-96                   /* Section 10: Alcohol Consumption */
AVEDRNK2      97-98
DRNK3GE5      99-100
MAXDRNKS      101-102
FLUSHOT5      103                     /* Section 11: Immunization */
FLSHTMY2      104-109
IMFVPLAC      110-111
PNEUVAC3      112
FALL12MN      113-114                 /* Section 12: Falls */
FALLINJ2      115-116
SEATBELT      117                     /* Section 13: Seatbelt Use */
DRNKDRI2      118-119                 /* Section 14: Drinking and Driving */
HADMAM        120                     /* Section 15: Breast/Cervical Cancer Screening */
HOWLONG       121
PROFEXAM      122
LENGEXAM      123
HADPAP2       124
LASTPAP2      125
HADHYST2      126
PCPSAAD1      127                     /* Section 16: Prostate Cancer Screening */
PCPSADI1      128
PCPSARE1      129
PSATEST1      130
PSATIME       131
PCPSARS1      132
BLDSTOOL      133                     /* Section 17: Colorectal Cancer Screening */
LSTBLDS3      134
HADSIGM3      135
HADSGCO1      136
LASTSIG3      137
HIVTST6       138                     /* Section 18: HIV/AIDS */
HIVTSTD3      139-144
HIVRISK3      145
_STSTR        146-150
_RFHLTH       151                     /* Section 1: Calculated Variables */
_HCVU651      152                     /* Section 3: Calculated Variables */
_TOTINDA      153                     /* Section 4: Calculated Variables */
_LTASTH1      154                     /* Section 5: Calculated Variables */
_CASTHM1      155
_ASTHMS1      156
_DRDXAR1      157
_EXTETH2      158                     /* Section 6: Oral Health */
_ALTETH2      159
_DENVST2      160
_PRACE        161-162
_MRACE        163-164
RACE2         165
_RACEG2       166
_RACEGR2      167
_RACE_G       168
_AGEG5YR      169-170
_AGE65YR      171
_AGE_G        172
HTIN4         173-175
HTM4          176-178
WTKG3         179-183
_BMI5         184-187
_BMI5CAT      188
_RFBMI5       189
_CHLDCNT      190
_EDUCAG       191
_INCOMG       192
_SMOKER3      193                     /* Section 9: Calculated Variables */
_RFSMOK3      194
DRNKANY5      195                     /* Section 10: Calculated Variables */
DROCDY3_      196-198
_RFBING5      199
_DRNKDY4      200-203
_DRNKMO4      204-207
_RFDRHV4      208
_RFDRMN4      209
_RFDRWM4      210
_FLSHOT5      211                     /* Section 11: Calculated Variables */
_PNEUMO2      212
_RFSEAT2      213                     /* Section 13: Calculated Variables */
_RFSEAT3      214
_RFMAM2Y      215                     /* Section 15: Calculated Variables */
_MAM502Y      216
_RFPAP32      217
_RFPSA21      218                     /* Section 16: Calculated Variables */
_RFBLDS2      219                     /* Section 17: Calculated Variables */
_RFSIGM2      220
_AIDTST3      221                     /* Section 18: Calculated Variables */
_CNTYWT       222-231                 /* County Weighting and Stratification Variables */
CNTYNAME      $232-281                /* County Weighting and Stratification Variables */
_CNTY         282-284                 /* County Weighting and Stratification Variables */
ENDOFREC      285                     /* End of Record Marker */
;
*****************************************************************
* TO INCLUDE THE FORMAT ASSIGNEMT STATEMENT REMOVE THE ASTERISK *
* FROM THE BEGINNING OF THE FOLLOWING LINE                      *
*****************************************************************;
* %INCLUDE FORMATIN ;
*************************************************
* THIS SECTION CREATES LABELS FOR THE VARIABLES *
*************************************************;
Label
;
RUN;
