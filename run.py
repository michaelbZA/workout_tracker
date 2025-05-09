# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    # app.run(debug=True) will start the Flask development server
    # debug=True enables debug mode, which provides helpful error messages
    # and reloads the server when you make code changes.
    # DO NOT use debug=True in a production environment.
    app.run(debug=True)