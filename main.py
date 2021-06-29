from flask import render_template
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate

from app import create_app, db

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(threaded=True, host="127.0.0.1", port=5000)

