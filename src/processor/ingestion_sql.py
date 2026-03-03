# Copyright (C) 2026 Francisco CABRERA HERRE
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU Affero General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.

import datetime
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from tqdm import tqdm
from src.database.models import production_energie, production_quarantaine, registre_audit_ia
from src.database.database_setup import SessionLocal


def executer_ingestion_systeme(df, resultat_audit, nom_fichier):
    db = SessionLocal()
    
    # Identification des indices des lignes en erreur
    indices_erreurs = set()
    for res in resultat_audit.results:
        if not res.success:
            indices = res.result.get('unexpected_index_list', [])
            indices_erreurs.update(indices)
    
    df = df.drop_duplicates(subset=['libelle_region', 'date_heure'], keep='first').reset_index(drop=True)
    
    print(f"Finalisation : Traitement de {len(df)} lignes...")

    # On crée deux listes pour accumuler les records au lieu d'insérer 1 par 1
    records_propres = []
    records_quarantaine = []

    try:
        for index, row in tqdm(df.iterrows(), total=len(df), desc="Préparation des données"):
            data_fields = {
                "libelle_region": str(row['libelle_region']),
                "date_heure": pd.to_datetime(row['date_heure']),
                "consommation": float(row['consommation']) if pd.notnull(row['consommation']) else 0,
                "nucleaire": float(row['nucleaire']) if pd.notnull(row['nucleaire']) else 0,
                "eolien": float(row['eolien']) if pd.notnull(row['eolien']) else 0,
                "solaire": float(row['solaire']) if pd.notnull(row['solaire']) else 0
            }

            if index in indices_erreurs:
                data_fields["erreur_log"] = "Échec validation audit"
                records_quarantaine.append(data_fields)
            else:
                records_propres.append(data_fields)

        # insertions en batch
        if records_propres:
            print(f"Envoi de {len(records_propres)} lignes vers la table de production...")
            stmt = insert(production_energie).values(records_propres)
            stmt = stmt.on_conflict_do_nothing(index_elements=['libelle_region', 'date_heure'])
            db.execute(stmt)

        if records_quarantaine:
            print(f"Envoi de {len(records_quarantaine)} lignes vers la quarantaine...")
            stmt_q = insert(production_quarantaine).values(records_quarantaine)
            db.execute(stmt_q)

        print("Finalisation de la transaction SQL...")
        db.commit()
        print(f"Succès : {len(records_propres)} validées, {len(records_quarantaine)} en quarantaine.")

    except Exception as e:
        db.rollback()
        print(f"Erreur d'ingestion : {e}")
        raise e
    finally:
        db.close()