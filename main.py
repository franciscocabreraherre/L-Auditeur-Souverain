import sys
from src.database.database_setup import SessionLocal
from src.processor.init_qualite import initialiser_audit_qualite, extraire_resume_audit
from src.processor.agent_ia import AgentAuditeurSouverain
from src.processor.ingestion_sql import executer_ingestion_systeme
from src.database.queries_ia import inserer_rapport_audit
from src.scraper.telecharger_donnees import executer_telechargement_incremental

def run_pipeline():
    """
    Orchestre le flux : téléchargement -> Audit qualité -> Ingestion SQL -> Rapport IA.
    """
    nom_csv = "delta_update.csv"
    print(f"Information : Lancement du pipeline pour {nom_csv}.")

    # ETAPE 1 : Téléchargement
    print("--- ETAPE 1 : Téléchargement des données ---")
    statut_telechargement = executer_telechargement_incremental()

    if statut_telechargement is None:
        print("Fin du pipeline : Aucune nouvelle donnée.")
        return
    
    if statut_telechargement is False:
        print("Erreur : Échec du téléchargement.")
        sys.exit(1)

    # ETAPE 2 : Audit Great Expectations
    print("--- ETAPE 2 : Audit de conformité (EU AI Act) ---")
    try:
        # On récupère df et resultat (ton objet GE)
        df, resultat = initialiser_audit_qualite()

        if df is None or resultat is None:
            sys.exit(1)

        print(f"Audit terminé. Score : {resultat.statistics['success_percent']}%")
    except Exception as e:
        print(f"Erreur lors de l'audit : {e}")
        return
    
    # ETAPE 3 : Ingestion SQL
    print("--- ETAPE 3 : Ingestion (Propre/Quarantaine) ---")
    try:    
        executer_ingestion_systeme(df, resultat, nom_fichier=nom_csv)
    except Exception as e:
        print(f"Erreur lors de l'ingestion : {e}")
        return
    
    # ETAPE 4 : Rapport IA et Persistance
    print("--- ETAPE 4 : Analyse IA et Enregistrement ---")
    try:        
        digest = extraire_resume_audit(resultat) 
                
        agent = AgentAuditeurSouverain()
        rapport_ia = agent.generer_audit_ia(digest)
                
        with SessionLocal() as session:
            inserer_rapport_audit(
                session=session,
                digest=digest,
                rapport_ia=rapport_ia,
                nom_fichier="delta_update.csv"
            )
        print("Information : Pipeline terminé avec succès.")
        
    except Exception as e:
        print(f"Erreur : ÉCHEC DU PIPELINE à l'étape IA : {e}")

if __name__ == "__main__":
    run_pipeline()