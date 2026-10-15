
import json
from pathlib import Path

import pandas as pd
import requests


# Chemin du fichier JSON local
BASE_DIR = Path(__file__).resolve().parent
FICHIER_LOCAL = BASE_DIR / "data_local.json"

# API distante
URL_API = "https://dummyjson.com/products"


def charger_donnees_locales():
    """Charge les produits depuis le fichier JSON local."""
    with open(FICHIER_LOCAL, "r", encoding="utf-8") as fichier:
        donnees = json.load(fichier)

    return pd.DataFrame(donnees)


def charger_donnees_distantes():
    """Récupère les produits depuis l'API HTTPS."""
    reponse = requests.get(URL_API, timeout=10)
    reponse.raise_for_status()

    donnees = reponse.json()
    return pd.DataFrame(donnees["products"])


def calculer_statistiques(df, colonne_prix):
    """Calcule les statistiques descriptives des prix."""
    if colonne_prix not in df.columns:
        raise ValueError(
            f"Colonne absente : {colonne_prix}"
        )

    prix = pd.to_numeric(
        df[colonne_prix], errors="coerce"
    ).dropna()

    if prix.empty:
        raise ValueError("Aucun prix valide disponible")

    stats = prix.describe()

    return {
        "total_produits": int(stats["count"]),
        "prix_moyen": round(float(stats["mean"]), 2),
        "prix_min": float(stats["min"]),
        "prix_max": float(stats["max"])
    }


def analyser_tous_les_produits():
    """Analyse les deux sources et retourne les résultats."""
    df_local = charger_donnees_locales()
    df_distant = charger_donnees_distantes()

    return {
        "source_locale": {
            "fichier": "data_local.json",
            "statistiques": calculer_statistiques(
                df_local, "prix"
            ),
            "colonnes": df_local.columns.tolist()
        },
        "source_distante": {
            "url": URL_API,
            "statistiques": calculer_statistiques(
                df_distant, "price"
            ),
            "colonnes": df_distant.columns.tolist()
        }
    }
