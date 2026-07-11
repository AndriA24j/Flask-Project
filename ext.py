import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__, instance_relative_config=True)

app.config["SECRET_KEY"] = "secret123"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
os.makedirs(app.instance_path, exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(app.instance_path, 'database.db')}"

db = SQLAlchemy(app)