# Copyright (C) 2026 Francisco CABRERA HERRE
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU Affero General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.

from sqlalchemy import text
import json

def sauvegarder_audit_final(engine, audit_id, rapport_ia):
    """
    Persiste le verdict et le rapport de l'IA dans la base de données.
    """
    verdict = rapport_ia.get('verdict_final', 'NON DÉTERMINÉ')
    
    query = text("""
        INSERT INTO registre_audit_ia (audit_id, verdict_ia, rapport_complet)
        VALUES (:aid, :verdict, :rapport)
    """)
    
    with engine.connect() as conn:
        conn.execute(query, {
            "aid": audit_id,
            "verdict": verdict,
            "rapport": json.dumps(rapport_ia)
        })
        conn.commit()