# Traçabilité des versions de firmware par une blockchain pédagogique

## 1. Contexte et objectif

Ce projet implémente un prototype local de blockchain en Python pour enregistrer et vérifier les versions successives d'un firmware embarqué. L'objectif est de garantir l'intégrité de l'historique des versions et de détecter toute modification sur un ancien enregistrement.

Le prototype suit exactement le cahier des charges du projet :

- enregistrer une nouvelle version à partir d'un fichier firmware ;
- conserver la liste chronologique des versions ;
- calculer l'empreinte SHA-256 du fichier ;
- relier chaque bloc au précédent grâce à un hash de chaîne ;
- vérifier la validité globale de la blockchain ;
- simuler une altération pour montrer où l'intégrité est rompue.

Le projet est volontairement pédagogique et local. Il ne met pas en œuvre de réseau distribué, de consensus ou de minage.

## 2. Architecture logicielle

### 2.1 Vue d'ensemble

L'architecture est organisée en quatre couches :

1. Couche d'entrée des données
   - réception du fichier firmware à partir du système de fichiers ;
   - récupération du nom de version et de la date d'enregistrement.

2. Couche métier / blockchain
   - représentation du bloc : index, horodatage, nom de version, hash du firmware, hash précédent, hash du bloc ;
   - gestion de la chaîne : ajout, recherche, vérification, détection d'altération.

3. Couche de persistance
   - stockage JSON local dans le dossier `data/` ;
   - les blocs sont sérialisés afin de conserver l'historique entre exécutions.

4. Couche interface utilisateur
   - interface CLI Python (`app.py`) pour ajouter, lister, rechercher, vérifier et simuler une corruption.

### 2.2 Composants principaux

#### Bloc (`Block`)
Le bloc contient toutes les informations nécessaires pour identifier une version donnée :

- `index` : position dans la chaîne ;
- `timestamp` : date et heure de création au format ISO 8601 ;
- `version_name` : libellé de la version ;
- `firmware_hash` : empreinte SHA-256 du fichier firmware ;
- `previous_hash` : hash du bloc précédent ;
- `hash` : hash calculé à partir du contenu du bloc.

Le hash d'un bloc est calculé selon le principe suivant :

- concaténer les champs structurants du bloc ;
- sérialiser les données au format JSON ;
- appliquer `sha256(...)` ;
- stocker le résultat dans le champ `hash`.

Si un seul champ change, le hash du bloc change aussi. Cela permet de détecter automatiquement toute modification non autorisée.

#### Chaîne (`Blockchain`)
La chaîne gère la liste de blocs et les opérations de sécurité :

- `add_version(version_name, firmware_path)` : ajoute un nouveau bloc ;
- `find_version(value)` : recherche une version par nom ou par index ;
- `list_versions()` : renvoie l'historique complet ;
- `verify_chain()` : contrôle le chaînage et les empreintes ;
- `tamper_block(version_name)` : simule une modification pour tester la détection d'intégrité.

Le chaînage est strict : chaque bloc contient le hash du bloc précédent. Si un ancien enregistrement est modifié, le hash suivant reste lié à l'ancien hash et la vérification signale la rupture.

#### Persistance (`data/firmware_chain.json`)
Chaque mise à jour est enregistrée dans le fichier JSON local :

- les blocs sont écrits sous forme de liste JSON ;
- la chaîne est rechargée automatiquement au démarrage ;
- les données restent visibles et exploitables sans nécessiter un réseau.

#### Interface CLI (`app.py`)
L'application expose une interface en ligne de commande simple :

- `add-version` : enregistre une nouvelle version de firmware ;
- `list` : affiche l'historique des versions ;
- `search` : recherche une version par nom ou index ;
- `verify` : vérifie la validité complète de la chaîne ;
- `tamper` : simule une modification d'un bloc pour valider la détection d'erreur.

## 3. Flux de fonctionnement

### 3.1 Ajout d'une version

1. Le programme reçoit le chemin d'un fichier firmware.
2. L'empreinte SHA-256 du fichier est calculée.
3. Le nom de version et la date sont ajoutés au bloc.
4. Le bloc reçoit le hash du bloc précédent.
5. Le hash du bloc courant est calculé.
6. Le bloc est ajouté à la chaîne et sauvegardé dans le fichier JSON.

Exemple de séquence :

```
Utilisateur -> app.py add-version --name v1.0 firmware.bin
app.py -> Blockchain.add_version()
Blockchain -> SHA-256(firmware.bin)
Blockchain -> génération du bloc n°0
Blockchain -> sauvegarde dans data/firmware_chain.json
```

### 3.2 Vérification de l'intégrité

1. Le programme parcourt tous les blocs de la chaîne.
2. Pour chaque bloc, il recalcul le hash à partir du contenu courant.
3. Il compare ce hash avec le hash enregistré.
4. Il vérifie ensuite que le `previous_hash` du bloc correspond bien au hash du bloc précédent.
5. S'il trouve une incohérence, il renvoie la position du bloc et la raison de la rupture.

### 3.3 Simulation d'altération

1. Le programme sélectionne une version enregistrée.
2. Il modifie un caractère de l'empreinte du firmware dans le bloc sélectionné.
3. Il recalcul le hash du bloc modifié.
4. La vérification de la chaîne détecte immédiatement l'incohérence.
5. Le bloc cassé est identifié et affiché.

## 4. Structure du projet

```text
blockchain/
├── README.md
├── app.py
├── firmware_blockchain.py
├── data/
│   └── firmware_chain.json
├── tests/
│   └── test_firmware_blockchain.py
└── firmware_examples/
    └── (fichiers de test ou binaires de démonstration)
```

## 5. Règles de conception

- simplicité pédagogique ;
- zéro dépendance externe ;
- stockage local et lisible en JSON ;
- validation explicite des blocs ;
- interface de démonstration facile à utiliser en ligne de commande.

## 6. Démonstration attendue

Le projet est pensé pour démontrer le scénario suivant :

1. enregistrer trois versions de test ;
2. vérifier la chaîne ;
3. modifier artificiellement un ancien enregistrement ;
4. relancer la vérification ;
5. afficher le bloc où l'intégrité est rompue.

Cette démonstration correspond exactement au besoin métier décrit dans le projet : garantir la trace d'une évolution de firmware tout en détectant une altération dans son historique.

## 7. Exemples d'utilisation

### Ajouter une version

```bash
python app.py --storage data/firmware_chain.json add-version firmware_v1.bin --name v1.0
python app.py --storage data/firmware_chain.json add-version firmware_v2.bin --name v2.0
python app.py --storage data/firmware_chain.json add-version firmware_v3.bin --name v3.0
```

### Lister les versions

```bash
python app.py --storage data/firmware_chain.json list
```

### Rechercher une version

```bash
python app.py --storage data/firmware_chain.json search v2.0
```

### Vérifier la chaîne

```bash
python app.py --storage data/firmware_chain.json verify
```

### Simuler une corruption

```bash
python app.py --storage data/firmware_chain.json tamper v1.0
```

La commande de corruption doit provoquer un échec de validation lors du prochain appel à `verify`.

## 8. Conclusion

Cette architecture crée un prototype de blockchain pédagogique, simple mais conforme aux exigences du cahier des charges : 

- historiques de versions ;
- intégrité par empreintes et chaînage ;
- détection d'altération ;
- démonstration locale et facile à exécuter.

Le code est volontairement lisible afin de servir de support pédagogique et de base de travail pour une évolution future vers des fonctionnalités plus avancées.
# firmware_tracking
