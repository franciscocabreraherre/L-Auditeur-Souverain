# Copyright (C) 2026 Francisco CABRERA HERRE
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU Affero General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.

import pandas as pd
import requests
import os
from tqdm import tqdm

def recuperer_donnees_2025():
    """
    Téléchargement des données régionales éCO2mix de l'année 2025 en utilisant l'API du site web de l'ODRE.
    """
    # URL de l'API OpenDataSoft pour RTE (Filtré sur l'année 2025)
    URL_API = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-regional-tr/exports/csv"
    parametres = {
        'where': "date_heure >= '2025-01-01' AND date_heure <= '2025-12-31'",
        'limit': -1,  # Récupérer toutes les données (eviter la pagination)
        'sep': ';'
    }

    print("Téléchargement des données RTE 2025 en cours (cela peut prendre un moment)...")
    
    try:
        reponse = requests.get(URL_API, params=parametres, stream=True)
        reponse.raise_for_status() # Vérifie si le téléchargement a échoué (404, 500, etc.)

        taille_totale = int(reponse.headers.get('content-length', 0))

        os.makedirs('data', exist_ok=True)
        
        chemin_fichier = "data/eco2mix_2025.csv"
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
            
        print(f"Données sauvegardées avec succès dans : {chemin_fichier}")
        
        df = pd.read_csv(chemin_fichier, sep=';')
        print(f"Colonnes détectées : {list(df.columns)}")
        print(f"Nombre de lignes : {len(df)}")

    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")


if __name__ == "__main__":
    recuperer_donnees_2025()