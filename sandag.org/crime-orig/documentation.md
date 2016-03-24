
Processed crime incidents, based on data supplied by SANDAG.

This dataset includes a set of crime incidents from 1 Jan 2007 to 31 March 2013 that were returned by SANDAG for Public Records request 12-075, and another set that was returned by an unnumbered request, for 2012, 2013, 2014 and 2015. These two dataset have different structures, with the second having more columns that the first, and some of the charges and charge descriptions are different. 

The dataset was provided without documentation, so here are some guesses:




Caveats
=======

As with most crime data, there are many issues, limitations and problems that users must be aware of to avoid making incorrect conclusions. 

*Crime incident data is inherently problematic.* Crime incident reports are collected by busy officers in stressful situations who are trying to describe complex situations with rigid categories. Virtually every point of the data collection process has multiple opportunities for errors and few opportunities for correction after the fact. Analysts must consider the difficulties of collecting crime data when assessing the validity of any conclusions. 

*Data is collected by 19 different agencies.* While the data is all sourced from SANDAG, it originates with 19 different police departments. These departments may have different policies that can result in different categorizations for the same crime, and they may have different emphases on  which crimes they pursue. 

*Many incidents at a single point.* Because all of the crimes on a block are geocoded to the middle of the block, many incidents will appear as a single point. 

*5% of crimes are not geocoded*. GIS users should consider that about 5% of the incidents were not properly geocoded, and are not included in the shapefiles. These crimes appear in the CSV files, and can be included in time series analysis, but they will not be available for spatial analysis. 

*Time and dates are often unreliable* Time and dates for many incidents are unreliable, with times being more unreliable than dates. 

  * Property crimes that occur while the owner is gone may be recorded as the time a responsible person left the property, arrived at the property to discover the crime, or the average between the two. There is no information available to select among these possibilities, so these incidents have very unreliable times. 

  * Because the time is unreliable, so is the date, for crimes that occurred at night. 

  * Times may have not been recorded in the original report. These times may be entered as midnight, or as another time. 


*Multiple crime incidents may not have all crimes recorded.* If a single person is charged with multiple violations for a single arrest, departments may enter only the most serious charge, the last charge, or all of the charges. There is no information to disambiguate these possibilities. 

*Locations may be unreliable*. Crimes that involve pursuits or violations committed and multiple locations may be recorded and any of many different locations.  When the location is ambiguous, tt is common for incidents to have the address recorded as the location where the arrested person was charged. Because of this, the highest crime block in San Diego is the downtown police station. Check high crime locations to ensure they are not police stations. 

