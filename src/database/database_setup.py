import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base

# Obtention de l'URL de la base de données à partir des variables d'environnement
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("L'URL de la base de données (DATABASE_URL) n'est pas définie.")

# Vérification et ajustement de l'URL pour utiliser le driver psycopg2 si nécessaire
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Création de l'engine SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)

# Créer la fabrique de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def initialiser_base_de_donnees():
    """
    Création des tables dans la base de données PostgreSQL si elles n'existent pas encore.
    SQLAlchemy lit les classes définies dans models.py pour générer le SQL nécessaire à la création des tables.
    """
    try:
        print("Initialisation du schéma de base de données...")
        Base.metadata.create_all(bind=engine)
        print("Schéma créé avec succès.")
    except Exception as e:
        print(f"Erreur lors de la création des tables : {e}")
        raise e

if __name__ == "__main__":
    initialiser_base_de_donnees()