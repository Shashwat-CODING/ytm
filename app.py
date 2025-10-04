from flask import Flask, jsonify
from flask_cors import CORS
from ytmusicapi import YTMusic
from routes import bp as api_bp
from routes_entities import bp_entities
from routes_explore import bp_explore
from routes_youtube import bp_youtube
from routes_jiosaavn import bp_jiosaavn
from swagger import init_swagger
import os


def create_app() -> Flask:
	app = Flask(__name__)

	# Enable CORS for all domains
	CORS(app, origins="*")

	# Unauthenticated client (no OAuth or cookies)
	# See: https://ytmusicapi.readthedocs.io/en/stable/
	ytmusic = YTMusic()

	@app.get("/health")
	def health() -> tuple:
		return jsonify({"status": "ok"}), 200

	# Expose ytmusic instance via app context for use in other routes
	app.config["YTMUSIC_CLIENT"] = ytmusic

	# Docs
	init_swagger(app)

	# Register API blueprints under /api
	app.register_blueprint(api_bp, url_prefix="/api")
	app.register_blueprint(bp_entities, url_prefix="/api")
	app.register_blueprint(bp_explore, url_prefix="/api")
	app.register_blueprint(bp_youtube, url_prefix="/api")
	app.register_blueprint(bp_jiosaavn, url_prefix="/api")
	return app


# Module-level app for WSGI servers
app = create_app()


if __name__ == "__main__":
	# Local dev server
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, debug=True)
