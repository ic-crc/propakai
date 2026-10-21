[Français](./README.fr.md)

To install the requirements and run the tests from a virtual environment, use the following commands
from the **project's root directory**.

Note that running the tests triggers the download of multiple ITU files (e.g. digital maps,
statistics, etc.) when not already available locally. Some tests use monthly statistics and require
several GB of data to be downloaded the first time they are run, consequently they are skipped by
default but may be activated through an environment variable (NO_SKIP) if desired.

On Windows (Command Prompt):
```bash
py -m venv venv

.\venv\Scripts\activate

python -m pip install -r requirements-tests.txt

cd tests

# To run default tests only
python -m unittest discover -s "tests"

# To run all tests
set NO_SKIP=1 && python -m unittest discover -s "tests"

deactivate
```

On Linux and macOS:
```bash
python3 -m venv ../venv

source venv/bin/activate

python -m pip install -r requirements-tests.txt

cd tests

# To run default tests only
python -m unittest discover -s "tests"

# To run all tests
NO_SKIP=1 python -m unittest discover -s "tests"

deactivate
```
