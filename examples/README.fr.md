[English](./README.md)

Pour installer les paquets nécessaires et rouler les exemples à partir d'un environnement
virtuel, veuillez utiliser les commandes ci-dessous depuis **le répertoire racine du projet**.

Sous Windows:
```bash
# Création d'un environnement virtuel sous le répertoire 'venv'
py -m venv venv

# Activation de l'environnement virtuel
.\venv\Scripts\activate

# Installation des paquets requis
python -m pip install -r requirements-examples.txt

cd examples

# Exécution d'un exemple spécifique (remplacer par l'exemple désiré)
python p530/p530_18_figure_3.py

# Une fois l'exécution des exemples terminée
deactivate
```

Sous Linux et macOS:
```bash
# Création d'un environnement virtuel sous le répertoire 'venv'
python3 -m venv venv

# Activation de l'environnement virtuel
source venv/bin/activate

# Installation des paquets requis
python -m pip install -r requirements-examples.txt

cd examples

# Exécution d'un exemple spécifique (remplacer par l'exemple désiré)
python p530/p530_18_figure_3.py

# Une fois l'exécution des exemples terminée
deactivate
```

Sous Linux, Matplotlib a besoin d'une interface graphique système (backend) pour l'affichage des
graphiques. En cas de problème d'affichage, vérifiez qu'une telle interface est installée.
L'interface par défaut est Tk ; elle s'installe via le gestionnaire de paquets de votre système.

```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```