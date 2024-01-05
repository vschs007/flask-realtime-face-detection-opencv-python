from flask import Flask, request, Response,render_template,make_response,redirect, url_for
from werkzeug.utils import secure_filename

from db import db_init, db
from models import Img
import os
import io

from PIL import Image
from pix2tex.cli import LatexOCR

app = Flask(__name__)

file_path = os.path.abspath(os.getcwd())+"\img.db"
# SQLAlchemy config. Read more: https://flask-sqlalche
# my.palletsprojects.com/en/2.x/
app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///'+file_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)

@app.route('/')
def index(name=None):
    return render_template('index.html',name=name)


@app.route('/upload', methods=['POST'])
def upload():
    pic = request.files['pic']
    if not pic:
        return 'No pic uploaded!', 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return 'Bad upload!', 400

    img = Img(img=pic.read(), name=filename, mimetype=mimetype)
    db.session.add(img)
    db.session.commit()

    #return 'Img Uploaded!', 200
    return redirect(url_for('get_img_latex', id=img.id))


@app.route('/<int:id>')
def get_img(id):
    img = Img.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)


@app.route('/use/<int:id>')
def get_img_latex(id):
    img = Img.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404
    img_data = Image.open(io.BytesIO(img.img))
    model = LatexOCR()
    result = model(img_data)

    response = make_response(result)

    return response