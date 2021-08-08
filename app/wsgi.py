# The purpose of this file is simply to provide the WSGI integration for gunicorn.
# Meaning - It allows us to run the web app on the gunicorn server, using a standard web server interface (WSGI).

from app import app


if __name__ == "__main__":
    app.run()
