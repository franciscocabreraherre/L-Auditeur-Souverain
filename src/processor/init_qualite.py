import great_expectations as gx
import os
import sys


def initialiser_audit_qualite():
    """
    Initialisation de la validation de la qualité des données avec Great Expectations.
    """
    ## ==============================================================
    ## PARTIE 1 : CONFIGURATION DE GREAT EXPECTATIONS
    ## ==============================================================
    
    # Créer un DataContext éphémère
    context = gx.get_context() 
    
    # Ajouter les données à valider au contexte
    chemin_csv = os.path.join("/app", "data", "eco2mix_2025.csv")  # Chemin vers le fichier CSV téléchargé précédemment, mais pointé vers le chemin dans le conteneur Docker

    if not os.path.exists(chemin_csv):
        print(f"Erreur : Le fichier de données n'a pas été trouvé à l'emplacement attendu : {chemin_csv}")
        sys.exit(1)
    
    # Définition de la source de données dans Great Expectations
    nom_source = "source_rte_2025"
    nom_asset = "asset_eco2mix"

    # Configuration du connecteur pour lire le CSV
    datasource = context.data_sources.add_pandas(name=nom_source) 
    asset = datasource.add_csv_asset(name=nom_asset, filepath_or_buffer=chemin_csv, sep=';')

    # Créer une suite d'attentes
    nom_suite = "suite_qualite_donnees"
    suite = gx.ExpectationSuite(name=nom_suite)
    suite = context.suites.add(suite)

    ## ==============================================================
    ## PARTIE 2 : RÉGLES DE VALIDATION (Art 10 EU IA Act)
    ## ==============================================================
    
    ## Note : Les règles suivantes sont basées sur les critères de qualité des données définis dans l'article 10 du Règlement sur l'Intelligence Artificielle de l'UE, adaptés au contexte des données énergétiques régionales.

    # 1- Intégrité du schéma (vérifier que les colonnes attendues sont présentes)
    colonnes_critiques = ["libelle_region", "date_heure", "consommation", "nucleaire", "eolien", "solaire"]
    for col in colonnes_critiques:
        suite.add_expectation(gx.expectations.ExpectColumnToExist(column=col))

    # 2- Completude (données manquantes)
    # Ex: une donnée sans date ou localisation n'est pas exploitable
    suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="date_heure"))
    suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="libelle_region"))
    
    # 3- Cohérence physique et données aberrantes
    # Ex: une consommation négative est un indicateur d'erreur
    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(
        column="consommation", 
        min_value=0, 
        max_value=25000  # Seuil base sur les records historiques par region
    ))
    ## Note : Des seuils plus stricts pourraient être appliqués par région ou par type de production (ex: solaire ne devrait pas dépasser 5000 MW dans une region donnée)
    ## Ici, nous appliquons une règle générale pour détecter les anomalies grossières, mais des règles plus fines pourraient être développées ultérieurement (en réalité la consomation la plus élevée observée est d'environ 14000-15000 MW pour la région d'Île-de-France).

    # 4. Formatage Temporel (Standard ISO 8601)
    suite.add_expectation(gx.expectations.ExpectColumnValuesToMatchStrftimeFormat(
        column="date_heure", 
        strftime_format="%Y-%m-%dT%H:%M:%S"
    ))

    ## ==============================================================
    ## PARTIE 3 : VALIDATION ET RESULTATS
    ## ==============================================================

    # Exécuter la validation via une Validation Definition
    definition_nom = "validation_eco2mix_2025"
    batch_definition = asset.add_batch_definition_whole_dataframe(name="batch_integral_2025")

    validation_definition = context.validation_definitions.add(
        gx.ValidationDefinition(
            name=definition_nom,
            data=batch_definition,
            suite=suite
        )
    )
    
    # Lancement de l'audit
    resultat = validation_definition.run()

    if resultat.success:
        print("Statut : Donnees conformes aux exigences de l'Article 10 EU AI Act.")
    else:
        print("Statut : Anomalies detectees. Audit de qualite rejete.")
        print(f"Taux de succes : {resultat.statistics['success_percent']}%")

    return resultat

if __name__ == "__main__":
    initialiser_audit_qualite()
