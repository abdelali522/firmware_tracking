# Architecture générale du projet

## Objectif

Ce projet vise à créer un prototype local de blockchain pour enregistrer et contrôler les versions successives d'un firmware embarqué.

L'idée principale est de garantir que l'historique des versions reste fiable et qu'une modification ancienne puisse être détectée.

## Vue d'ensemble

Le système suit un modèle simple et pédagogique :

- un fichier firmware est reçu en entrée ;
- une version est ajoutée dans une chaîne de blocs ;
- chaque bloc contient des informations sur cette version ;
- chaque bloc est lié au précédent grâce à un hash ;
- la chaîne peut être vérifiée pour détecter toute altération.

## Composants principaux

### 1. Données d'entrée

Le système prend en charge les fichiers firmware qui doivent être tracés.

Pour chaque version, on conserve :

- le nom de la version ;
- la date d'enregistrement ;
- l'empreinte SHA-256 du fichier ;
- le hash du bloc précédent.

### 2. Bloc

Un bloc représente une version enregistrée.

Il contient notamment :

- un identifiant de position dans la chaîne ;
- une date et heure d'enregistrement ;
- le nom de la version ;
- le hash du firmware ;
- le hash du bloc précédent ;
- le hash du bloc courant.

### 3. Chaîne de blocs

La chaîne regroupe tous les blocs dans l'ordre chronologique.

Son rôle est de :

- ajouter de nouvelles versions ;
- conserver l'historique ;
- relier chaque bloc au précédent ;
- vérifier l'intégrité globale.

### 4. Vérification d'intégrité

Avant de considérer la chaîne comme valide, le système contrôle :

- que chaque bloc n'a pas été modifié ;
- que le hash calculé correspond bien au contenu ;
- que le hash précédent correspond au bloc antérieur.

Si un enregistrement ancien est altéré, la chaîne ne passe plus la vérification.

### 5. Persistance locale

Les données sont stockées localement sous forme de fichier JSON.

Cela permet :

- de conserver l'historique entre les exécutions ;
- de relire facilement les versions enregistrées ;
- de tester le fonctionnement sans infrastructure réseau.

### 6. Interface utilisateur

L'application expose une interface simple en ligne de commande.

Elle permet de :

- ajouter une version ;
- lister l'historique ;
- rechercher une version ;
- vérifier la chaîne ;
- simuler une modification pour voir où la rupture apparaît.

## Schéma conceptuel

```text
Fichier firmware
      |
      v
Ajout d'une version
      |
      v
Création d'un bloc
      |
      v
Calcul du hash SHA-256
      |
      v
Enregistrement dans la chaîne
      |
      v
Vérification du chaînage et de l'intégrité
```

## Principe de sécurité

Le système repose sur deux mécanismes simples mais efficaces :

- empreinte cryptographique du firmware ;
- chaînage des blocs à l'aide des hashes précédents.

Grâce à cela, une modification d'un ancien enregistrement modifie les données associées à ce bloc et rompt la cohérence de la chaîne.

## Conclusion

L'architecture générale du projet est celle d'une blockchain pédagogique locale :

- elle enregistre les versions de firmware ;
- elle sécurise leur historique ;
- elle détecte les altérations ;
- elle reste simple, lisible et facile à démontrer.
