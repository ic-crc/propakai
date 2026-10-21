[English](./README.md)

Pour installer les dépendances et générer la documentation HTML depuis un environnement virtuel,
utilisez les commandes suivantes depuis **le répertoire racine du projet**.

Sous Windows:
```bash
# Création d'un environnement virtuel sous le répertoire 'venv'
py -m venv venv

# Activation de l'environnement virtuel
.\venv\Scripts\activate

# Installation des paquets requis
python -m pip install -r requirements-docs.txt

# Générer et servir la documentation
zensical serve

# Une fois le travail sur la documentation terminé
deactivate
```


Sous Linux et macOS:
```bash
# Création d'un environnement virtuel sous le répertoire 'venv'
python3 -m venv venv

# Activation de l'environnement virtuel
source venv/bin/activate

# Installation des paquets requis
python -m pip install -r requirements-docs.txt

# Générer et servir la documentation
zensical serve

# Une fois le travail sur la documentation terminé
deactivate
```
