# Copyright (C) 2026 Francisco CABRERA HERRE
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU Affero General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.

import os
import json
from mistralai import Mistral
from dotenv import load_dotenv  # pour l'execution locale uniquemente

class AgentAuditeurSouverain:
    def __init__(self):
        # Charge les variables du fichier .env s'il existe
        # (Uniquement pour les tests locales)
        load_dotenv() 
        
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY non trouvée dans l'environnement")
        
        self.client = Mistral(api_key=api_key)
        self.model = "mistral-medium-latest"


    def generer_audit_ia(self, digest: dict) -> dict:
        """
        Analyse le résumé d'audit et produit un verdict structuré.
        """
        # Détermination du scénario (Harnais logique)
        taux = digest.get('taux_succes', 0)
        scenario = "A" if taux == 100 else ("B" if taux > 95 else "C")
        
        prompt_systeme = (
            "Tu es l'Auditeur Souverain. Posture : Froide, rigoureuse. "
            "Expert Article 10 EU AI Act. Ne cite que les chiffres fournis. "
            "Si un doute subsiste, réponds 'NON DÉTERMINÉ'."
        )

        prompt_utilisateur = self.obtenir_prompt_production(digest)

        # Utilisation du nouveau format de réponse JSON du SDK Mistral
        reponse = self.client.chat.complete(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": prompt_systeme},
                {"role": "user", "content": prompt_utilisateur}
            ]
        )

        return json.loads(reponse.choices[0].message.content)


    def obtenir_prompt_production(self, digest):
        return f"""
            AUDIT CRITIQUE - FLUX ÉCO2MIX RTE
            Données : {json.dumps(digest)}

            CADRE D'EXPERTISE :
            1. ANALYSE STRUCTURELLE : Si le nombre d'erreurs détectées est multiple de 12, prende en compte qu'en France, il y a 12 régions continentales. Conclus sur la probabilité d'une panne d'API vs une panne réelle.
            2. ÉVALUATION AI ACT (ART. 10) : Le jeu de données est-il 'représentatif et sans erreur' ? Réponds par OUI ou NON avant d'argumenter.
            3. RISQUE SOUVERAIN : Le nucléaire est la base de la stabilité du réseau (environ 70% de la production nationale). Déduis l'impact d'une erreur de mesure sur le pilotage des réserves de puissance.

            CONSIGNE DE STYLE : Ne sois pas évasif. Si une donnée manque, utilise ta connaissance du secteur énergétique français pour proposer l'hypothèse la plus probable.

            FORMAT JSON REQUIS :
            {{
                "verdict_final": "NON CONFORME | RÉSERVE | CONFORME",
                "hypothese_technique": "Analyse de la panne (12 régions)",
                "audit_legal_detaille": "Analyse Article 10",
                "impact_stabilite_reseau": "Analyse métier profonde",
                "action_immediate": "Recommandation concrète"
            }}
            """