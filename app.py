
from flask import Flask, jsonify
import pandas as pd
import requests
import json
from pathlib import Path

app = Flask(__name__)

# Chemin du fichier local, indépendant du dossier courant
BASE_DIR = Path(__file__).resolve().parent
FICHIER_LOCAL = BASE_DIR / "data_local.json"

URL_API = "https://dummyjson.com/products"


def charger_donnees_locales():
    """Charge les produits depuis le fichier JSON local."""
    with open(FICHIER_LOCAL, "r", encoding="utf-8") as fichier:
        donnees = json.load(fichier)

    return pd.DataFrame(donnees)


def charger_donnees_distantes():
    """Récupère les produits depuis une API HTTPS."""
    reponse = requests.get(URL_API, timeout=10)
    reponse.raise_for_status()

    donnees = reponse.json()
    return pd.DataFrame(donnees["products"])


def calculer_statistiques(df, colonne_prix):
    """Calcule les statistiques d'une Series de prix."""
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


@app.route("/api/v1/stats/produits", methods=["GET"])
def analyser_produits():
    try:
        # 1. Extraction des deux sources
        df_local = charger_donnees_locales()
        df_distant = charger_donnees_distantes()

        # 2. Manipulation des DataFrames et des Series
        stats_locales = calculer_statistiques(
            df_local, "prix"
        )

        stats_distantes = calculer_statistiques(
            df_distant, "price"
        )

        # 3. Réponse JSON
        resultat = {
            "source_locale": {
                "fichier": "data_local.json",
                "statistiques": stats_locales,
                "colonnes": df_local.columns.tolist()
            },
            "source_distante": {
                "url": URL_API,
                "statistiques": stats_distantes,
                "colonnes": df_distant.columns.tolist()
            }
        }

        return jsonify(resultat), 200

    except FileNotFoundError:
        return jsonify({
            "erreur": "Le fichier data_local.json est introuvable"
        }), 500

    except (requests.RequestException, ValueError, KeyError) as erreur:
        app.logger.warning("Erreur de traitement : %s", erreur)
        return jsonify({
            "erreur": "Impossible de récupérer ou analyser les données"
        }), 502

    except (OSError, json.JSONDecodeError):
        app.logger.exception("Erreur de lecture du fichier local")
        return jsonify({
            "erreur": "Impossible de lire le fichier JSON local"
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=3000)
