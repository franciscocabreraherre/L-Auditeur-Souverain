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
