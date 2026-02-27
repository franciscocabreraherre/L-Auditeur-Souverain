# Copyright (C) 2026 Francisco CABRERA HERRE
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU Affero General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.

import great_expectations as gx
import pandas as pd
import os
import sys


def initialiser_audit_qualite():
    """
    Initialisation de la validation de la qualité des données avec Great Expectations.
    """
    ## ==============================================================
    ## PARTIE 1 : CONFIGURATION DE GREAT EXPECTATIONS
    ## ==============================================================
    
    # Créer un DataContext éphémère
    context = gx.get_context() 
    
    # Ajouter les données à valider au contexte
    chemin_csv = os.path.join("/app", "data", "eco2mix_2025.csv")  # Chemin vers le fichier CSV téléchargé précédemment, mais pointé vers le chemin dans le conteneur Docker

    if not os.path.exists(chemin_csv):
        print(f"Erreur : Le fichier de données n'a pas été trouvé à l'emplacement attendu : {chemin_csv}")
        sys.exit(1)
    
    # On crée un dataframe pour réaliser l'insertion vers sql plus tard
    df = pd.read_csv(chemin_csv, sep=';')
    
    # Définition de la source de données dans Great Expectations
    nom_source = "source_rte_2025"
    nom_asset = "asset_eco2mix"

    # Configuration du connecteur pour lire le CSV
    datasource = context.data_sources.add_pandas(name=nom_source) 
    asset = datasource.add_csv_asset(name=nom_asset, filepath_or_buffer=chemin_csv, sep=';')

    # Créer une suite d'attentes
    nom_suite = "suite_qualite_donnees"
    suite = gx.ExpectationSuite(name=nom_suite)
    suite = context.suites.add(suite)

    ## ==============================================================
    ## PARTIE 2 : RÉGLES DE VALIDATION (Art 10 EU IA Act)
    ## ==============================================================
    
    ## Note : Les règles suivantes sont basées sur les critères de qualité des données définis dans l'article 10 du Règlement sur l'Intelligence Artificielle de l'UE, adaptés au contexte des données énergétiques régionales.

    # 1- Intégrité du schéma (vérifier que les colonnes attendues sont présentes)
    colonnes_critiques = ["libelle_region", "date_heure", "consommation", "nucleaire", "eolien", "solaire"]
    for col in colonnes_critiques:
        suite.add_expectation(gx.expectations.ExpectColumnToExist(column=col))

    # 2- Completude (données manquantes)
    # Ex: une donnée sans date ou localisation n'est pas exploitable
    suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="date_heure"))
    suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="libelle_region"))
    
    # 3- Cohérence physique et données aberrantes
    # Ex: une consommation négative est un indicateur d'erreur
    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(
        column="consommation", 
        min_value=0, 
        max_value=25000  
        # Seuil base sur les records historiques par region
        # Note : historiquement, la consommation maximale observée pour une région donnée est d'environ 14000-15000 MW, mais nous appliquons une marge de sécurité pour détecter les anomalies grossières (ex: 25000 MW serait clairement anormal pour une région française).
    ))
    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(
        column="nucleaire", 
        min_value=0, 
        max_value=15000
    ))
    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(
        column="eolien", 
        min_value=0, 
        max_value=10000
    ))
    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(
        column="solaire", 
        min_value=0, 
        max_value=8000
    ))
    # Note : les seuils pour le nucléaire, l'éolien et le solaire sont basés sur les capacités de production maximales historiques par région, avec une marge de sécurité pour détecter les anomalies.

    # 4. Formatage Temporel (Standard ISO 8601)
    suite.add_expectation(gx.expectations.ExpectColumnValuesToMatchRegex(
        column="date_heure",
        regex=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:?\d{2}$"
    ))

    ## ==============================================================
    ## PARTIE 3 : VALIDATION ET RESULTATS
    ## ==============================================================

    # Exécuter la validation via une Validation Definition
    definition_nom = "validation_eco2mix_2025"
    batch_definition = asset.add_batch_definition_whole_dataframe(name="batch_integral_2025")

    validation_definition = context.validation_definitions.add(
        gx.ValidationDefinition(
            name=definition_nom,
            data=batch_definition,
            suite=suite
        )
    )
    
    # Lancement de l'audit
    resultat = validation_definition.run(result_format="COMPLETE")
    # Le flag "COMPLETE" sert à obtenir un champ avec l'index de toutes les 
    # lignes qui ont échoué à au moins une règle, ce qui nous permettra 
    # de les diriger vers la table de quarantaine lors de l'ingestion.

    if resultat.success:
        print("Statut : Donnees conformes aux exigences de l'Article 10 EU AI Act.")
    else:
        print("Statut : Anomalies detectees. Audit de qualite rejete.")
        print(f"Taux de succes : {resultat.statistics['success_percent']}%")

    return df, resultat

if __name__ == "__main__":
    initialiser_audit_qualite()
