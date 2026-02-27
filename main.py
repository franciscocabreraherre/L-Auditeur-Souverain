import os
from src.processor.init_qualite import initialiser_audit_qualite
from src.processor.ingestion_sql import executer_ingestion_systeme

def run_pipeline():
    nom_fichier = "eco2mix_2025.csv" 
    
    print(f"--- ETAPE 1 : Lancement de l'audit sur {nom_fichier} ---")
    
    # Execution audit
    try:
        df, resultat = initialiser_audit_qualite()
        taux = resultat.statistics['success_percent']
        print(f"Audit terminé. Score de qualité : {taux}%")
    except Exception as e:
        print(f"Erreur lors de l'audit : {e}")
        return

    print("--- ETAPE 2 : Ingestion en base de données (Tri Propre/Quarantaine) ---")
    
    # On envoie les données et le rapport à notre script d'ingestion
    try:
        executer_ingestion_systeme(df, resultat, nom_fichier)
        print("Pipeline exécuté avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'ingestion : {e}")

if __name__ == "__main__":
    run_pipeline()