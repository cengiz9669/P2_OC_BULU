
Titre projet 2 : Utilisez les bases de Python pour l'analyse de marché.

## Installation

### 1. Téléchargement du projet sur votre ordinateur

Clonez le repository

```bash
# git clone https://github.com/cengiz9669/P2_OC_BULU.git
```

Accédez au répertoire cloné.
```bash
cd P2_OC_BULU
```

### 2. Création d'un environnement virtuel 
Créez l'environnement virtuel env.
```bash
python3 -m venv env
```

### 3. Activation et installation de votre environnement virtuel 

Activez votre environnement virtuel env nouvellement créé.
```bash
source env/bin/activate
sous windows : env/Scripts/activate.bat
```

Installez les paquets présents dans la liste requirements.txt
```bash
pip install -r requirements.txt
```

## Utilisation

Lancer simplement le script python scraper.py présent à la source du dossier de travail.
```python
python scraper.py
```

## Résultat

Une fois le script exécuté, le résultat se trouvera dans le dossier Donnees_resultat/.
Vous y trouverez les fichiers CSV correspondant aux informations de tous les livres de chaque catégorie de livre présente sur le site https://books.toscrape.com/index.html.
Vous y trouverez également dans le sous-dossier Donnees_resultat/Couvertures/ les images de couverture de tous les livres présents sur le site.

