# Copyright (C) 2026 Francisco CABRERA HERRE
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU Affero General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.

from src.database.database_setup import SessionLocal
from src.database.models import production_energie, production_quarantaine, registre_audit_ia
import pandas as pd
import datetime
from tqdm import tqdm


def executer_ingestion_systeme(df, resultat_audit, nom_fichier):
    db = SessionLocal()
    
    # Pour identifier les lignes avec erreur d'audit
    indices_erreurs = set()
    # Note : 'set' est utilisé pour éviter les doublons d'indices
    # si une ligne échoue à plusieurs règles de validation.
    for res in resultat_audit.results:
        if not res.success:
            indices = res.result.get('unexpected_index_list', [])
            indices_erreurs.update(indices)
    
    # Nettoyage des doublons potentiels dans le DataFrame avant l'insertion
    # à cause du changement d'heure été/hiver + contraint d'unicité sur 
    # (région, date_heure) dans la base de données
    nb_avant = len(df)
    # On garde la première occurrence en cas de doublon sur le couple (région, date)
    df = df.drop_duplicates(subset=['libelle_region', 'date_heure'], keep='first')
    df = df.reset_index(drop=True)
    
    nb_apres = len(df)
    if nb_avant != nb_apres:
        print(f"/!\ Nettoyage : {nb_avant - nb_apres} lignes en doublon supprimées. /!\ ")

    try:
        objets_clean = []
        objets_quarantaine = []

        df_reset = df.reset_index(drop=True)

        # On parcourt le DataFrame Pandas ligne par ligne
        for index, row in tqdm(df_reset.iterrows(), total=len(df), desc="Tri des données", unit="ligne"):
            # Préparation des données (on gère les NaT/NaN pour SQL)
            data_fields = {
                "libelle_region": str(row['libelle_region']),
                "date_heure": pd.to_datetime(row['date_heure']),
                "consommation": float(row['consommation']) if pd.notnull(row['consommation']) else 0,
                "nucleaire": float(row['nucleaire']) if pd.notnull(row['nucleaire']) else 0,
                "eolien": float(row['eolien']) if pd.notnull(row['eolien']) else 0,
                "solaire": float(row['solaire']) if pd.notnull(row['solaire']) else 0
            }

            if index in indices_erreurs:
                objets_quarantaine.append(production_quarantaine(**data_fields, erreur_log="Échec validation audit"))
            else:
                objets_clean.append(production_energie(**data_fields))

        # Insertion massive
        print(f"\nFinalisation : Insertion des {len(df)} lignes dans PostgreSQL...")
        db.add_all(objets_clean)
        db.add_all(objets_quarantaine)
        
        # Log de l'audit
        stats = resultat_audit.statistics
        
        audit_log = registre_audit_ia(
            date_audit=datetime.datetime.now(datetime.timezone.utc),
            nom_fichier=nom_fichier,
            taux_succes=stats['success_percent'],
            nb_lignes_ignorees=len(objets_quarantaine),
            conformite_statut=resultat_audit.success
        )
        db.add(audit_log)

        # Commit de la transaction
        db.commit()
        print(f"Succès : {len(objets_clean)} lignes validées, {len(objets_quarantaine)} en quarantaine.")

    except Exception as e:
        db.rollback()
        print(f"Erreur d'ingestion : {e}")
    finally:
        db.close()