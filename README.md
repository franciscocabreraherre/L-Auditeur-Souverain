# Projet : L'Auditeur Souverain

Ce projet implémente un pipeline de gouvernance de données end-to-end pour le secteur énergétique français. Il utilise l'IA souveraine **Mistral** et la bibliothèque **Great Expectations** pour garantir la conformité des données de production électrique aux exigences de l'**EU AI Act**.

## Fiche Technique : Données et Objectifs

### Source des Données
* **Nom** : éCO2mix Régional (*Temps Réel*)
* **Producteur** : RTE (*Réseau de Transport d'Électricité*)
* **Portail** : ODRE (*Open Data Réseaux Énergies*)
* **Période cible** : Janvier 2025 - Décembre 2025
* **Note** : Les données ne sont pas versionnées dans ce dépôt. Le script situé dans le répertoire `src/scraper` permet une ingestion automatisée et vérifiée.

### Objectifs de l'Audit (IA Souveraine)
L'agent d'IA (Mistral) analyse le pipeline pour répondre aux exigences de l'Article 10 de l'EU AI Act (Gouvernance des données) :

1. **Vérification de la Complétude et des Biais**: L'IA valide que les filières énergétiques (*Solaire, Éolien, Nucléaire*) sont documentées sans omissions pour chaque région, évitant ainsi des modèles de prédiction biaisés géographiquement.
2. **Détection d'Outliers Critiques** : Identification des anomalies de mesure (*pics de consommation aberrants*) pouvant entraîner des erreurs de prédiction dans les systèmes de régulation du réseau, minimisant le risque de rupture d'approvisionnement.
3. **Audit de Souveraineté et Sécurité des Flux** : L'IA audite les métadonnées pour garantir que les données restent confinées dans l'environnement local (*PostgreSQL/Docker*). Elle vérifie qu'aucune donnée sensible ou identifiant d'infrastructure critique n'est exposé à des services tiers non souverains.

## Architecture Technique

* **IA** : Mistral AI (*Modèles via API sécurisée*).
* **Qualité** : Great Expectations (*Contrats de données*).
* **Stockage** : PostgreSQL (*Persistance locale*).
* **Infrastructure** : Docker (*Environnement conteneurisé multi-services*).

## Structure du Répertoire

```text
L-AUDITEUR-SOUVERAIN/
├── data/                        # Sources de données et documentation RTE
│   └── eco2mix_2025.csv         # Dataset principal (400k+ lignes)
├── docker/                      # Fichiers de build Docker
│   └── auditeur.dockerfile
├── notebooks/                   # Études et exploration de données
│   └── data_exploration.ipynb
├── src/
│   ├── auditor/                 # Tests et intégration IA
│   │   └── tester_mistral.py    # [Agentic] Intégration Mistral AI
│   ├── database/                # Configuration SQL et modèles
│   │   ├── database_setup.py
│   │   └── models.py
│   ├── processor/               # Cœur fonctionnel (ETL & Audit)
│   │   ├── ingestion_sql.py     # Tri et insertion massive
│   │   └── init_qualite.py      # Audit Great Expectations
│   └── scraper/                 # Scripts de récupération automatisée
├── .env                         # Secrets et configurations locales
├── docker-compose.yml           # Orchestration des conteneurs
├── main.py                      # Point d'entrée du pipeline
└── requirements.txt             # Dépendances du projet
```

## Guide d'installation (Docker)

Ce projet est entièrement conteneurisé pour garantir la reproductibilité de l'audit et de l'ingestion, indépendamment de l'hôte.  

### 1. Prérequis  
- **Docker** (v24.0+) et **Docker Compose** (v2.20+).  
- Le fichier de données `eco2mix_2025.csv` doit être présent dans le dossier `./data/` (*Note : le fichier `telecharger_donnees.py` dans le dossier `./src/scraper/` sert à télécharger ces données, l'étape 4 du guide montre comment l'utiliser.*)  

### 2. Configuration de l'environnement  
Créez un fichier `.env` à la racine du projet pour définir les paramètres de la base de données PostreSQL : 

```
POSTGRES_USER=admin
POSTGRES_PASSWORD=votre_mot_de_passe
POSTGRES_DB=audit_energie
DB_HOST=db_audit
DB_PORT=5432
```
Dans une future itération du projet une clé API pour Mistral sera nécessaire pour l'exécution du code intéragissant avec l'IA, donc vous pouvez dès maintenant créer cette clé et l'ajouter à votre `.env` sous la forme : 

```
MISTRAL_API_KEY=votre_cle
```  

### 3. Déploiement de l'infrastructure
Lancer les conteneurs en mode détaché : 
```bash
docker compose up -d --build
```

Cela construit l'image de l'Auditeur (via `.docker/auditeur.dockerfile`) et initialise deux services :  
- **db_audit** : une base de données PostgreSQL 15 avec stockage sur volume persistant.  
- **app_auditeur** : l'environnement Python contenant la logique d'audit et les dépendances.  

### 4. Obtention des données
Lancer le fichier de téléchargement des données avec la commande suivante :  
```bash
docker compose exec app_auditeur python src/scraper/telecharger_donnees.py
```  
Cela créera le fichier `eco2mix_2025.csv` dans le dossier `./src/data/`  

### 5. Lancement du pipeline  
Pour lancer le cycle complet (Audit -> Nettoyage -> Ingestion):  
```bash
docker compose exec app_auditeur python main.py
```

### 6. Verification des données  
Vous pouvez accéder au terminal PostgreSQL pour vérifier le volume des données
```bash
docker compose exec db_audit psql -U admin -d audit_energie -c "SELECT count(*) FROM production_energie;"
```
