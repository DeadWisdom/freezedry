from flask import Flask, render_template
from flask_flatpages import FlatPages
from flask_frozen import Freezer
import toml
import importlib.util


def create_app(add_routes:bool=True) -> Flask:
  """
  Creates the app. Optionally adds the base routes.
  """
  # App
  app = Flask('app')

  # Config
  app.config.from_mapping({
    'FLATPAGES_AUTO_RELOAD': True,
    'FLATPAGES_EXTENSION': '.md',
  })
  app.config.from_file("pyproject.toml", load=lambda x: toml.load(x).get('app', {}))

  # Setup
  app.url_map.strict_slashes = False

  # Base routes
  if add_routes:
    pages = FlatPages(app)

    @app.route("/")
    @app.route("/<path:path>.html")
    def page(path=None):
        page = pages.get_or_404(path or 'index')
        return render_template("page.html", page=page, title=page.meta.get('title', ''))

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
  freezer = Freezer(app)
  freezer.freeze()

def serve():
  app = resolve_app()
  app.run(debug=True)
