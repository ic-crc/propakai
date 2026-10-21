[Français](./README.fr.md)

To install the requirements and run the examples from a virtual environment, use the following
commands from the **project's root directory**.

On Windows (Command Prompt):
```bash
# Create the virtual environment in a folder named 'venv'
py -m venv venv

# Activate the environment
.\venv\Scripts\activate

# Install packages needed for the examples
python -m pip install -r requirements-examples.txt

cd examples

# Run a specific example (replace with the script you want to run)
python p530/p530_18_figure_3.py

# Once done running examples
deactivate
```

On Linux and macOS:
```bash
# Create the virtual environment in a folder named 'venv'
python3 -m venv venv

# Activate the environment
source venv/bin/activate

# Install packages needed for the examples
python -m pip install -r requirements-examples.txt

cd examples

# Run a specific example (replace with the script you want to run)
python p530/p530_18_figure_3.py

# Once done running examples
deactivate
```

On Linux, Matplotlib requires a system-level graphical backend to display plots. If plots fail to
show, make sure you have a backend installed. Tk is the standard default, it can be installed using
your system's package manager.

```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```
