# Projet : L'Auditeur Souverain

Ce projet implémente un pipeline de gouvernance de données end-to-end pour le secteur énergétique français. Il utilise l'IA souveraine Mistral et la bibliothèque Great Expectations pour garantir la conformité des données de production électrique aux exigences de l'EU AI Act.

## Fiche Technique : Données et Objectifs

### Source des Données
* **Nom** : éCO2mix Régional (Temps Réel)
* **Producteur** : RTE (Réseau de Transport d'Électricité)
* **Portail** : ODRE (Open Data Réseaux Énergies)
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
├── data/           # Fichiers de données locaux (exclus du versioning)
├── docker/         # Fichiers de configuration Docker
├── notebooks/      # Analyses exploratoires
├── src/            # Code source modulaire
│   ├── app/        # Interface utilisateur
│   ├── auditor/    # Logique d'IA et conformité
│   ├── processor/  # Traitement et validation
│   └── scraper/    # Ingestion des données
├── .env            # Variables d'environnement (secrets, exclus du versioning)
├── .gitignore      # Définition des fichiers à ignorer
├── docker-compose.yml
└── requirements
```
