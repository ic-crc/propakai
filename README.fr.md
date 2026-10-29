<p align="center">
  <img src="docs/assets/propakai_logo_name.png" alt="Project Logo" width="250"/>
</p>

#

[English](./README.md)

PropaKai est un paquet Python pour implémentations de recommandations UIT-R P.

Ces recommandations, élaborées par le Groupe d’étude 3 du Secteur des radiocommunications de
l’Union internationale des télécommunications (UIT-R), fournissent des normes et méthodes
internationales pour la prévision de la propagation des ondes radio.

#### Avertissement
> Ce projet, PropaKai, est une implémentation logicielle indépendante et
tierce de certaines recommandations ITU-R P. Ce projet n’est pas affilié, maintenu, autorisé,
sponsorisé ni d’aucune manière officiellement lié à l’Union internationale des télécommunications
(UIT). Toute utilisation des acronymes « UIT » et « ITU » est faite uniquement à des fins
descriptives et d’identification. Pour les textes et normes officiels, les utilisateurs doivent se
référer directement au site officiel de l’UIT ([www.itu.int](www.itu.int)).


## Installation

Pour installer ou mettre à jour PropaKai sur votre système, veuillez télécharger le fichier wheel
**(.whl)** depuis la page [Releases](https://github.com/ic-crc/propakai/releases).

À partir du répertoire contenant le fichier .whl, installez le paquet à l'aide de la commande
suivante:

```bash
# Remplacez x.y.z par le numéro de version actuel.
# Omettez "[full]" pour une installation minimale incluant seulement les dépendances essentielles.
python -m pip install propakai-x.y.z-py3-none-any.whl[full]
```
_Remarque : selon votre système, il peut être nécessaire d’utiliser la commande `py` sous Windows
ou `python3` sous macOS/Linux à la place de `python`._


## Exemple

Voici un petit exemple de code utilisant PropaKai:
```python
from propakai import p1511_3 as p1511

if __name__ == '__main__':

    # Le premier appel à topographic_height() téléchargera et installera
    # la carte numérique UIT contenant les données d’altitude topographique.
    # Tout appel suivant réutilisera le fichier de carte numérique installé.
    altitude_topo_m = p1511.topographic_height(lat=45.0, lon=-75.0)

    print(f'Altitude topographique: {altitude_topo_m:.1f} m')
```


## Documentation de l’API

https://ic-crc.github.io/propakai/


## Désinstallation

Pour désinstaller le paquet:
```bash
# Cette commande supprimera toute carte numérique ou autre fichier de données UIT
# ayant été installés par PropaKai.
propakai-data-cleanup

python -m pip uninstall propakai
```
_Remarque: au lieu d'utiliser `propakai-data-cleanup`, vous pouvez aussi utiliser `propakai-info`
afin d'obtenir le chemin d’installation des fichiers de données UIT, puis effectuer la suppression
manuellement selon vos besoins._


## Implémentations Inclues

[Recommandations](https://www.itu.int/rec/R-REC-P/fr) entièrement ou substantiellement implémentées:

- **UIT-R P.368-10:** Méthode de prévision de la propagation de l'onde de sol entre 10 kHz et 30
MHz.
- **UIT-R P.452-18:** Méthode de prévision pour évaluer les brouillages entre stations situées à la
surface de la Terre à des fréquences supérieures à 100 MHz environ.  _(exclue la prévision des
brouillages dus à la diffusion par les hydrométéores)_
- **UIT-R P.528-5**: Méthode de prévision de la propagation dans les bandes d'ondes métriques,
décimétriques et centimétriques pour le service mobile aéronautique et le service de radionavigation
aéronautique.
- **UIT-R P.676-13:** Affaiblissement dû aux gaz de l'atmosphère et effets associés.
- **UIT-R P.835-7:** Atmosphère de référence. _(exclue l'Annexe 3)_
- **UIT-R P.837-8:** Caractéristiques des précipitations pour la modélisation de la propagation. _(exclue l'Annexe 2)_
- **UIT-R P.838-3:** Modèle d'affaiblissement linéique dû à la pluie destiné aux méthodes de
prévision.
- **UIT-R P.839-4:** Modèle d'altitude de pluie pour les méthodes de prévision.
- **UIT-R P.840-9:** Affaiblissement dû aux nuages et au brouillard.
- **UIT-R P.1510-1:** Température moyenne de surface.
- **UIT-R P.1511-3:** Topographie pour la modélisation de la propagation Terre-espace.
- **UIT-R P.1546-6:** Méthode de prévision de la propagation point à zone pour les services de Terre
entre 30 MHz et 4 000 MHz.
- **UIT-R P.1812-8:** Méthode de prévision de la propagation fondée sur le trajet pour les services
de Terre point à zone dans la gamme de fréquences comprises entre 30 MHz et 6 GHz.
- **UIT-R P.2001-6:** Modèle général de large portée pour la propagation sur des trajets de Terre
dans la gamme des fréquences comprises entre 30 MHz et 50 GHz.
- **UIT-R P.2108-1:** Prévision de l'affaiblissement dû à des groupes d'obstacles.
- **UIT-R P.2109-2:** Prévision de l'affaiblissement dû à la pénétration dans les bâtiments.
- **UIT-R P.2145-0:** Cartes numériques relatives au calcul de l'affaiblissement dû aux gaz et
effets associés.
- **UIT-R P.2148-0:** Cartes numériques relatives aux statistiques sur la vitesse du vent de
surface.

Recommandations partiellement implémentées:

- **UIT-R P.530-18:** Données de propagation et méthodes de prévision nécessaires pour la conception
de faisceaux hertziens à visibilité directe de Terre.
- **UIT-R P.618-14:** Données de propagation et méthodes de prévision nécessaires pour la conception
de systèmes de télécommunication Terre-espace.
- **UIT-R P.619-6:** Données sur la propagation nécessaires à l'évaluation des brouillages entre des
stations dans l'espace et des stations situées à la surface de la Terre.
- **UIT-R P.681-11:** Données de propagation nécessaires pour la conception de systèmes du service
mobile terrestre par satellite.
- **UIT-R P.1411-13:** Données de propagation et méthodes de prévision pour la planification de
systèmes de radiocommunication, à courte portée, destinés à fonctionner à l'extérieur de bâtiments
et de réseaux locaux hertziens dans la gamme de fréquences comprises entre 300 MHz et 300 GHz.

Autres:

- Le sous-paquet `propakai.geo_catalog` facilite l'accès au [catalogue géospatial de
l’UIT-R](https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/).
- Le sous-paquet `propakai.extras` comprend des outils additionnels pour l’utilisation des
recommandations. par exemple pour l'extraction de profils de terrain.


## Concepts Clés

Voici quelques concepts clés qui ont été pris en compte lors du design et du développement
de PropaKai.

- Les différentes recommandations de l'UIT ne sont pas toujours mises à jour simultanément. Il
arrive parfois qu'une recommandation A soit modifiée alors qu'une recommandation B reste inchangée
et continue de se référer à une version antérieure de A. Afin d'éviter toute confusion ou tout
problème de codage inhérent, PropaKai a été **conçu de façon à prendre en charge plusieurs
versions d’une même recommandation**.

- Les fichiers de données de l’UIT (tels que les cartes numériques et les statistiques) ne peuvent
être redistribués. Pour en faciliter l’usage tout en respectant les conditions d’utilisation de
l’UIT, PropaKai **télécharge et sauvegarde automatiquement** ces fichiers, au besoin. Ces
téléchargements ont été autorisés par l'UIT, sous réserve du respect des conditions suivantes :
  - Les liens de téléchargement depuis le site de l’UIT sont affichés à l’utilisateur.
  - Un avis informe l’utilisateur que ces fichiers sont destinés à un usage personnel uniquement.
  - Les fichiers ne doivent pas être modifiés après le téléchargement.

- Les implémentations en Python sont pratiques et peuvent être facilement utilisées sur de
nombreuses plateformes. Cependant, l'utilisation d’autres langages de programmation peut parfois
être nécessaire afin d'obtenir de meilleures performances d’exécution. PropaKai **permet la
cohabitation de différentes implémentations d’une même recommandation en Python et en C/C++**, à
condition d'inclure les liaisons Python appropriées. Par exemple, un module Python implémentant la
recommandation UIT-R P.2109-2 porterait le nom `p2109_2`, tandis qu’un module nommé `p2109_2_dso`
indiquerait l'utilisation sous-jacente d'un object partagé dynamique (dynamic shared object, ou
DSO en anglais) d'un langage de programmation compilé. Le ou la programmeur·se peut alors choisir
d’utiliser l’un ou l’autre, ou bien les deux selon ses besoins.

- **Chaque fonction est documentée en indiquant la section ou sous-section correspondante** de la
recommandation de référence. Les paramètres des fonctions reprennent généralement les noms de
variables utilisés dans les recommandations, tout en respectant la convention de nommage Python
(snake_case).

- Lorsque disponibles, **les fichiers de validation de l’UIT sont utilisés afin de vérifier la
conformité des implémentations**.

- PropaKai a été **conçu pour être sûr en contexte multithread (thread-safe)**. Dans la mesure du
possible, les recommandations sont implémentées sous forme de fonctions pures, c’est-à-dire
qu’elles ne dépendent que de leurs paramètres d’entrée et n’utilisent ni état externe ni variable
globale. Cette approche les rend naturellement adaptées à une utilisation parallèle. Lorsque cette
approche n’est pas possible ou souhaitable (par exemple lors du téléchargement ou du chargement de
fichiers de données en mémoire), PropaKai gère ces situations de façon à garantir la sécurité
d’exécution en multithread.

  <details>
  <summary>Notes sur la concurrence en Python : Threads vs. Processus</summary>

  >**CPython Standard (Majorité des utilisateurs):**  
  >_Dans la version standard de CPython, un mécanisme connu sous le nom de Verrou d'Interpréteur
  Global (GIL) empêche plusieurs threads de s'exécuter sur plus d'un cœur de processeur (CPU) à la
  fois. Par conséquent, le multithreading n’apporte pas de bénéfices pour les tâches intensives en
  calcul. Pour obtenir un véritable parallélisme, il est recommandé d’utiliser le multiprocessing
  (plutôt que le multithreading). Comme pour la plupart des packages Python, le multiprocessing
  fonctionne sans difficulté avec PropaKai, puisque chaque processus dispose de son propre ensemble
  indépendant de variables de module._
  >
  >**Experimental Free-Threaded CPython (Python 3.13+):**  
  >_Depuis Python 3.13, une alternative expérimentale est disponible. Il est maintenant possible
  d'installer une version spéciale de CPython, dite "free-threaded", qui est compilée sans le GIL.
  Il s'agit d'un interpréteur Python distinct. Bien qu'il s'agisse actuellement d'une installation
  optionnelle, l'objectif à long terme de l'équipe de développement principale de Python est que ce
  mode "free-threaded" devienne la version par défaut à terme. Si vous exécutez PropaKai avec l'une
  de ces versions spécifiques, le multithreading peut apporter des accélérations significatives pour
  les tâches intensives en calcul._

</details>

- **Les contributions sont bienvenues !** Nul besoin d’implémenter une recommandation complète pour
participer : même l’ajout d’une petite partie peut être utile à d’autres utilisateurs. Le projet
actuel contient à la fois des implémentations complètes ou presque complètes, ainsi que d’autres où
seule une petite fraction a été complétée.


### Paroles de Sagesse

> _« Propagation, pas formules seulement. Propagation, leçon pour toute la science. Onde avoir
équilibre, tout va mieux. »_
>
> — M. Miyagi (probablement)