from apps import create_app

from dotenv import load_dotenv
load_dotenv(verbose=True)

app = create_app()

if __name__ == "__main__":
    app.run(ssl_context='adhoc', debug=True)
