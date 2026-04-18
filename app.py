from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask import send_from_directory
from sqlalchemy import distinct
from flask import url_for
import os
import uuid
import random
import uuid
from flask_mail import Mail, Message
# ---------------- BASIC SETUP ----------------
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = "fpyywqfthtklqper"
# ---------------- MAIL CONFIG ----------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'laharivarala06@gmail.com'
app.config['MAIL_PASSWORD'] = 'fpyywqfthtklqper'
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
# create folder automatically
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
mail = Mail(app)
# ---------------- DATABASE ----------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)
# ---------------- MODELS ----------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # TEAM INFORMATION
    team_id = db.Column(db.String(50))
    event_name = db.Column(db.String(200))
    event_type = db.Column(db.String(100))
    organization = db.Column(db.String(200))
    place = db.Column(db.String(200))
    project_title = db.Column(db.String(200))
    from_date = db.Column(db.String(20))
    to_date = db.Column(db.String(20))
    faculty_name = db.Column(db.String(200))
    contact_number = db.Column(db.String(20))
    team_leader = db.Column(db.String(200))
    # STUDENT DETAILS
    student_name = db.Column(db.String(200))
    roll_no = db.Column(db.String(50))
    email = db.Column(db.String(120))   # ✅ ADDED (DO NOT DELETE)
    department = db.Column(db.String(50))
    year = db.Column(db.String(10))
    section = db.Column(db.String(10))   # keep only this one
    # ⭐ already existing
    hod_group = db.Column(db.String(20))
    # APPROVAL STATUS
    ceer_status = db.Column(db.String(50), default="Pending")
    hod_status = db.Column(db.String(50), default="Pending")
    director_status = db.Column(db.String(50), default="Pending")
    faculty_status = db.Column(db.String(50), default="Pending")
    attendance = db.Column(db.String(10))
    # CURRENT APPROVAL STAGE
    stage = db.Column(db.String(50), default="CEER")
class HOD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200), default="cmr123")
    first_login = db.Column(db.Boolean, default=True)
class CEER(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200), default="cmr123")
    first_login = db.Column(db.Boolean, default=True)
class Director(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200), default="cmr123")
    first_login = db.Column(db.Boolean, default=True)
class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200), default="cmr123")
    first_login = db.Column(db.Boolean, default=True)
# ---------------- PERMANENT HOD SEED ----------------
def seed_hods():
    hod_emails = [
        "cse1@cmrcet.ac.in",
        "cse2@cmrcet.ac.in",
        "ece@cmrcet.ac.in",
        "eee@cmrcet.ac.in",
        "csd@gmail.com",
        "csm@gmail.com",
        "mech@cmrcet.ac.in",
        "civil@cmrcet.ac.in"
    ]
    for mail_id in hod_emails:
        exists = HOD.query.filter_by(email=mail_id).first()
        if not exists:
            db.session.add(HOD(email=mail_id, password="cmr123", first_login=True))
    db.session.commit()
# ---------------- HOME ----------------
@app.route('/student_portal')
def student_portal():
    return render_template("student_select.html")
@app.route('/')
def home():
    return render_template("index.html")   # OR login.html
# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # ✅ CHECK IF USER EXISTS
        existing_user = Student.query.filter_by(email=email).first()

        if existing_user:
            flash("User already exists, please login", "error")
            return redirect('/login')   # ✅ better UX

        # ✅ ADD NEW USER
        new_user = Student(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registered successfully, please login", "success")
        return redirect('/login')

    return render_template("register.html")
# ---------------- STUDENT LOGIN ----------------
@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Student.query.filter_by(email=email, password=password).first()

        if user:
            session['user_email'] = email
            return redirect('/student_dashboard')

        flash("Invalid email or password", "error")   # ✅ better message
        return redirect('/login')

    return render_template("login.html")
# ---------------- FORGOT PASSWORD ----------------
@app.route('/forgot', methods=['GET','POST'])
def forgot():

    if request.method == 'POST':

        action = request.form['action']
        email = request.form['email']

        # SEND OTP
        if action == "send_otp":

            student = Student.query.filter_by(email=email).first()

            if not student:
                flash("Email not registered", "error")
                return redirect('/forgot')

            otp = str(random.randint(100000,999999))

            session['otp'] = otp
            session['reset_email'] = email

            msg = Message(
                "Password Reset OTP",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )

            msg.body = f"Your OTP for password reset is: {otp}"

            try:
                mail.send(msg)
            except Exception as e:
                print("Mail error:", e)

            flash("OTP sent to your email", "success")

            return redirect('/verify_otp')

    return render_template("forgot_password.html")
# ---------------- VERIFY OTP ----------------
@app.route('/verify_otp', methods=['GET','POST'])
def verify_otp():

    if request.method == "POST":

        entered_otp = request.form['otp']
        new_password = request.form['password']

        if entered_otp == session.get('otp'):

            email = session.get('reset_email')

            student = Student.query.filter_by(email=email).first()

            if student:
                student.password = new_password
                db.session.commit()

            session.pop('otp', None)
            session.pop('reset_email', None)

            flash("Password updated successfully", "success")

            return redirect('/login')

        else:
            flash("Invalid OTP", "error")

    return render_template("verify_otp.html")
## ---------------- RESET PASSWORD ----------------
@app.route('/reset_password', methods=['GET','POST'])
def reset_password():

    if request.method == "POST":

        new_password = request.form['password']
        email = session.get('reset_email')

        student = Student.query.filter_by(email=email).first()

        if student:
            student.password = new_password
            db.session.commit()

        session.pop('reset_email', None)

        flash("Password updated successfully")

        return redirect('/login')

    return render_template("reset.html")
# ---------------- STUDENT DASHBOARD ----------------
@app.route('/student_dashboard')
def student_dashboard():
    if 'user_email' not in session:
        return redirect('/login')
    return render_template("student_dashboard.html",email=session['user_email'])
# ---------------- COMMON LOGOUT ----------------
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect('/')
# ---------------- APPLY TEAM  ----------------
@app.route('/apply_team', methods=['GET','POST'])
def apply_team():

    if 'user_email' not in session:
        return redirect('/login')

    if request.method == 'POST':

        team_id = str(uuid.uuid4())
        size = int(request.form.get("teamSize"))

        for i in range(1, size+1):

            dept = request.form.get(f"dept{i}").strip().upper()
            section = request.form.get(f"section{i}").strip().upper()
            hod_group = dept
            if dept == "CSE":
                if section in ["C","D","E","F"]:
                    hod_group = "CSE1"
                elif section in ["A","B","G"]:
                    hod_group = "CSE2"

            email_val = request.form.get(f"email{i}")
            roll = email_val.split('@')[0].strip().upper()

            db.session.add(Permission(
                team_id=team_id,

                event_name=request.form['event_name'],
                event_type=request.form['event_type'],
                organization=request.form['organization'],
                place=request.form['place'],
                project_title=request.form.get('project_title'),

                from_date=request.form['from_date'],
                to_date=request.form['to_date'],

                faculty_name=request.form['faculty_name'],
                contact_number=request.form['contact_number'],
                team_leader=request.form['tl_name'],

                student_name=request.form.get(f"name{i}"),

                roll_no=roll,

                email=session['user_email'],   # ✅ IMPORTANT

                department=dept,
                year=str(request.form.get(f"year{i}")),  # ✅ FIX (string)
                section=section,

                hod_group=hod_group,

                ceer_status="Pending",
                hod_status="Pending",
                director_status="Pending",
                faculty_status="Pending",

                stage="CEER"
            ))

        db.session.commit()
        flash("Successfully Submitted", "success")
        return redirect('/apply_team')

    return render_template("team.html")
#-------------------STATUS----------------
@app.route('/status')
def status():
    if 'user_email' not in session:
        return redirect('/login')
    user_email = session['user_email']
    user_roll = user_email.split('@')[0].strip().upper()
    data = Permission.query.filter(
        (Permission.roll_no == user_roll) | (Permission.email == user_email)
    ).all()
    if not data:
        return render_template("status.html", team_data=[])
    team_data = []
    team_ids = list(set([d.team_id for d in data]))
    for tid in team_ids:
        members = Permission.query.filter_by(team_id=tid).all()
        team_data.append({
            "event": members[0].event_name,
            "members": members
        })
    return render_template("status.html", team_data=team_data)
#--------------------HISTORY------------------------------
@app.route('/history')
def history():
    if 'user_email' not in session:
        return redirect('/login')
    user_email = session['user_email']
    user_roll = user_email.split('@')[0].strip().upper()
    data = Permission.query.filter(
        (Permission.roll_no == user_roll) | (Permission.email == user_email)
    ).all()
    if not data:
        return render_template("history.html", teams=[])
    teams = []
    team_ids = list(set([d.team_id for d in data]))
    for tid in team_ids:
        members = Permission.query.filter_by(team_id=tid).all()
        teams.append({
            "event": members[0].event_name,
            "from": members[0].from_date,
            "to": members[0].to_date,
            "size": len(members),
            "hod": members[0].hod_status,
            "ceer": members[0].ceer_status,
            "director": members[0].director_status
        })
    return render_template("history.html", teams=teams)
# =====================================================
# 🔐 HOD LOGIN
# =====================================================
@app.route('/hod_login', methods=['GET','POST'])
def hod_login():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        # ---- FIRST CHECK HOD ----
        hod = HOD.query.filter_by(email=email).first()

        if hod and hod.password == password:

            session['hod_email'] = hod.email

            # extract department from email
            dept = hod.email.split("@")[0]

            # ⭐ FIX: keep CSE1 and CSE2 (do NOT remove numbers)
            dept = dept.strip().upper()

            session['hod_dept'] = dept

            print("HOD DEPARTMENT:", session['hod_dept'])  # DEBUG LINE (helps confirm)

            if hod.first_login:
                return redirect('/hod_change_password')

            session['hod_logged'] = True
            session['role'] = "hod"

            return redirect('/hod_dashboard')

        # ---- THEN CHECK CEER ----
        ceer = CEER.query.filter_by(email=email).first()

        if ceer and ceer.password == password:

            session['ceer_email'] = ceer.email

            if ceer.first_login:
                return redirect('/ceer_change_password')

            session['ceer_logged'] = True
            session['role'] = "ceer"

            return redirect('/ceer_dashboard')

        flash("Invalid Credentials")
        return redirect('/hod_login')

    return render_template("hod_login.html")
# ---------------- HOD CHANGE PASSWORD ----------------
@app.route('/hod_change_password', methods=['GET','POST'])
def hod_change_password():
    if 'hod_email' not in session:
        return redirect('/hod_login')
    if request.method == 'POST':
        newpass = request.form['newpass']
        hod = HOD.query.filter_by(email=session['hod_email']).first()
        hod.password = newpass
        hod.first_login = False
        db.session.commit()
        # FORCE RELOGIN AFTER PASSWORD CHANGE
        session.clear()
        flash("Password changed successfully. Please login again.", "success")
        return redirect('/hod_login')
    return render_template("hod_change_password.html")
# ---------------- HOD FORGOT PASSWORD ----------------
@app.route('/hod_forgot', methods=['GET','POST'])
def hod_forgot():

    if request.method == "POST":

        email = request.form['email']

        hod = HOD.query.filter_by(email=email).first()

        if not hod:
            flash("Email not registered", "error")
            return redirect('/hod_forgot')

        otp = str(random.randint(100000,999999))

        session['hod_reset_email'] = email
        session['hod_otp'] = otp

        msg = Message(
            "HOD Password Reset OTP",
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )

        msg.body = f"Your OTP for HOD password reset is: {otp}"

        mail.send(msg)

        flash("OTP sent to your email", "success")

        return redirect('/hod_verify_otp')

    return render_template("hod_forgot_password.html")
# ---------------- HOD VERIFY OTP ----------------
@app.route('/hod_verify_otp', methods=['GET','POST'])
def hod_verify_otp():

    if request.method == "POST":

        entered_otp = request.form['otp']
        new_password = request.form['password']

        if entered_otp == session.get('hod_otp'):

            email = session.get('hod_reset_email')

            hod = HOD.query.filter_by(email=email).first()

            if hod:
                hod.password = new_password
                db.session.commit()

            session.pop('hod_otp', None)
            session.pop('hod_reset_email', None)

            flash("Password updated successfully", "success")

            return redirect('/hod_login')

        else:
            flash("Invalid OTP", "error")

    return render_template("hod_verify_otp.html")

# ---------------- PERMANENT CEER HOD SEED ----------------
def seed_ceer():
    ceer_email = "ceer@cmrcet.ac.in"
    ceer = CEER.query.filter_by(email=ceer_email).first()

    if not ceer:
        db.session.add(
            CEER(
                email=ceer_email,
                password="cmr123",
                first_login=True
            )
        )
    db.session.commit()
#-------------------------CEER HOD LOGIN----------------------------------
@app.route('/ceer_login', methods=['GET','POST'])
def ceer_login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        ceer = CEER.query.filter_by(email=email).first()

        if ceer and ceer.password == password:

            session['ceer_email'] = ceer.email

            if ceer.first_login:
                return redirect('/ceer_change_password')

            session['ceer_logged'] = True
            return redirect('/ceer_dashboard')

        flash("Invalid Credentials", "error")
        return redirect('/ceer_login')

    return render_template("hod_login.html")
#----------------------------CEER CHANGE PASSWORD-----------------------------------
@app.route('/ceer_change_password', methods=['GET','POST'])
def ceer_change_password():

    if 'ceer_email' not in session:
        return redirect('/ceer_login')

    if request.method == 'POST':
        new_pass = request.form['new_password']
        ceer = CEER.query.filter_by(email=session['ceer_email']).first()
        ceer.password = new_pass
        ceer.first_login = False
        db.session.commit()

        # remove login session
        session.pop('ceer_email', None)
        session.pop('ceer_logged', None)

        # 🔥 CLEAR OLD FLASH MESSAGES
        session.pop('_flashes', None)

        return redirect('/ceer_login')   # FIXED

    return render_template("ceer_change_password.html")
#---------------------CEER HOD DASHBOARD------------------------------
@app.route('/ceer_dashboard')
def ceer_dashboard():
    if 'ceer_email' not in session:
        return redirect('/ceer_login')
    return render_template("ceer_dashboard.html")
# ---------------- CEER PERMISSION ----------------
@app.route('/ceer_permission')
def ceer_permission():
    if 'ceer_logged' not in session:
        return redirect('/hod_login')
    # show only HOD approved requests
    data = Permission.query.filter_by(hod_status="Approved").order_by(Permission.year.asc()).all()
    return render_template("ceer_permission.html", requests=data)
# ---------------- CEER HISTORY ----------------
@app.route('/ceer_history')
def ceer_history():
    if 'ceer_email' not in session:
        return redirect('/ceer_login')
    teams = {}
    # get all records (latest first)
    records = Permission.query.order_by(Permission.from_date.desc()).all()
    for r in records:
        if r.team_id not in teams:
            members = Permission.query.filter_by(team_id=r.team_id).all()
            ceer_status = members[0].ceer_status
            # -------- STATUS LOGIC --------
            if ceer_status == "Approved (Final Review)":
                initial_status = "Approved"
                final_status = "Approved"
            elif ceer_status == "Approved (Initial Review)":
                initial_status = "Approved"
                final_status = "Pending"
            elif "Rejected" in ceer_status:
                initial_status = "Rejected"
                final_status = "Rejected"
            else:
                initial_status = "Pending"
                final_status = "Pending"
            # -------- STORE TEAM DATA --------
            teams[r.team_id] = {
                "event": r.event_name,
                "leader": r.team_leader,
                "phone": r.contact_number,   # ✅ TEAM LEADER PHONE
                "date": r.from_date,
                "size": len(members),
                "members": members,
                "ceer_initial": initial_status,
                "ceer_final": final_status
            }
    return render_template(
        "ceer_history.html",
        teams=teams.values()
    )
#---------------------CEER APPROVAL DASHBOARD---------------
@app.route('/ceer_approval')
def ceer_approval():

    if 'ceer_email' not in session:
        return redirect('/ceer_login')

    # -------- INITIAL REVIEW --------
    initial_team_ids = db.session.query(Permission.team_id)\
        .filter(Permission.stage == "CEER")\
        .distinct().all()

    initial_review = []

    for team in initial_team_ids:
        members = Permission.query.filter_by(team_id=team.team_id).all()
        initial_review.append(members)


    # -------- FINAL REVIEW --------
    final_team_ids = db.session.query(Permission.team_id)\
        .filter(Permission.stage == "CEER_FINAL")\
        .distinct().all()

    final_review = []

    for team in final_team_ids:

        members = Permission.query.filter_by(team_id=team.team_id).all()

        # ❗ Skip teams already approved or rejected
        if members[0].ceer_status in ["Approved (Final Review)", "Rejected (Final Review)"]:
            continue

        final_review.append(members)

    return render_template(
        "ceer_approval.html",
        initial_review=initial_review,
        final_review=final_review
    )
#-----------------CEER Initial Approval-------------------
@app.route('/ceer_initial_approve/<team_id>')
def ceer_initial_approve(team_id):
    records = Permission.query.filter_by(team_id=team_id).all()
    for r in records:
        r.ceer_status = "Approved (Initial Review)"
        r.stage = "HOD"
    db.session.commit()
    return redirect('/ceer_approval')
#------------------CEER INTIAL REJECT---------------------
@app.route('/ceer_initial_reject/<team_id>')
def ceer_initial_reject(team_id):
    records = Permission.query.filter_by(team_id=team_id).all()
    for r in records:
        r.ceer_status = "Rejected (Initial Review)"
        r.stage = "REJECTED"
    db.session.commit()
    return redirect('/ceer_approval')
#-----------------CEER FINAL Approval-------------------
@app.route('/ceer_final_approve/<team_id>')
def ceer_final_approve(team_id):

    # ✅ only take approved students
    records = Permission.query.filter_by(
        team_id=team_id,
        hod_status="Approved"
    ).all()

    for r in records:
        r.ceer_status = "Approved (Final Review)"
        r.stage = "DIRECTOR"   # move forward

    db.session.commit()

    return redirect('/ceer_approval')
#----------------------CEER FINAL REJECT---------------------------
@app.route('/ceer_final_reject/<team_id>')
def ceer_final_reject(team_id):
    records = Permission.query.filter_by(team_id=team_id).all()
    for r in records:
        r.ceer_status = "Rejected (Final Review)"
        r.stage = "REJECTED"   # THIS removes it from CEER page
    db.session.commit()
    return redirect('/ceer_approval')
#------------------CEER STATUS----------------
@app.route('/ceer_status')
def ceer_status():
    if 'ceer_email' not in session:
        return redirect('/ceer_login')
    records = Permission.query.all()
    teams = {}
    for r in records:
        if r.team_id not in teams:
            members = Permission.query.filter_by(team_id=r.team_id).all()
            teams[r.team_id] = {
                "event": r.event_name,
                "leader": r.team_leader,   # 👈 added
                "size": len(members),
                "ceer_initial": members[0].ceer_status,
                "hod": members[0].hod_status,
                "ceer_final": members[0].ceer_status,
                "director": members[0].director_status
            }

    return render_template("ceer_status.html", teams=teams.values())

#-------------------------HOD DASHBOARD-------------------------
@app.route('/hod_dashboard')
def hod_dashboard():

    if 'hod_email' not in session:
        return redirect('/hod_login')

    hod_dept = session['hod_dept']

    # show ONLY records currently in HOD stage
    records = Permission.query.filter_by(stage="HOD").all()

    teams = {}

    for r in records:
        if r.team_id not in teams:
            teams[r.team_id] = []
        teams[r.team_id].append(r)

    return render_template(
        "hod_dashboard.html",
        teams=teams.values(),
        hod_dept=hod_dept
    )
@app.route('/hod_approvals')
def hod_approvals():

    if 'hod_email' not in session:
        return redirect('/hod_login')

    hod_dept = session['hod_dept']

    records = Permission.query.filter_by(
        stage="HOD",
        hod_group=hod_dept
    ).all()

    teams = {}

    for r in records:
        if r.team_id not in teams:
            members = Permission.query.filter_by(team_id=r.team_id).all()
            teams[r.team_id] = members

    return render_template(
        "hod_approvals.html",
        teams=teams.values(),
        hod_dept=hod_dept
    )
# ---------------- HOD APPROVE ----------------
@app.route('/hod_approve/<int:id>', methods=['POST'])
def hod_approve(id):

    record = Permission.query.get(id)

    # ✅ GET attendance from form
    attendance = request.form.get('attendance')

    # ✅ SAVE attendance (THIS WAS MISSING)
    if attendance:
        record.attendance = attendance

    # ✅ approve ONLY this student
    record.hod_status = "Approved"

    db.session.commit()

    team_records = Permission.query.filter_by(team_id=record.team_id).all()

    # check if ANY still pending
    any_pending = False
    for r in team_records:
        if r.hod_status == "Pending":
            any_pending = True
            break

    # if NO pending → move forward
    if not any_pending:
        for r in team_records:
            if r.hod_status == "Approved":
                r.stage = "CEER_FINAL"
            elif r.hod_status == "Rejected":
                r.stage = "REJECTED"

        db.session.commit()

    return redirect('/hod_approvals')
# ---------------- HOD REJECT ----------------
@app.route('/hod_reject/<int:id>', methods=['POST'])
def hod_reject(id):

    record = Permission.query.get(id)

    # ✅ get attendance ALSO for rejected
    attendance = request.form.get('attendance')

    if attendance:
        record.attendance = attendance

    record.hod_status = "Rejected"
    record.stage = "REJECTED"

    db.session.commit()

    team_records = Permission.query.filter_by(team_id=record.team_id).all()

    any_pending = False
    for r in team_records:
        if r.hod_status == "Pending":
            any_pending = True
            break

    if not any_pending:
        for r in team_records:
            if r.hod_status == "Approved":
                r.stage = "CEER_FINAL"

        db.session.commit()

    return redirect('/hod_approvals')
# ---------------- HOD STATUS ----------------
@app.route('/hod_status')
def hod_status():
    if 'hod_email' not in session:
        return redirect('/hod_login')
    # GET HOD DEPARTMENT
    hod_email = session['hod_email']
    hod_dept = hod_email.split("@")[0]
    # remove numbers like cse1 → cse
    hod_dept = ''.join([i for i in hod_dept if not i.isdigit()])
    hod_dept = hod_dept.strip().upper()
    records = Permission.query.filter(
        Permission.stage.in_(["HOD", "CEER_FINAL", "DIRECTOR"])
    ).all()
    teams = {}
    for r in records:
        if r.team_id not in teams:
            members = Permission.query.filter_by(team_id=r.team_id).all()
            # check if all HODs approved
            all_hods = all(m.hod_status == "Approved" for m in members)
            teams[r.team_id] = {
                "event": r.event_name,
                "leader": r.team_leader,
                "size": len(members),
                "other_hods": "True" if all_hods else "False",
                "ceer_final": members[0].ceer_status,
                "director": members[0].director_status
            }
    return render_template("hod_status.html", teams=teams.values())
# ---------------- HOD HISTORY ----------------
@app.route('/hod_history')
def hod_history():
    if 'hod_email' not in session:
        return redirect('/hod_login')
    teams = {}
    records = Permission.query.order_by(Permission.from_date.desc()).all()
    for r in records:
        if r.team_id not in teams:
            members = Permission.query.filter_by(team_id=r.team_id).all()
            teams[r.team_id] = {
                "event": r.event_name,
                "leader": r.team_leader,
                "date": r.from_date,
                "size": len(members),
                "members": members,
                "hod": members[0].hod_status,
                "ceer_final": members[0].ceer_status
            }
    return render_template(
        "hod_history.html",
        teams=teams.values()
    )
#-------------------DIRECTOR SEED---------------------------
def seed_director():
    director_email = "director@cmrcet.ac.in"
    director = Director.query.filter_by(email=director_email).first()
    if not director:
        db.session.add(
            Director(
                email=director_email,
                password="cmr123",
                first_login=True
            )
        )
        db.session.commit()
#-----------------------------DIRECTOR LOGIN-----------------------------
@app.route('/director_login', methods=['GET','POST'])
def director_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        director = Director.query.filter_by(email=email).first()
        if director and director.password == password:
            session['director_email'] = director.email
            if director.first_login:
                return redirect('/director_change_password')
            session['director_logged'] = True
            return redirect('/director_dashboard')
        flash("Invalid Credentials")
    return render_template("director_login.html")
#---------------------------------DIRECTOR CHANGE PASS-------------------------------
@app.route('/director_change_password', methods=['GET','POST'])
def director_change_password():
    if 'director_email' not in session:
        return redirect('/director_login')
    if request.method == 'POST':
        new_pass = request.form['new_password']
        director = Director.query.filter_by(email=session['director_email']).first()
        director.password = new_pass
        director.first_login = False
        db.session.commit()
        session.clear()
        return redirect('/director_login')
    return render_template("director_change_password.html")
#---------------------------DIRECTOR DASHBOARD-------------------
@app.route('/director_dashboard')
def director_dashboard():
    if 'director_email' not in session:
        return redirect('/director_login')
    return render_template("director_dashboard.html")
#------------DIRECTOR APPROVALS------------------------------
@app.route('/director_approvals')
def director_approvals():

    if 'director_email' not in session:
        return redirect('/director_login')

    # only teams ready for director
    records = Permission.query.filter_by(stage="DIRECTOR").all()

    events = {}

    for r in records:

        event = r.event_name

        if event not in events:
            events[event] = {}

        if r.team_id not in events[event]:

            members = Permission.query.filter_by(team_id=r.team_id).all()

            events[event][r.team_id] = {
                "leader": r.team_leader,
                "phone": r.contact_number,
                "members": members
            }

    return render_template("director_approvals.html", events=events)
# ------------ DIRECTOR APPROVE ----------------
@app.route('/director_approve/<team_id>')
def director_approve(team_id):

    # ✅ take only HOD approved students
    records = Permission.query.filter_by(
        team_id=team_id,
        hod_status="Approved"
    ).all()

    for r in records:
        r.director_status = "Approved"
        r.stage = "FACULTY"   # move forward

    db.session.commit()

    return redirect('/director_approvals')
#--------------------------DIRECTOR REJECT-----------------
@app.route('/director_reject/<team_id>')
def director_reject(team_id):
    records = Permission.query.filter_by(
        team_id=team_id,
        hod_status="Approved"
    ).all()
    for r in records:
        r.director_status = "Rejected"
        r.stage = "REJECTED"
    db.session.commit()
    return redirect('/director_approvals')
#----------------------------DIRECTOR HISTORY-----------------
@app.route('/director_history')
def director_history():
    if 'director_email' not in session:
        return redirect('/director_login')
    # get only requests already processed by director
    records = Permission.query.filter(
        Permission.director_status != "Pending"
    ).all()
    events = {}
    for r in records:
        event = r.event_name
        team_id = r.team_id
        # create event if not exists
        if event not in events:
            events[event] = {}
        # create team inside event
        if team_id not in events[event]:
            members = Permission.query.filter_by(team_id=team_id).all()
            events[event][team_id] = {
                "leader": r.team_leader,
                "phone": r.contact_number,
                "director_status": r.director_status,
                "members": members
            }
    return render_template(
        "director_history.html",
        events=events
    )
#-----------------------FACULTY SEED---------------
def seed_faculty():
    faculty_emails = [
        "faculty1@cmrcet.ac.in",
        "faculty2@cmrcet.ac.in",
        "faculty3@cmrcet.ac.in",
        "faculty4@cmrcet.ac.in",
        "faculty5@cmrcet.ac.in"
    ]
    for mail in faculty_emails:
        exists = Faculty.query.filter_by(email=mail).first()
        if not exists:
            db.session.add(
                Faculty(
                    email=mail,
                    password="cmr123",
                    first_login=True
                )
            )
    db.session.commit()
#----------------------------------FACULTY LOGIN------------------------
@app.route('/faculty_login', methods=['GET','POST'])
def faculty_login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        faculty = Faculty.query.filter_by(email=email).first()

        if faculty and faculty.password == password:

            session['faculty_email'] = faculty.email

            # first login → force password change
            if faculty.first_login:
                return redirect(url_for('faculty_change_password'))

            return redirect(url_for('faculty_dashboard'))

        flash("Invalid Credentials","error")
        return redirect(url_for('faculty_login'))

    return render_template("faculty_login.html")
#---------------------FACULTY CHANGE PASSWORD----------------------------
@app.route('/faculty_change_password', methods=['GET','POST'])
def faculty_change_password():

    if 'faculty_email' not in session:
        return redirect(url_for('faculty_login'))

    if request.method == 'POST':

        newpass = request.form.get('newpass')

        faculty = Faculty.query.filter_by(email=session['faculty_email']).first()

        if faculty:
            faculty.password = newpass
            faculty.first_login = False

            db.session.commit()

        session.clear()

        flash("Password changed successfully. Please login again.", "success")

        return redirect(url_for('faculty_login'))

    return render_template("faculty_change_password.html")
#-------------------FACULTY DASHBOARD--------------
@app.route('/faculty_dashboard')
def faculty_dashboard():
    if 'faculty_email' not in session:
        return redirect(url_for('faculty_login'))
    years = [1,2,3,4]
    return render_template(
        "faculty_dashboard.html",
        years=years
    )
#----------------------FACULTY DEPARTMENTS-----------------------
@app.route('/faculty_year/<int:year>')
def faculty_year(year):
    if 'faculty_email' not in session:
        return redirect(url_for('faculty_login'))
    # departments logic
    if year in [1,2]:
        departments = ["CSE","CSM","CIVIL","MECH","CSD","ECE","EEE"]
    else:
        departments = ["CSE","CSM","CIVIL","MECH","CSD","CSC","ECE","EEE"]
    return render_template(
        "faculty_departments.html",
        year=year,
        departments=departments
    )
#-----------------FACULTY SECTIONS---------------------
@app.route('/faculty_sections/<int:year>/<dept>')
def faculty_sections(year, dept):

    if 'faculty_email' not in session:
        return redirect(url_for('faculty_login'))

    # section counts
    section_counts = {
        "CSE":7,
        "CSM":6,
        "CSD":3,
        "CSC":2,
        "ECE":4,
        "EEE":1,
        "CIVIL":1,
        "MECH":2
    }

    # remove CSC for 1st & 2nd year
    if year in [1,2] and dept == "CSC":
        flash("CSC not available for this year","error")
        return redirect(url_for('faculty_year', year=year))

    count = section_counts.get(dept,0)

    sections = []

    for i in range(1, count+1):
        sections.append(i)

    return render_template(
        "faculty_sections.html",
        year=year,
        dept=dept,
        sections=sections
    )
# ---------------- FACULTY STUDENTS ----------------
@app.route('/faculty_students/<int:year>/<dept>/<int:section>')
def faculty_students(year, dept, section):

    if 'faculty_email' not in session:
        return redirect('/faculty_login')

    # convert section number → alphabet
    section_letter = chr(64 + section)

    students = Permission.query.filter_by(
        year=year,
        department=dept,
        section=section_letter,
        director_status="Approved"   # IMPORTANT
    ).all()
    return render_template(
        "faculty_students.html",
        students=students,
        year=year,
        dept=dept,
        section=section_letter
    )
@app.route('/reset_permissions')
def reset_permissions():

    Permission.query.delete()
    db.session.commit()

    return "All hackathon records deleted"
@app.route('/reset_all_users')
def reset_all_users():
    # delete all users
    Student.query.delete()
    HOD.query.delete()
    Faculty.query.delete()
    Director.query.delete()
    CEER.query.delete()
    db.session.commit()
    return "All logins deleted"
@app.route('/add_faculty')
def add_faculty():

    for i in range(1, 6):
        email = f"faculty{i}@cmrcet.ac.in"

        exists = Faculty.query.filter_by(email=email).first()

        if not exists:
            db.session.add(Faculty(
                email=email,
                password="cmr123",
                first_login=True
            ))

    db.session.commit()

    return "Faculty added successfully"

#--------------------MAIN------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_hods()
        seed_ceer()
        seed_director()
        seed_faculty()
    app.run(host="0.0.0.0", port=10000)