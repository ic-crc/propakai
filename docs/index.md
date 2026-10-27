#  <!-- white space title to avoid "Home" being displayed -->
<p align="center">
  <img src="./assets/propakai_logo_name.png" alt="Project Logo" width="333"/>
</p>

PropaKai is a cohesive Python package for implementations of ITU-R P. recommendations.

These recommendations, developed by the International Telecommunication Union Radiocommunication
Sector (ITU-R) Study Group 3, provide international standards and methods for predicting the
propagation of radio waves.

### Disclaimer
> This project, PropaKai, is an independent, third-party software implementation of certain ITU-R P.
recommendations. This project is not affiliated with, maintained by, authorized by, sponsored by,
or in any way officially connected with the International Telecommunication Union (ITU). Any use of
the acronym "ITU" is for descriptive and identification purposes only. For official texts and
standards, users must refer directly to the official ITU website
([www.itu.int](https://www.itu.int)).


## How to Install

To install or update the PropaKai package on your system, first download the latest wheel file
(.whl) from the [Releases page](https://github.com/ic-crc/propakai/releases).

From the directory containing the .whl file, install the package with:
```bash
# Replace x.y.z with the current version number.
# Omit "[full]" for a minimal installation with only core dependencies.
python -m pip install propakai-x.y.z-py3-none-any.whl[full]
```
*Note: instead of the `python` command, you may sometimes have to use `py` on Windows or `python3`
on macOS/Linux.*


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


## How to Uninstall

To uninstall the package, you may use:
```bash
# This will delete any digital map or other ITU data file that PropaKai
# may have downloaded and installed.
propakai-data-cleanup

python -m pip uninstall propakai
```

*Note: Alternately to `propakai-data-cleanup`, you may use `propakai-info` to get the
installation path for ITU data files and perform the deletion manually, as desired.*


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

    >The download URLs from the ITU website are shown to the user.  
    >A notice informs the user that the files are for personal use only.  
    >Files must not be modified after downloading.

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
  
    Standard CPython (Most Users):<br>
    *In standard CPython, a mechanism known as the Global Interpreter Lock (GIL) prevents multiple
    threads from executing on more than one CPU core at the same time. For this reason, multithreading
    does not benefit CPU-bound tasks. To achieve true parallelism, multiprocessing is the
    traditionally recommended approach, and PropaKai works seamlessly with it.*
    <br><br>
    Experimental Free-Threaded CPython (Python 3.13+):<br> 
    *Starting with Python 3.13, an experimental alternative is available. You can now install a
    special free-threaded build of CPython. This is a separate Python interpreter compiled without
    the GIL. While this is currently an optional installation, the long-term goal of the Python core
    development team is for this free-threaded mode to eventually become the default. If you are
    running PropaKai within one of these specific builds, multithreading can provide significant
    speed-ups for CPU-bound tasks.*
    </details>

- The `propakai.geo_catalog` subpackage has been added to facilitate usage of the
[ITU-R Geospatial Catalog](https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/). The 
`propakai.extras` subpackage provides complementary tools to the core package and address common
data preparation tasks.


## Words of Wisdom

> *"Propagation not just formulas only. Propagation, lesson for whole science. Wave have a balance,
everything be better."*
>
> — Mr. Miyagi (probably)

