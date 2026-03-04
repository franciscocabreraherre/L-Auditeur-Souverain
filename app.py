# Copyright (C) 2026 Francisco CABRERA HERRE
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU Affero General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px
import requests
import datetime
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="L'Auditeur Souverain", layout="wide")

def get_engine():
    user = os.getenv("POSTGRES_USER", "admin")
    password = os.getenv("POSTGRES_PASSWORD", "password")
    db = os.getenv("POSTGRES_DB", "audit_energie")
    host = os.getenv("DB_HOST", "db_audit")
    return create_engine(f"postgresql://{user}:{password}@{host}:5432/{db}")

engine = get_engine()

# --- SIDEBAR ---
st.sidebar.header("🛡️ Intégrité")
with engine.connect() as conn:
    count_q = pd.read_sql("SELECT count(*) FROM production_quarantaine", conn).iloc[0,0]
    if count_q > 0:
        st.sidebar.error(f"⚠️ {count_q} lignes en quarantaine")
    else:
        st.sidebar.success("✅ Données 100% Conformes")

mode = st.sidebar.radio("Mode d'affichage", ["Vue Régionale", "Vue Nationale", "Comparaison"])

# Dates de test adaptées aux données RTE 2025/2026
start_date = st.sidebar.date_input("Début", datetime.date(2025, 1, 1))
end_date = st.sidebar.date_input("Fin", datetime.date(2026, 12, 31))

st.title("⚡ Gouvernance Énergétique")

# --- CARTE DE FRANCE ---
@st.cache_data(ttl=3600)
def get_map_data():
    # GeoJSON officiel des régions
    geo_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson"
    geojson = requests.get(geo_url).json()
    with engine.connect() as conn:
        df = pd.read_sql("SELECT libelle_region, SUM(consommation) as total FROM production_energie GROUP BY 1", conn)
    return df, geojson

try:
    df_map, fra_geo = get_map_data()
    fig = px.choropleth(
        df_map, geojson=fra_geo, locations="libelle_region",
        featureidkey="properties.nom", color="total",
        color_continuous_scale="Viridis", scope="europe"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=350)
    st.plotly_chart(fig, use_container_width=True)
except Exception:
    st.info("Chargement de la carte...")

st.markdown("---")

# --- SECTION AUDIT IA ---
st.header("🔍 Dernier Rapport d'Audit (EU AI Act)")

query_audit = "SELECT date_audit, rapport_ia, taux_succes FROM registre_audit_ia ORDER BY date_audit DESC LIMIT 1"
try:
    df_audit = pd.read_sql(query_audit, engine)
    if not df_audit.empty:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.metric("Taux de Succès", f"{df_audit['taux_succes'][0]}%")
            st.write(f"**Date de l'audit :** {df_audit['date_audit'][0].strftime('%d/%m/%Y %H:%M')}")
        
        with col2:
            # On décode le JSON du rapport d'audit
            rapport = df_audit['rapport_ia'][0]
            st.success(f"**Verdict :** {rapport.get('verdict_final', 'N/A')}")
            st.info(f"**Analyse technique :** {rapport.get('audit_legal_detaille', 'N/A')}")
            with st.expander("Voir les détails de l'action immédiate"):
                st.write(rapport.get('action_immediate', 'Aucune action requise.'))
    else:
        st.warning("Aucun rapport d'audit trouvé en base.")
except Exception as e:
    st.error(f"Erreur lors de la récupération de l'audit : {e}")

# --- SECTION ANALYSE DYNAMIQUE ---
st.markdown("---")

# 1. Initialisation
query = None
params = {}

if mode == "Vue Nationale":
    st.header("🇫🇷 Analyse Nationale")
    query = text("""
        SELECT date_trunc('day', date_heure) as date_heure, 
               SUM(consommation) as consommation, SUM(nucleaire) as nucleaire, 
               SUM(eolien) as eolien, SUM(solaire) as solaire
        FROM production_energie 
        WHERE date_heure BETWEEN :start AND :end
        GROUP BY 1 ORDER BY 1 ASC
    """)
    params = {"start": start_date, "end": end_date}

elif mode == "Vue Régionale":
    with engine.connect() as conn:
        regions = pd.read_sql("SELECT DISTINCT libelle_region FROM production_energie", conn)['libelle_region'].tolist()
    region_selected = st.selectbox("Choisir une région", regions)
    st.header(f"📍 Région : {region_selected}")
    query = text("""
        SELECT date_trunc('hour', date_heure) as date_heure, 
               consommation, nucleaire, eolien, solaire
        FROM production_energie 
        WHERE libelle_region = :region AND date_heure BETWEEN :start AND :end
        ORDER BY 1 ASC LIMIT 2000
    """)
    params = {"region": region_selected, "start": start_date, "end": end_date}

else: # Comparaison
    st.header("⚖️ Comparaison Régionale")
    with engine.connect() as conn:
        regions = pd.read_sql("SELECT DISTINCT libelle_region FROM production_energie", conn)['libelle_region'].tolist()
    
    col1, col2 = st.columns(2)
    r1 = col1.selectbox("Région A", regions, index=0)
    r2 = col2.selectbox("Région B", regions, index=1 if len(regions)>1 else 0)

    query = text("""
        SELECT date_trunc('day', date_heure) as date_heure, libelle_region, SUM(consommation) as total
        FROM production_energie 
        WHERE libelle_region IN (:r1, :r2) 
        AND date_heure >= :start AND date_heure <= :end
        GROUP BY 1, 2 ORDER BY 1 ASC
    """)
    params = {"r1": r1, "r2": r2, "start": start_date, "end": end_date}

# 2. Exécution et Affichage
if query is not None: 
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params=params)
        
        if not df.empty:
            if mode == "Comparaison":
                # On pivote pour avoir une colonne par région
                df_pivot = df.pivot(index='date_heure', columns='libelle_region', values='total')
                st.line_chart(df_pivot)
            else:
                # Affichage standard
                df = df.set_index('date_heure')
                col_a, col_b = st.columns(2)
                with col_a:
                    st.line_chart(df[['solaire', 'eolien', 'nucleaire']])
                with col_b:
                    st.area_chart(df['consommation'])
        else:
            st.warning("Aucune donnée trouvée pour cette période.")
    except Exception as e:
        st.error(f"Erreur d'affichage : {e}")