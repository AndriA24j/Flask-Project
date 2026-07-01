from ext import app


if __name__ == "__main__":
    from routes import *
    app.run(port=5000, debug=True)