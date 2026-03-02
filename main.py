import sys
from src.processor.init_qualite import initialiser_audit_qualite
from src.processor.ingestion_sql import executer_ingestion_systeme
from src.scraper.telecharger_donnees import executer_telechargement_incremental

def run_pipeline():
    """
    Orchestre le flux : téléchargement -> Audit qualité -> Ingestion SQL.
    """
    print("Information : Lancement du pipeline.")

    # ETAPE 1 : Téléchargement des données (Delta via API)
    print("--- ETAPE 1 : Téléchargement des données ---")

    statut_telechargement = executer_telechargement_incremental()

    if statut_telechargement is None:
        print("Arret : Aucune nouvelle donnée à traiter. Fin du pipeline.")
        return
    
    if statut_telechargement is False:
        print("Erreur : Le téléchargement a échoué (vérifier connéxion ou clé API). Fin du pipeline.")
        sys.exit(1)

    # ETAPE 2 : Audit de qualité des données avec Great Expectations
    print(f"--- ETAPE 2 : Lancement de l'audit de conformité (EU AI Act) ---")
    try:
        df, resultat = initialiser_audit_qualite()

        if df is None or resultat is None:
            print("Erreur : L'audit de qualité n'a pas pu être initialisé. Fin du pipeline.")
            sys.exit(1)

        taux = resultat.statistics['success_percent']
        print(f"Audit terminé. Score de qualité : {taux}%")
    except Exception as e:
        print(f"Erreur lors de l'audit : {e}")
        return
    
    # ETAPE 3 : Ingestion en base de données (Tri Propre/Quarantaine)
    print("--- ETAPE 3 : Ingestion en base de données (Tri Propre/Quarantaine) ---")

    try:    
        executer_ingestion_systeme(df, resultat, nom_fichier="delta_update.csv")
        print("\nInformation : Pipeline exécuté avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'ingestion : {e}")
        return


if __name__ == "__main__":
    run_pipeline()