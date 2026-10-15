
from flask import Flask, jsonify

from analyse_produits import analyser_tous_les_produits

app = Flask(__name__)


@app.route("/api/v1/stats/produits", methods=["GET"])
def analyser_produits():
    try:
        resultat = analyser_tous_les_produits()
        return jsonify(resultat), 200

    except FileNotFoundError:
        return jsonify({
            "erreur": "Le fichier data_local.json est introuvable"
        }), 500

    except Exception:
        app.logger.exception("Erreur lors de l'analyse")
        return jsonify({
            "erreur": "Impossible d'analyser les produits"
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=3000)
