

## Region codes

The `geotype` field has a code the describes the type of geography used in 
aggregating each row. These geographies are generally Census geographies, 
and are specified with Census geoids, in the `geotypevalue` field. The
`geotype` codes are:

- `CA` The whole state of California
- `CO` A county
- `CD` A county subdivision
- `PL` A Census Designated Place
- `RE` A Sub-state region
- `ZC` ZCTA, the Census version of a ZIP code area.


## Caveats

As of Dec 1, 2015, In the ``Neighborhood Change`` files, the Relative Standard Error (rse) column is often computed for values that are ver close to zero, so the RSE is very large. In other files in this dataset, the rse value is capped
at 100. As per Dulce Bustamante-Zamora at CDPH, these values should be blank, (NULL) so this correction is made for rows where the difference is 0. 

Two fields have been removed from the tables, 'ind_id', the ID number for the indicator in the table, and 'ind_definition.' These values are the same for every row in a table, so they have been moved to the table description. 

The `reportyear` field can be either a single integer year, or it may be a range of years, which is represented as a string. 