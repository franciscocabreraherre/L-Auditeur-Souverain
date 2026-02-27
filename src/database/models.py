# Copyright (C) 2026 Francisco CABRERA HERRE
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU Affero General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.

from sqlalchemy import Numeric, String, DateTime, Float, Boolean, Integer, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime

## Définition des modèles de données pour SQLAlchemy


class Base(DeclarativeBase):
    pass


class production_energie(Base):
    # nom de la table dans la base de données
    __tablename__ = "production_energie"

    # définition des colonnes de la table
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    libelle_region: Mapped[str] = mapped_column(String(100), nullable=False)
    date_heure: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=False), nullable=False) #timezone=False car les données d'eco2mix sont en heure locale
    consommation: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)
    nucleaire: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)
    eolien: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)
    solaire: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)

    # contrainte d'unicité pour éviter les doublons de données pour une même région et une même date/heure
    __table_args__ = (
        UniqueConstraint("libelle_region", "date_heure", name="uq_region_date_heure"),
        {"extend_existing": True} # pour éviter les conflits si la table existe déjà, notamment lors du développement et des tests répétés
    )


class registre_audit_ia(Base):
    # nom de la table dans la base de données
    __tablename__ = "registre_audit_ia"

    # définition des colonnes de la table
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date_audit: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False) #timezone=True pour stocker la date et l'heure de l'audit avec le fuseau horaire, ce qui est important pour les audits réalisés à différents moments de la journée ou dans différents fuseaux horaires
    nom_fichier: Mapped[str] = mapped_column(String(255), nullable=False)
    taux_succes: Mapped[float] = mapped_column(Float, nullable=False)
    nb_lignes_ignorees: Mapped[int] = mapped_column(Integer, nullable=False)
    conformite_statut: Mapped[bool] = mapped_column(Boolean, nullable=False)


class production_quarantaine(Base):
    # nom de la table dans la base de données
    __tablename__ = "production_quarantaine"

    # définition des colonnes de la table
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    libelle_region: Mapped[str] = mapped_column(String(100), nullable=False)
    date_heure: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=False), nullable=False) #timezone=False car les données d'eco2mix sont en heure locale
    consommation: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)
    nucleaire: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)
    eolien: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)
    solaire: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)

    # nouvelle colonne pour la traçabilite de l'erreur
    erreur_log: Mapped[str] = mapped_column(String(255), nullable=True)

    # pas de contrainte d'unicité pour permettre l'insertion de 
    # plusieurs tentatives de données érronées si besoin
