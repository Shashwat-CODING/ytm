from flasgger import Swagger

swagger_template = {
	"swagger": "2.0",
	"info": {
		"title": "YouTube Music API (Unofficial)",
		"description": "Flask wrapper around ytmusicapi (unauthenticated). See docs: https://ytmusicapi.readthedocs.io/en/stable/",
		"version": "1.0.0",
	},
	"basePath": "/",
}

swagger_config = {
	"headers": [],
	"specs": [
		{
			"endpoint": "apispec",
			"route": "/apispec.json",
			"rule_filter": lambda rule: True,
			"model_filter": lambda tag: True,
		}
	],
	"static_url_path": "/flasgger_static",
	"swagger_ui": True,
	"specs_route": "/docs/",
}


def init_swagger(app):
	Swagger(app, template=swagger_template, config=swagger_config)
