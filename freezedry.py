import posixpath
from flask import Flask, render_template, render_template_string
from flask_flatpages import FlatPages
from flask_frozen import Freezer
from jinja2.exceptions import TemplateNotFound
from werkzeug.exceptions import HTTPException
import toml
import importlib.util

### Templates
error_template = """
<html>
  <head><title>{{ title }}</title></head>
  <body>
    <h1>{{ title }}</h1>
    {% if page %}
      {% block content %} {{ page.html|safe }} {% endblock content %}
    {% endif %}
    {% if not page %}
      <p>{{ error.description }}</p>
    {% endif %}
  </body>
</html>
"""


### App
def create_app(add_routes: bool = True) -> Flask:
    """
    Creates the app. Optionally adds the base routes.
    """
    # App
    app = Flask("app")

    # Freezer
    freezer = Freezer(app)
    app.freezer = freezer

    # Config
    app.config.from_mapping(
        {
            "FLATPAGES_AUTO_RELOAD": True,
            "FLATPAGES_EXTENSION": ".md",
            "FREEZER_IGNORE_MIMETYPE_WARNINGS": True,
        }
    )
    app.config.from_file("pyproject.toml", load=lambda x: toml.load(x).get("app", {}))

    # Setup
    app.url_map.strict_slashes = False

    # Base routes
    if add_routes:
        pages = FlatPages(app)

        @app.route("/")
        @app.route("/<path:path>")
        @app.route("/<path:path>.html")
        def page(path=None):
            page = pages.get(path or "index") or pages.get_or_404(
                posixpath.join(path, "index")
            )
            return render_template(
                page.meta.get("template", "page.html"),
                page=page,
                title=page.meta.get("title", ""),
            )

        @freezer.register_generator
        def list_pages():
            pages.get("test")
            # Return a list. (Any iterable type will do.)
            for page, created in pages._file_cache.values():
                path = "/" + page.path
                path = path.replace("/index", "/")
                if not path.endswith("/"):
                    path = path + ".html"
                print(path)
                yield path

        @app.errorhandler(HTTPException)
        def error(e):
            page = pages.get(f"error_{e.code}") or pages.get("error")
            title = page.meta.get("title", e.name) if page else e.name
            try:
                return (
                    render_template("error.html", page=page, title=title, error=e),
                    e.code,
                )
            except TemplateNotFound:
                return render_template_string(
                    error_template, page=page, title=title, error=e
                )

    return app


def resolve_app() -> Flask:
    try:
        spec = importlib.util.spec_from_file_location("app", "app.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except FileNotFoundError:
        return create_app()
    return mod.app


# Scripts
def freeze():
    app = resolve_app()
    print("Freezing app...")
    app.freezer.freeze()
    print("Done.")


def serve():
    app = resolve_app()
    app.run(debug=True)
