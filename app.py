from flask import Flask, render_template, request, redirect, session
from models import db, User, Violation
import qrcode
import os

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///traffic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# create DB
with app.app_context():
    db.create_all()

    if not User.query.first():
        db.session.add(User(username="admin", password="1234"))
        db.session.commit()

# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()

        if user:
            session['user'] = user.username
            return redirect('/dashboard')

    return render_template('login.html')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    total = Violation.query.count()
    paid = Violation.query.filter_by(status="Paid").count()
    unpaid = Violation.query.filter_by(status="Unpaid").count()

    return render_template('dashboard.html',
                           total=total,
                           paid=paid,
                           unpaid=unpaid)

# ---------------- ADD ----------------
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':

        file = request.files['image']
        filename = ""

        if file and file.filename != "":
            filename = file.filename
            filepath = os.path.join("static/uploads", filename)
            file.save(filepath)

        v = Violation(
            vehicle_number=request.form['vehicle'],
            violation_type=request.form['type'],
            location=request.form['location'],
            date=request.form['date'],
            fine_amount=request.form['fine'],
            image=filename
        )

        db.session.add(v)
        db.session.commit()

        # QR
        qr_folder = "static/qr_codes"
        os.makedirs(qr_folder, exist_ok=True)

        url = request.host_url + f"status/{v.id}"
        img = qrcode.make(url)
        img.save(f"{qr_folder}/{v.id}.png")

        return redirect('/dashboard')

    return render_template('add.html')

# ---------------- SEARCH ----------------
@app.route('/search', methods=['GET', 'POST'])
def search():
    data = []

    if request.method == 'POST':
        vehicle = request.form.get('vehicle')

        if vehicle:
            data = Violation.query.filter(
                Violation.vehicle_number.like(f"%{vehicle}%")
            ).all()

    return render_template('search.html', data=data)

# ---------------- UPDATE ----------------
@app.route('/update/<int:id>')
def update(id):
    v = Violation.query.get(id)
    v.status = "Paid"
    db.session.commit()
    return redirect('/search')

# ---------------- STATUS ----------------
@app.route('/status/<int:id>')
def status(id):
    record = Violation.query.get(id)
    qr = f"qr_codes/{id}.png"
    return render_template('status.html', record=record, qr=qr)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)