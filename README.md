# Projet : L'Auditeur Souverain

Ce projet implémente un pipeline de gouvernance de données end-to-end pour le secteur énergétique français. Il utilise l'IA souveraine **Mistral** et la bibliothèque **Great Expectations** pour garantir la conformité des données de production électrique aux exigences de l'**EU AI Act** (Article 10).

## État du Projet (03 Mars 2026)
* **Pipeline Haute Performance** : Ingestion batch de ~500k lignes en moins de 3 minutes (optimisation des entrées/sorties SQL).
* **Audit Agentique Mistral** : Analyse automatisée des rapports de qualité et stockage des verdicts de conformité au format JSON.
* **Gouvernance de Données** : Séparation stricte entre données validées (`production_energie`) et données en anomalie (`production_quarantaine`).

## Architecture Technique
* **Ingestion** : Python / Pandas / SQLAlchemy.
* **Qualité** : Great Expectations (Contrats de données Article 10).
* **IA** : Agent Mistral (Analyse souveraine).
* **Base de données** : PostgreSQL 15 (Dockerisé).

## Guide d'Utilisation Rapide
1. **Lancer l'infrastructure** : `docker compose up -d --build`
2. **Exécuter le pipeline complet** : `docker compose exec app_auditeur python main.py`
3. **Consulter les rapports d'audit** : 
   ```bash
   docker compose exec db_audit psql -U admin -d audit_energie -c "SELECT * FROM registre_audit_ia ORDER BY date_audit DESC LIMIT 1;"
   ```

## Fiche Technique : Données et Objectifs

### Source des Données
* **Nom** : éCO2mix Régional (*Temps Réel*)
* **Producteur** : RTE (*Réseau de Transport d'Électricité*)
* **Portail** : ODRE (*Open Data Réseaux Énergies*)
* **Période cible** : A partir du 01/01/2025
* **Note** : Les données ne sont pas versionnées dans ce dépôt. Le script situé dans le répertoire `src/scraper` permet une ingestion automatisée et vérifiée.

## Strategie de mise a jour des donnees

Le pipeline utilise desormais une approche incrementale pour l'acquisition des donnees via l'API ODRE (Réseaux Énergies). 

1. **Initialisation** : Lors de la premiere execution, le systeme telecharge l'integralite des donnees pour l'annee 2025.
2. **Incrementation** : Les executions suivantes interrogent la base de donnees pour identifier le dernier horodatage (`MAX date_heure`). 
3. **Filtrage API** : Seules les donnees posterieures a cet horodatage sont requetees aupres de l'API RTE, minimisant la consommation de bande passante et les ressources de calcul.
4. **Securité** : Une verification de doublons (`drop_duplicates`) est effectuee en memoire avant l'insertion pour garantir l'integrite referentielle en cas de reponse API chevauchante.

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
│   └── delta_update.csv         # Dataset principal (400k+ lignes)
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
- Un compte sur le portail ODRE pour obtenir une `ODRE_API_KEY` (optionnel mais recommande).

### 2. Configuration de l'environnement  
Créez un fichier `.env` à la racine du projet pour définir les paramètres de la base de données PostreSQL : 

```
POSTGRES_USER=admin
POSTGRES_PASSWORD=votre_mot_de_passe
POSTGRES_DB=audit_energie
DB_HOST=db_audit
DB_PORT=5432
ODRE_API_KEY=votre_cle
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

### 4. Ingestion et Mise a jour des donnees
Le projet ne contient pas de donnees pre-installees. Pour initialiser ou mettre a jour la base de donnees, executez le pipeline principal :
```bash
docker compose exec app_auditeur python main.py
```

### 5. Verification des données  
Vous pouvez accéder au terminal PostgreSQL pour vérifier le volume des données
```bash
docker compose exec db_audit psql -U admin -d audit_energie -c "SELECT count(*) FROM production_energie;"
```
