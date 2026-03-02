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


def recuperer_donnees_incrementales():
    """
    Télécharge uniquement les nouvelles données régionales éCO2mix depuis la dernière date présente dans la base de données.
    """
    derniere


def recuperer_donnees_2025():
    """
    Téléchargement des données régionales éCO2mix de l'année 2025 en utilisant l'API du site web de l'ODRE.
    """
    derniere_date = obtenir_derniere_date_base()
    
    # Si la base est vide on télécharge toutes les données à partir du 01/01/2025
    if derniere_date is None:
        start_filter = "2025-01-01T00:00:00Z"
        print("Aucune date trouvée dans la base de données. Téléchargement de toutes les données à partir de 2025.")
    else:
        start_filter = (derniere_date).isoformat()
        print(f"Dernière date dans la base de données : {derniere_date}. Téléchargement des données à partir de cette date.")

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

    print("Téléchargement des données RTE 2025 en cours (cela peut prendre un moment)...")
    
    try:
        reponse = requests.get(URL_API, params=parametres, headers=headers, stream=True)
        reponse.raise_for_status() # Vérifie si le téléchargement a échoué (404, 500, etc.)

        # Si l'API ne renvoie rien (pas de nouvelles données)
        if int(reponse.headers.get('Content-Length', 0)) < 100: # Seuil arbitraire pour un CSV vide
             print("Aucune nouvelle donnée disponible sur le serveur.")
             return False

        taille_totale = int(reponse.headers.get('content-length', 0))

        os.makedirs('data', exist_ok=True)
        chemin_fichier = "data/delta_update.csv"
        
        with open(chemin_fichier, "wb") as f, \
        tqdm(
            desc="Téléchargement",
            total=taille_totale,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as barre:
            for morceau in reponse.iter_content(chunk_size=1024):
                taille = f.write(morceau)
                barre.update(taille)
        
        print(f"Nouvelles données sauvegardées dans : {chemin_fichier}")
        return True

    except Exception as e:
        print(f"Erreur lors de la récupération : {e}")
        return False

if __name__ == "__main__":
    recuperer_donnees_incrementales()
