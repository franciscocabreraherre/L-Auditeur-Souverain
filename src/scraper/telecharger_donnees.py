# Copyright (C) 2026 Francisco CABRERA HERRE
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU Affero General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.

import pandas as pd
import requests
import os
from tqdm import tqdm
from sqlalchemy import func # pour les fonctions d'agrégation dans SQLAlchemy
from src.database.database_setup import SessionLocal
from src.database.models import production_energie


def obtenir_derniere_date_base():
    """
    Récupère la dernière date de données présentes dans la base de données.
    """
    db = SessionLocal()
    try:
        derniere_date = db.query(func.max(production_energie.date_heure)).scalar()
        return derniere_date
    finally:
        db.close()


def executer_telechargement_incremental():
    """
    Télécharge uniquement les nouvelles données régionales éCO2mix depuis la dernière date présente dans la base de données.
    """
    
    derniere_date = obtenir_derniere_date_base()
    
    # Si la base est vide on télécharge toutes les données à partir du 01/01/2025
    if derniere_date is None:
        start_filter = "2025-01-01T00:00:00Z"
        print("Initialisation : aucune donnée en base. Récupération depuis le 01/01/2025.")
    else:
        start_filter = (derniere_date).isoformat()
        print(f"Mise à jour : récupération des données postérieures au {start_filter}.")

    URL_API = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-regional-tr/exports/csv"

    # Nous utilisons le paramètre 'where' pour filtrer données côté serveur (API)
    parametres = {
        'where': f"date_heure >= '{start_filter}'",
        'limit': -1,  # Récupérer toutes les données (eviter la pagination)
        'sep': ';'
    }

    # Optionnel si la clé de l'API est configurée dans les variables d'environnement
    api_key = os.getenv("ODRE_API_KEY")
    headers = {"Authorization": f"Apikey {api_key}"} if api_key else {}

    # Début du téléchargement avec barre de progression
    print("Téléchargement des données RTE 2025 en cours (cela peut prendre un moment)...")
    
    try:
        reponse = requests.get(URL_API, params=parametres, headers=headers, stream=True)
        reponse.raise_for_status() # Vérifie si le téléchargement a échoué (404, 500, etc.)

        os.makedirs('data', exist_ok=True)
        chemin_fichier = "data/delta_update.csv"
        
        with open(chemin_fichier, "wb") as f:
            # On récupère le premier morceau pour vérifier s'il y a du contenu
            iterateur = reponse.iter_content(chunk_size=1024)
            try:
                premier_morceau = next(iterateur)
            except StopIteration:
                print("Information : le serveur a renvoyé un fichier vide.")
                return None
            
            f.write(premier_morceau)

            with tqdm(desc="Téléchargement", unit='iB', unit_scale=True, unit_divisor=1024) as barre:
                barre.update(len(premier_morceau))
                for morceau in iterateur:
                    f.write(morceau)
                    barre.update(len(morceau))
        
        # vérification post-téléchargement de la taille du fichier
        taille_reelle = os.path.getsize(chemin_fichier)

        if taille_reelle < 2500: # Taille estimée pour un CSV de plus de 12 lignes (environ 2kb d'après les tests)
            print("Information : Le fichier téléchargé est vide ou ne contient que les en-têtes.")
            return None
        
        print(f"Succès : données sauvegardées dans {chemin_fichier}")
        return True

    except Exception as e:
        print(f"Erreur lors de la récupération : {e}")
        return False

if __name__ == "__main__":
    executer_telechargement_incremental()
