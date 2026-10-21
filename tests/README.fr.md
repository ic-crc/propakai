[English](./README.md)

Pour installer les paquets nécessaires et rouler les tests à partir d'un environnment virtuel,
veuillez utiliser les commandes ci-dessous depuis **le répertoire racine du projet**.

Notez que l'exécution des tests active le téléchargement de multiple fichiers de l'UIT (e.g.
cartes digitales, statistiques, etc.) lorsqu'ils ne sont pas déjà présents localement. Certains
tests utilisent des données statistiques mensuelles nécessitant le téléchargement de plusieurs Go
de données lorsqu'exécutés pour la première fois. Conséquemment, ces tests sont exclus par défaut
mais peuvent néanmoins être activés à l'aide d'unve variable d'environnment (NO_SKIP) si désiré.

Sous Windows:
```bash
py -m venv venv

.\venv\Scripts\activate

python -m pip install -r requirements-tests.txt

cd tests

# Pour exécuter les tests habituels
python -m unittest discover -s "tests"

# Pour exécuter tous les tests
set NO_SKIP=1 && python -m unittest discover -s "tests"

deactivate
```

Sous Linux et macOS:
```bash
python3 -m venv ../venv

source venv/bin/activate

python -m pip install -r requirements-tests.txt

cd tests

# Pour exécuter les tests habituels
python -m unittest discover -s "tests"

# Pour exécuter tous les tests
NO_SKIP=1 python -m unittest discover -s "tests"

deactivate
```
