`propakai.geo_catalog` is a sub-package for querying the ITU-R Geospatial Catalog.

Instead of using locally installed digital maps like other recommendation modules in the main
package, geo_catalog queries an ITU's REST API in order to get a digital map's interpolated value
for a specific location.

See https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/


##### Code Snippet

```python
from propakai.geo_catalog import gc_p1511_3

if __name__ == '__main__':
    height_m = gc_p1511_3.topographic_height(lat=45.0, lon=-75.0)
    print(f'Terrain height: {height_m:.1f} m')
```