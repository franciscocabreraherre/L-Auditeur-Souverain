# Copyright (C) 2026 Francisco CABRERA HERRE
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU Affero General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.

from sqlalchemy.orm import Session
from src.database.models import registre_audit_ia
import datetime

def inserer_rapport_audit(session: Session, digest: dict, rapport_ia: dict, nom_fichier: str):
    """
    Insère le verdict de l'IA et les stats de Great Expectations 
    dans la table registre_audit_ia.
    """
    try:
        # On mappe le JSON de l'IA vers le modèle SQLAlchemy
        nouvel_audit = registre_audit_ia(
            date_audit=datetime.datetime.now(datetime.timezone.utc),
            nom_fichier=nom_fichier,
            taux_succes=digest.get("taux_succes", 0.0),
            nb_lignes_ignorees=digest.get("nb_lignes_quarantaine", 0),
            # On convertit le verdict texte en Boolean pour la colonne conformite_statut
            conformite_statut=(rapport_ia.get("verdict_final") == "CONFORME"),
            # On stocke l'intégralité du JSON pour le Dashboard
            rapport_ia=rapport_ia 
        )

        session.add(nouvel_audit)
        session.commit()
        print(f"✓ Rapport d'audit inséré avec succès (ID: {nouvel_audit.id})")
        return nouvel_audit.id

    except Exception as e:
        session.rollback()
        print(f"✗ Erreur lors de l'insertion de l'audit : {e}")
        raise e