[Français](./README.fr.md)

To install the requirements and build the HTML documentation from a virtual environment, use the
following commands from the **project's root directory**.

On Windows (Command Prompt):
```bash
# Create the virtual environment in a folder named 'venv'
py -m venv venv

# Activate the environment
.\venv\Scripts\activate

# Install packages needed for building the documentation
python -m pip install -r requirements-docs.txt

# Build and serve the documentation using a static site generator
zensical serve

# Once done building/testing documentation
deactivate
```


On Linux and macOS:
```bash
# Create the virtual environment in a folder named 'venv'
python3 -m venv venv

# Activate the environment
source venv/bin/activate

# Install packages needed for building the documentation
python -m pip install -r requirements-docs.txt

# Build and serve the documentation using a static site generator
zensical serve

# Once done building/testing documentation
deactivate
```
