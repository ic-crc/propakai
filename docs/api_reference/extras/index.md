
The `propakai.extras` subpackage provides additional tools for working with ITU Recommendations.
These tools are complementary to the core package and address common data preparation tasks.

[propakai.extras.buildings](./buildings.md)  
Retrieve building data, including footprint geometry and height, from shapefiles or OpenStreetMap.
Useful when working with ITU-R Recommendations such as P.1411.

[propakai.extras.streets](./streets.md)  
Using OpenStreetMap data, identify potential propagation paths for scenarios where antennas are
mounted below rooftop level and propagation is dominated by street canyon effects. Useful when
working with ITU-R Recommendations such as P.1411.


[propakai.extras.topography](./topography.md)  
Read terrain elevation, surface elevation and clutter profiles from various raster file formats
such as GeoTIFF. Retrieve radio climatic zone profiles from ITU Digital World Map (IDWM) data.
Useful when working with ITU-R Recommendations such as P.452, P.1546, P.1812 and P.2001.
