from flask import Flask, render_template, request, send_from_directory, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "ImageGallery/uploads"


db = SQLAlchemy(app)


class File(db.Model):
    __tablename__ = "files"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)

    def __init__(self, filename):
        self.filename = filename


@app.route("/")
def index():
    files = File.query.all()
    return render_template("index.html", files=files)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        filename = file.filename
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        newfile = File(filename)
        db.session.add(newfile)
        db.session.commit()
        return redirect("/")
    return redirect("/", error="file is not uploaded please try again")


@app.route("/images/<filename>")
def images(filename):
    upload_folder = os.path.abspath(app.config["UPLOAD_FOLDER"])  # Get absolute path
    return send_from_directory(upload_folder, filename)


@app.route("/download/<int:id>")
def download(id):
    file = File.query.get_or_404(id)
    upload_folder = os.path.abspath(app.config["UPLOAD_FOLDER"])
    return send_from_directory(upload_folder, file.filename, as_attachment=True)

@app.route("/delete/<int:id>")
def delete(id):
    file = File.query.get_or_404(id)
    upload_folder = os.path.abspath(app.config["UPLOAD_FOLDER"])
    os.remove(os.path.join(upload_folder, file.filename))
    db.session.delete(file)
    db.session.commit()
    return redirect('/')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
