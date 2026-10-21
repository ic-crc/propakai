[English](./README.md)

## Compilation des fichiers de bibliothèque dynamique

Des fichiers de bibliothèque dynamique pour Windows (.dll), Linux (.so) et macOS (.dylib) sont
inclus dans les roues Python disponibles depuis la page
[Releases](https://github.com/mplussier/itupropag-sandbox/releases).

Si vous le souhaitez, vous pouvez compiler les bibliothèques manuellement en suivant les étapes
ci-dessous.


### Sous Windows

Sous Windows, les fichiers *.dll fournis sont présentement générés à l'aide de
[MSYS2](https://www.msys2.org/). Après avoir complété la procédure d'installation fournie sur le
site web de MSYS2, installez la suite d'outils suivante à partir de l'invite de commandes MSYS2
UCRT64:
```
pacman -S mingw-w64-ucrt-x86_64-toolchain
```

Optionnellement, ouvrez une invite de commandes Windows en mode Administrateur et créez un lien
symbolique pour la commande `make` (_modifiez les répertoires ci-dessous pour qu'ils correspondent
à votre installation_):
```
mklink C:\msys64\ucrt64\bin\make.exe C:\msys64\ucrt64\bin\mingw32-make.exe
```

À partir de l'invite de commandes MSYS2 UCRT64, utilisez la commande `make` ou `mingw32-make` de
l'un des répertoires contenant un fichier Makefile pour générer le(s) fichier(s) de bibliothèque
dynamique (.dll) correspondant:
```
# si vous avez créé le lien symbolique à l'étape précédente
make rebuild

# autrement
mingw32-make rebuild
```
Les fichiers de bibliothèque sont copiés automatiquement dans le répertoire `propakai/bin` (relatif
à la racine du dépôt) dans le cadre de la compilation.

Remarque: Les étapes décrites ci-dessus s’appliquent à Windows x86_64 (Intel/AMD 64 bits). Sur
Windows ARM64, il est possible de générer les DLLs de façon similaire, en utilisant `clang++`
depuis l’environnement CLANGARM64 de MSYS2, ce qui produira des binaires natifs pour ARM64.

Remarque: Assurez-vous de [mettre à jour votre installation de MSYS2](https://www.msys2.org/docs/updating/)
de temps à autre en invoquant la commande `pacman -Suy` à **deux** reprises à partir de l'invite
de commandes MSYS2 MSYS.


### Sous Linux et macOS

Sous Linux et macOS, vous pouvez utiliser les outils de compilation en ligne de commande standards
(la suite d’outils GNU sous Linux, les outils en ligne de commande Xcode sous macOS) pour le
processus de compilation.

Remarque: Sous macOS, assurez-vous que les outils Xcode soient installés. Si ce n’est pas le cas,
exécutez: `code-select --install`.

Utilisez la commande `make` dans l’un des répertoires contenant un fichier Makefile pour construire
le(s) fichier(s) de bibliothèque dynamique correspondant (.so sous Linux, .dylib sous macOS):
```
make rebuild
```
Les fichiers de bibliothèque sont copiés automatiquement dans le répertoire `propakai/bin` (relatif
à la racine du dépôt) dans le cadre de la compilation.

### Procédure de compilation alternative (Windows, Linux et macOS)

Les fichiers de bibliothèque dynamique (.dll, .so, .dylib) peuvent également être compilés en
utilisant [Zig](https://ziglang.org/download/) (version 0.16.0 ou ultérieure), qui prend en charge
la compilation croisée vers plusieurs plateformes à partir d'une seule machine hôte.

Une fois Zig installé, exécutez la commande suivante depuis l'un des répertoires contenant un
fichier `build.zig`:
```
zig build
```
Les fichiers de bibliothèque sont copiés automatiquement dans le répertoire `propakai/bin` (relatif
à la racine du dépôt) dans le cadre de la compilation.

Remarque: Toutes les plateformes cibles sont compilées par défaut, indépendamment du système
d'exploitation hôte. Aucun SDK ou chaîne d'outils supplémentaire n'est requis.
