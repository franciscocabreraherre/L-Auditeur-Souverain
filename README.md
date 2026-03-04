# L'Auditeur Souverain : Pipeline de Gouvernance Energetique

Ce projet implemente un pipeline de donnees end-to-end conforme a l'Article 10 de l'EU AI Act. Il assure l'ingestion massive, l'audit de qualite via Mistral AI et la visualisation souveraine des donnees de production electrique francaise.

## Etat du Projet (Mars 2026)
* Dashboard Interactif : Interface Streamlit permettant une analyse multi-mode (National, Regional, Comparaison) avec cartographie choroplethe integree.
* Audit Agentique Mistral : Analyse automatisee des rapports de qualite et stockage des verdicts de conformite au format JSON dans la table registre_audit_ia.
* Pipeline Haute Performance : Ingestion batch de ~500k lignes optimisee via SQLAlchemy.
* Gouvernance de Donnees : Separation stricte entre donnees validees (production_energie) et donnees en anomalie (production_quarantaine).

## Architecture Technique
* Interface : Streamlit et Plotly Express (Visualisation et Cartographie).
* Ingestion : Python / Pandas / SQLAlchemy.
* Qualite : Great Expectations (Contrats de donnees Article 10).
* IA : Agent Mistral (Analyse souveraine via API securisee).
* Base de donnees : PostgreSQL 15 (Dockerise) avec contraintes d'unicite et indexation.



## Guide d'Utilisation Rapide

### 1. Deploiement de l'infrastructure
Assurez-vous d'avoir un fichier .env configure, puis lancez les conteneurs :
```bash
docker compose up -d --build
```
### 2. Execution du Pipeline  
Pour lancer l'ingestion, les tests de qualite et l'audit Mistral :
```bash
docker compose exec app_auditeur python main.py
```
### 3. Consultation du Dashboard
L'interface de visualisation est accessible a l'adresse suivante :
http://localhost:8501

## Fiche Technique : Données et Objectifs

### Source des Données
* **Nom** : éCO2mix Régional (*Temps Réel*)
* **Producteur** : RTE (*Réseau de Transport d'Électricité*)
* **Portail** : ODRE (*Open Data Réseaux Énergies*)
* **Période cible** : A partir du 01/01/2025
* **Note** : Les données ne sont pas versionnées dans ce dépôt. Le script situé dans le répertoire `src/scraper` permet une ingestion automatisée et vérifiée.

### Objectif: Gouvernance et EU AI Act (Art. 10)

L'agent d'IA (Mistral) analyse le pipeline pour repondre aux exigences reglementaires :

1. **Représentativité** : Validation que les filieres energetiques (Solaire, Eolien, Nucleaire) sont documentees sans omissions regionales.  
2. **Précision technique** : Identification des anomalies de mesure (pics de consommation) pour minimiser les risques de regulation.

3. **Souverainete des flux** : Garantie que les donnees critiques restent confinees dans l'environnement local PostgreSQL/Docker.

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
├── src/
│   ├── database/        # modeles SQLAlchemy (production, quarantaine, audit)
│   ├── auditor/         # integration Mistral AI
│   └── processor/       # ETL et Great Expectations
├── app.py               # Dashboard Streamlit (Visualisation et Map)
├── main.py              # Point d'entree du pipeline
├── docker-compose.yml   # Orchestration des services (db_audit, app_auditeur)
└── requirements.txt     # Dependances (streamlit, plotly, sqlalchemy, etc.)
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

## Licence

Copyright (C) 2026 Francisco CABRERA HERRE.
Ce programme est un logiciel libre : vous pouvez le redistribuer et/ou le modifier selon les termes de la Licence Publique Generale Affero GNU (AGPL) telle que publiee par la Free Software Foundation, version 3 ou ulterieure.