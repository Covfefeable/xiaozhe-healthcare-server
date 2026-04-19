from app import create_app
from app.extensions import db


app = create_app()
shell_context = {"app": app, "db": db}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)

