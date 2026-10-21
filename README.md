<p align="center">
  <img src="docs/assets/propakai_logo_name.png" alt="Project Logo" width="250"/>
</p>

#

[Français](./README.fr.md)

PropaKai is a cohesive Python package for implementations of ITU-R P. recommendations.

These recommendations, developed by the International Telecommunication Union Radiocommunication
Sector (ITU-R) Study Group 3, provide international standards and methods for predicting the
propagation of radio waves.

#### Disclaimer
> This project, PropaKai, is an independent, third-party software implementation of certain ITU-R P.
recommendations. This project is not affiliated with, maintained by, authorized by, sponsored by,
or in any way officially connected with the International Telecommunication Union (ITU). Any use of
the acronym "ITU" is for descriptive and identification purposes only. For official texts and
standards, users must refer directly to the official ITU website ([www.itu.int](www.itu.int)).


## How to Install

To install or update the PropaKai package on your system, first download the latest wheel file
**(.whl)** from the [Releases page](https://github.com/ic-crc/propakai/releases).

From the directory containing the .whl file, install the package with:
```bash
# Replace x.y.z with the current version number.
# Omit "[full]" for a minimal installation with only core dependencies.
python -m pip install propakai-x.y.z-py3-none-any.whl[full]
```
_Note: instead of the `python` command, you may sometimes have to use `py` on Windows or `python3`
on macOS/Linux._


## Code Snippet

Here is a little piece of code using PropaKai:
```python
from propakai import p1511_3 as p1511

if __name__ == '__main__':

    # The first call to topographic_height() will download and install the required
    # ITU digital map containing topographic height data. Any subsequent call will
    # re-use the installed digital map file.
    height_m = p1511.topographic_height(lat=45.0, lon=-75.0)

    print(f'Terrain height: {height_m:.1f} m')
```


## API Documentation

API documentation for PropaKai is found at:

https://ic-crc.github.io/propakai/


## How to Uninstall

To uninstall the package, you may use:
```bash
# This will delete any digital map or other ITU data file that PropaKai
# may have downloaded and installed.
propakai-data-cleanup

python -m pip uninstall propakai
```

_Note: Alternately to `propakai-data-cleanup`, you may use `propakai-info` to get the
installation path for ITU data files and perform the deletion manually, as desired._


## Included Implementations

[Recommendations](https://www.itu.int/rec/R-REC-P/en) being fully implemented or having significant
parts implemented include:

- **ITU-R P.368-10:** Ground-wave propagation prediction method for frequencies between 10 kHz and
30 MHz.
- **ITU-R P.452-18:** Prediction procedure for the evaluation of interference between stations on
the surface of the Earth at frequencies above about 100 MHz. _(excludes hydrometeor-scatter
interference prediction)_
- **ITU-R P.528-5**: A propagation prediction method for aeronautical mobile and radionavigation
services using the VHF, UHF and SHF bands.
- **ITU-R P.676-13:** Attenuation by atmospheric gases and related effects.
- **ITU-R P.835-7:** Reference atmospheres. _(excludes Annex 3)_
- **ITU-R P.838-3:** Specific attenuation model for rain for use in prediction methods.
- **ITU-R P.839-4:** Rain height model for prediction methods.
- **ITU-R P.840-9:** Attenuation due to clouds and fog.
- **ITU-R P.1510-1:** Mean surface temperature.
- **ITU-R P.1511-3:** Topography for Earth-space propagation modelling.
- **ITU-R P.1546-6:** Method for point-to-area predictions for terrestrial services in the frequency
range 30 MHz to 4000 MHz.
- **ITU-R P.1812-8:** A path-specific propagation prediction method for point-to-area terrestrial
services in the frequency range 30 MHz to 6 GHz.
- **ITU-R P.2001-6:** A general purpose wide-range terrestrial propagation model in the frequency
range 30 MHz to 50 GHz.
- **ITU-R P.2108-1:** Prediction of clutter loss.
- **ITU-R P.2109-2:** Prediction of building entry loss.
- **ITU-R P.2145-0:** Digital maps related to the calculation of gaseous attenuation and related
effects.
- **ITU-R P.2148-0:** Digital maps related to surface wind speed statistics.

Recommendations with partial implementations include:

- **ITU-R P.530-18:** Propagation data and prediction methods required for the design of terrestrial
line-of-sight systems.
- **ITU-R P.618-14:** Propagation data and prediction methods required for the design of Earth-space
telecommunication systems.
- **ITU-R P.619-6:** Propagation data required for the evaluation of interference between stations
in space and those on the surface of the Earth.
- **ITU-R P.681-11:** Propagation data required for the design systems in the land mobile-satellite
service.
- **ITU-R P.1411-13:** Propagation data and prediction methods for the planning of short-range
outdoor radiocommunication systems and radio local area networks in the frequency range 300 MHz to
300 GHz.

Others:

- The `propakai.geo_catalog` subpackage can be used to query the [ITU-R Geospatial
Catalog](https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/).
- The `propakai.extras` subpackage provides complementary tools and address common data preparation
tasks, like obtaining terrain profiles from raster files for instance.


## Key Concepts

Here are a few concepts that were kept in mind while designing and developing PropaKai.

- ITU recommendations are not always updated simultaneously. For instance, recommendation A may
have been updated while recommendation B continues to reference an earlier version of A. To prevent
unexpected code breakage and accommodate such scenarios, PropaKai is **designed to support
multiple versions of the same recommendation**.

- ITU data files (such as digital maps and statistics) cannot be redistributed. To facilitate their
use while complying with the ITU's terms, PropaKai **automatically downloads and stores the
necessary ITU data files** locally when needed. The ITU has granted permission for these downloads
as long as the following conditions are met:
  - The download URLs from the ITU website are shown to the user.
  - A notice informs the user that the files are for personal use only.
  - Files must not be modified after downloading.

- Python implementations are practical and can be easily run on many platforms. However,
implementations in other programming languages may sometimes be needed to achieve higher execution
speed. PropaKai **welcomes implementations of the same recommendation in both the Python and C/C++
programming languages**, as long as appropriate Python bindings are provided. For example, a Python
module implementing ITU-R P.2109-2 would be named `p2109_2`, while a module named `p2109_2_dso`
would indicate underlying usage of dynamic shared object(s) (DSO) from a compiled language. The
Python programmer can choose to use either one or both, as needed.

- Each function is **documented with a reference to the corresponding section or subsection** of
the recommendation. Function parameters are generally named after the variable names used in the
recommendations, while also adhering to Python's naming convention (snake_case).

- When available, **ITU validation files are used to verify the correctness of the
implementations**.

- PropaKai is designed to be **thread-safe**. Whenever possible, recommendations are implemented as
sets of pure functions—meaning they rely solely on their input parameters and do not use external
or global state. This approach greatly facilitates thread-safety. In cases where pure functions are
not feasible or desirable (such as when downloading or loading data files into memory), PropaKai
handles these situations internally to ensure thread safety is maintained.  

  <details>
  <summary>Notes on Concurrency in Python: Threads vs. Processes</summary>

  >**Standard CPython (Most Users):**  
  >_In standard CPython, a mechanism known as the Global Interpreter Lock (GIL) prevents multiple
  threads from executing on more than one CPU core at the same time. For this reason, multithreading
  does not benefit CPU-bound tasks. To achieve true parallelism, multiprocessing is the
  traditionally recommended approach, and PropaKai works seamlessly with it._
  >
  >**Experimental Free-Threaded CPython (Python 3.13+):**  
  >_Starting with Python 3.13, an experimental alternative is available. You can now install a
  special free-threaded build of CPython. This is a separate Python interpreter compiled without
  the GIL. While this is currently an optional installation, the long-term goal of the Python core
  development team is for this free-threaded mode to eventually become the default. If you are
  running PropaKai within one of these specific builds, multithreading can provide significant
  speed-ups for CPU-bound tasks._

</details>

- **Contributions are welcome!** You don't need to implement a full recommendation to contribute—
even adding a small section may benefit others. PropaKai currently includes some implementations
that are fully or nearly complete, as well as others where only a small section has been
implemented.


### Words of Wisdom

> _“Propagation not just formulas only. Propagation, lesson for whole science. Wave have a balance,
everything be better.”_
>
> — Mr. Miyagi (probably)
