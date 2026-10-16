from datetime import timedelta
from db import init_db
import flask

def create_app():
    app = flask.Flask(__name__)
    app.secret_key = "aadyujfweaetrhgfb3455687uym,.;kljd"
    app.permanent_session_lifetime = timedelta(days=5)


    init_db()

    from views import view
    app.register_blueprint(view)

    from catalogues import catalogue
    app.register_blueprint(catalogue)

    return app


app = create_app()
if __name__ == '__main__':
    app.run(debug=True)