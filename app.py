import base64
import os
from datetime import datetime

from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


basedir = os.path.abspath(os.path.dirname("__file__"))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'

UPLOAD_FOLDER = os.path.join(basedir, "uploads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(300), unique=False)
    rendered_data = db.Column(db.Text, nullable=False)  # Data to render the pic in browser


@app.route('/', methods=['GET', 'POST'])
def main():
    files = File.query.all()
    return render_template('index.html', files=files)


def render_picture(data):
    render_pic = base64.b64encode(data).decode('ascii')
    return render_pic


@app.route('/success', methods=['POST'])
def success():
    file = request.files['inputFile']
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    data = file.read()
    render_file = render_picture(data)

    newFile = File(name=file.filename, rendered_data=render_file)
    db.session.add(newFile)
    db.session.commit()
    flash(f'Pic {newFile.name} uploaded')

    return render_template('success.html', name=newFile.name)
