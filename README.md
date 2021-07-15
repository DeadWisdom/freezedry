## FreezeDry

Freeze Dry is a simple static site generator using Flask and Frozen Flask.

It's based off this tutorial: [https://github.com/DeadWisdom/flask-static-tutorial/](https://github.com/DeadWisdom/flask-static-tutorial/).

## Usage:

Initialize your project, and add the dependency:

    $ poetry init
    ...
    $ poetry add git+https://github.com/deadwisdom/freezedry.git#main
  
Create two files:

    /pages/index.md
    /templates/page.html

Also, create a static directory, and add files, use like \<img src="/static/..."\>

    /static/base.css
    /static/img/...
    ...

Now to run locally:

    $ poetry run serve

To build:

    $ poetry run freeze

## Settings

Add app settings to your `pyproject.toml` like:

    [app]
    FLATPAGES_EXTENSION = '.moo'

## Extend

The `app` symbol from a local `app.py` will be preferred to the freezedry project one.
So you can extend the app by creating an `app.py` file like so:

    import create_app from freezedry

    app = create_app()

    @app.route('/test')
    def test():
        return "Works"
