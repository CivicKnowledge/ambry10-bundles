

Caveats
=======

As of Dec 1, 2015, In the ``Neighborhood Change`` files, the Relative Standard Error (rse) column is often computed for values that are ver close to zero, so the RSE is very large. In other files in this dataset, the rse value is capped
at 100. As per Dulce Bustamante-Zamora at CDPH, these values should be blank, (NULL) so this correction is made for rows where the difference is 0. 