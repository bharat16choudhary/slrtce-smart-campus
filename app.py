"""
SLRTCE Smart Campus — app.py  (Backend + DB Models)
All SQLAlchemy models AND Flask routes live in this one file.
Every route renders the single templates/index.html.
Run:  python app.py
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import datetime, date
from werkzeug.security import check_password_hash, generate_password_hash
import os
import uuid

app = Flask(__name__)
app.secret_key = 'slrtce_smart_campus_2024_secret'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'slrtce.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_upload(file, subfolder='general', allowed_ext=None):
    """Save an uploaded file to static/uploads/<subfolder>/ and return the relative path."""
    if not file or file.filename == '':
        return None
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if allowed_ext and ext not in allowed_ext:
        return None
    filename = f"{uuid.uuid4().hex}.{ext}"
    folder = os.path.join(UPLOAD_FOLDER, subfolder)
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, filename))
    return f"uploads/{subfolder}/{filename}"

# ══════════════════════════════════════════════════════════════════════════════
#  DATABASE MODELS
# ══════════════════════════════════════════════════════════════════════════════

class User(db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    uid        = db.Column(db.String(50), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(150))
    phone      = db.Column(db.String(20))
    photo      = db.Column(db.String(300))
    role       = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all,delete')
    teacher_profile = db.relationship('TeacherProfile', backref='user', uselist=False, cascade='all,delete')
    admin_profile   = db.relationship('AdminProfile',   backref='user', uselist=False, cascade='all,delete')


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    roll_no = db.Column(db.String(10))
    branch  = db.Column(db.String(20))
    div     = db.Column(db.String(5))
    year    = db.Column(db.String(5))
    dob     = db.Column(db.String(20))
    address = db.Column(db.String(300))


class TeacherProfile(db.Model):
    __tablename__ = 'teacher_profiles'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    branch      = db.Column(db.String(20))
    subject     = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    employee_id = db.Column(db.String(20))


class AdminProfile(db.Model):
    __tablename__ = 'admin_profiles'
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_desc = db.Column(db.String(100))


class TimetableEntry(db.Model):
    __tablename__ = 'timetable_entries'
    id         = db.Column(db.Integer, primary_key=True)
    branch     = db.Column(db.String(20), nullable=False)
    div        = db.Column(db.String(5))
    year       = db.Column(db.String(5))
    day        = db.Column(db.String(15), nullable=False)
    slot_index = db.Column(db.Integer, nullable=False)
    slot_label = db.Column(db.String(20))
    subject    = db.Column(db.String(100))


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    branch     = db.Column(db.String(20))
    div        = db.Column(db.String(5))
    subject    = db.Column(db.String(100))
    date       = db.Column(db.Date, nullable=False)
    status     = db.Column(db.String(10), nullable=False, default='absent')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', foreign_keys=[student_id], backref='attendance_as_student')
    teacher = db.relationship('User', foreign_keys=[teacher_id])


class StudyMaterial(db.Model):
    __tablename__ = 'study_materials'
    id            = db.Column(db.Integer, primary_key=True)
    uploaded_by   = db.Column(db.Integer, db.ForeignKey('users.id'))
    branch        = db.Column(db.String(20))
    subject       = db.Column(db.String(100), nullable=False)
    module        = db.Column(db.String(100))
    material_type = db.Column(db.String(30))
    name          = db.Column(db.String(200), nullable=False)
    file_path     = db.Column(db.String(300))
    url           = db.Column(db.String(500))
    uploaded_at   = db.Column(db.DateTime, default=datetime.utcnow)
    uploader      = db.relationship('User', foreign_keys=[uploaded_by])


class Assignment(db.Model):
    __tablename__ = 'assignments'
    id         = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    branch     = db.Column(db.String(20), nullable=False)
    div        = db.Column(db.String(5), nullable=False)
    subject    = db.Column(db.String(100), nullable=False)
    module     = db.Column(db.String(100))
    title      = db.Column(db.String(300), nullable=False)
    marks      = db.Column(db.Integer, default=10)
    due_date   = db.Column(db.String(30))
    file_path  = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    teacher     = db.relationship('User', foreign_keys=[teacher_id])
    submissions = db.relationship('AssignmentSubmission', backref='assignment', cascade='all,delete')


class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submissions'
    id            = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path     = db.Column(db.String(300))
    submitted_at  = db.Column(db.DateTime, default=datetime.utcnow)
    marks_given   = db.Column(db.Integer)
    student       = db.relationship('User', foreign_keys=[student_id])


class Notice(db.Model):
    __tablename__ = 'notices'
    id          = db.Column(db.Integer, primary_key=True)
    posted_by   = db.Column(db.Integer, db.ForeignKey('users.id'))
    notice_type = db.Column(db.String(20), nullable=False)
    branch      = db.Column(db.String(20))
    div         = db.Column(db.String(5))
    subject     = db.Column(db.String(100))
    title       = db.Column(db.String(300), nullable=False)
    body        = db.Column(db.Text, nullable=False)
    from_name   = db.Column(db.String(100))
    photo_path  = db.Column(db.String(300))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    poster      = db.relationship('User', foreign_keys=[posted_by])

    @property
    def date(self):
        return self.created_at.strftime('%d %b %Y') if self.created_at else ''

    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'body': self.body,
                'subject': self.subject, 'from': self.from_name or '',
                'date': self.date, 'notice_type': self.notice_type,
                'branch': self.branch, 'div': self.div,
                'photo_path': self.photo_path or ''}


class Complaint(db.Model):
    __tablename__ = 'complaints'
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    from_name  = db.Column(db.String(100))
    subject    = db.Column(db.String(200), nullable=False)
    body       = db.Column(db.Text, nullable=False)
    status     = db.Column(db.String(20), default='pending')
    photo_path = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    student    = db.relationship('User', foreign_keys=[student_id])

    @property
    def date(self):
        return self.created_at.strftime('%d %b %Y') if self.created_at else ''

    def to_dict(self):
        return {'id': self.id, 'from': self.from_name or '', 'subject': self.subject,
                'body': self.body, 'status': self.status, 'date': self.date,
                'photo_path': self.photo_path or ''}


class Exam(db.Model):
    __tablename__ = 'exams'
    id        = db.Column(db.Integer, primary_key=True)
    branch    = db.Column(db.String(20))
    div       = db.Column(db.String(5))
    subject   = db.Column(db.String(100), nullable=False)
    exam_type = db.Column(db.String(20))
    date      = db.Column(db.String(30))
    time      = db.Column(db.String(20))
    venue     = db.Column(db.String(100))


class ExamMark(db.Model):
    __tablename__ = 'exam_marks'
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject    = db.Column(db.String(100), nullable=False)
    exam_type  = db.Column(db.String(20))
    marks      = db.Column(db.Float)
    max_marks  = db.Column(db.Float, default=20)
    student    = db.relationship('User', foreign_keys=[student_id])


class CalendarEvent(db.Model):
    __tablename__ = 'calendar_events'
    id         = db.Column(db.Integer, primary_key=True)
    date       = db.Column(db.String(20), nullable=False)
    title      = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(20))


# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

BRANCHES   = ['CMPN', 'IT', 'EXTC', 'CIVIL', 'MECH']
DIVISIONS  = ['A', 'B', 'C']
SUBJECTS   = ['Data Structures', 'DBMS', 'Mathematics III', 'Operating Systems', 'Computer Networks']
TIME_SLOTS = ['9:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-1:00', '1:00-2:00', '2:00-3:00']
FAQS = [
    {'q': 'How do I get my hall ticket?',
     'a': 'Hall tickets are available in the Exams section. Download them 7 days before the exam.'},
    {'q': 'How can I check my attendance?',
     'a': 'Your attendance is visible on the Dashboard and in full detail on the Attendance page.'},
    {'q': 'How to submit an assignment?',
     'a': 'Go to Assignments, select your subject, and click Submit next to the due assignment.'},
    {'q': 'I forgot my password. What to do?',
     'a': 'Contact your department coordinator or admin office with your UID and ID proof.'},
    {'q': 'How to download study materials?',
     'a': 'Go to Study Material, select your subject, and choose the material type.'},
]

# ══════════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

@app.context_processor
def inject_session():
    return dict(session=session)


def get_user(uid):
    return User.query.filter_by(uid=uid).first()


def build_timetable(branch='CMPN', div='A'):
    entries = TimetableEntry.query.filter_by(branch=branch, div=div).order_by(
        TimetableEntry.day, TimetableEntry.slot_index).all()
    timetable = {}
    for e in entries:
        timetable.setdefault(e.day, [None] * 6)
        timetable[e.day][e.slot_index] = e.subject
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    return {d: timetable.get(d, ['---'] * 6) for d in day_order if d in timetable}


def build_attendance_summary(student_id):
    records = AttendanceRecord.query.filter_by(student_id=student_id).all()
    subject_map = {}
    for r in records:
        subject_map.setdefault(r.subject, {'present': 0, 'total': 0})
        subject_map[r.subject]['total'] += 1
        if r.status == 'present':
            subject_map[r.subject]['present'] += 1
    total_present = sum(v['present'] for v in subject_map.values())
    total_classes = sum(v['total'] for v in subject_map.values())
    pct = round((total_present / total_classes * 100) if total_classes else 0)
    return {'monthly': subject_map,
            'overall': {'present': total_present, 'total': total_classes},
            'monthly_percent': pct, 'overall_percent': pct}


def build_student_list(branch, division):
    profiles = StudentProfile.query.filter_by(branch=branch, div=division).all()
    result = []
    for p in profiles:
        u = p.user
        att = build_attendance_summary(u.id)
        total, present = att['overall']['total'], att['overall']['present']
        pct = round((present / total * 100) if total else 0)
        result.append({'roll_no': p.roll_no, 'name': u.name, 'uid': u.uid, 'photo': u.photo,
                       'attendance': {'present': present, 'total': total, 'percent': pct}})
    return result


def build_exam_data(student_id):
    upcoming = Exam.query.filter_by(branch='CMPN', div='A').all()
    iat_raw  = ExamMark.query.filter(ExamMark.student_id == student_id,
                                     ExamMark.exam_type.in_(['iat1', 'iat2'])).all()
    sem_raw  = ExamMark.query.filter(ExamMark.student_id == student_id,
                                     ExamMark.exam_type.in_(['sem1', 'sem2'])).all()
    iat_by_subj = {}
    for m in iat_raw:
        iat_by_subj.setdefault(m.subject, {'iat1': None, 'iat2': None, 'max': m.max_marks})
        iat_by_subj[m.subject][m.exam_type] = m.marks
    sem_by_subj = {}
    for m in sem_raw:
        sem_by_subj.setdefault(m.subject, {'sem1': None, 'sem2': None, 'max': m.max_marks})
        sem_by_subj[m.subject][m.exam_type] = m.marks
    return {
        'upcoming':  [{'subject': e.subject, 'date': e.date, 'time': e.time,
                        'type': e.exam_type, 'venue': e.venue} for e in upcoming],
        'iat_marks': [{'subject': s, **v} for s, v in iat_by_subj.items()],
        'scorecard': [{'subject': s, **v} for s, v in sem_by_subj.items()],
        'kts': []
    }


def build_study_material(subject):
    mats = StudyMaterial.query.filter_by(subject=subject).all()
    result = {'handwritten': [], 'ppt_pdf': [], 'reference_books': [], 'youtube': []}
    for m in mats:
        if m.material_type == 'youtube':
            result['youtube'].append({'name': m.name, 'url': m.url})
        else:
            result.setdefault(m.material_type, []).append({
                'name': m.name, 'file': m.file_path or '#',
                'date': m.uploaded_at.strftime('%d %b %Y') if m.uploaded_at else ''})
    return result


def build_assignments(branch, div):
    assigns = Assignment.query.filter_by(branch=branch, div=div).all()
    result = []
    for a in assigns:
        subs = AssignmentSubmission.query.filter_by(assignment_id=a.id).all()
        result.append({'id': a.id, 'subject': a.subject, 'module': a.module,
                       'title': a.title, 'marks': a.marks, 'due_date': a.due_date,
                       'file_path': a.file_path or '',
                       'submitted_by': [s.student.uid for s in subs],
                       'marks_given': {s.student.uid: s.marks_given for s in subs},
                       'submission_files': {s.student.uid: s.file_path for s in subs}})
    return result


def _teacher_dict(user):
    p = user.teacher_profile
    return {'name': user.name, 'email': user.email, 'phone': user.phone, 'photo': user.photo,
            'branch': p.branch if p else '', 'subject': p.subject if p else '',
            'designation': p.designation if p else '', 'employee_id': p.employee_id if p else ''}

# ══════════════════════════════════════════════════════════════════════════════
#  AUTH DECORATOR
# ══════════════════════════════════════════════════════════════════════════════

def login_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('user_role') != role:
                return redirect(url_for('landing'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ══════════════════════════════════════════════════════════════════════════════
#  ROUTES — all render index.html with a 'page' variable
# ══════════════════════════════════════════════════════════════════════════════

# ── Landing ──────────────────────────────────────────────────────────────────
@app.route('/')
def landing():
    return render_template('index.html', page='landing')

# ── Auth ─────────────────────────────────────────────────────────────────────
@app.route('/login/student', methods=['GET', 'POST'])
def student_login():
    error = None
    if request.method == 'POST':
        uid, pwd = request.form.get('uid','').strip(), request.form.get('password','').strip()
        user = User.query.filter_by(uid=uid, role='student').first()
        if user and check_password_hash(user.password, pwd):
            session.clear()
            session.update({'user_role':'student','uid':uid,'user_id':user.id,'user_name':user.name})
            return redirect(url_for('student_dashboard'))
        error = 'Invalid UID or Password.'
    return render_template('index.html', page='student_login', error=error)


@app.route('/login/faculty', methods=['GET', 'POST'])
def faculty_login():
    error = None
    if request.method == 'POST':
        uid, pwd = request.form.get('uid','').strip(), request.form.get('password','').strip()
        user = User.query.filter_by(uid=uid, role='teacher').first()
        if user and check_password_hash(user.password, pwd):
            session.clear()
            session.update({'user_role':'teacher','uid':uid,'user_id':user.id,'user_name':user.name})
            return redirect(url_for('teacher_dashboard'))
        error = 'Invalid UID or Password.'
    return render_template('index.html', page='faculty_login', error=error)


@app.route('/login/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        uid, pwd = request.form.get('uid','').strip(), request.form.get('password','').strip()
        user = User.query.filter_by(uid=uid, role='admin').first()
        if user and check_password_hash(user.password, pwd):
            session.clear()
            session.update({'user_role':'admin','uid':uid,'user_id':user.id,'user_name':user.name})
            return redirect(url_for('admin_dashboard'))
        error = 'Invalid UID or Password.'
    return render_template('index.html', page='admin_login', error=error)


@app.route('/logout')
def logout():
    role = session.get('user_role','student')
    session.clear()
    return redirect(url_for('faculty_login' if role=='teacher' else
                             'admin_login'  if role=='admin'   else 'student_login'))

# ── Student pages ─────────────────────────────────────────────────────────────
@app.route('/student/dashboard')
@login_required('student')
def student_dashboard():
    user    = get_user(session['uid'])
    profile = user.student_profile
    assignments_raw = Assignment.query.filter_by(
        branch=profile.branch or 'CMPN', div=profile.div or 'A').all()
    assignments = []
    for a in assignments_raw:
        sub = AssignmentSubmission.query.filter_by(
            assignment_id=a.id, student_id=user.id).first()
        assignments.append({'id':a.id,'subject':a.subject,'module':a.module,
                            'title':a.title,'marks':a.marks,'due_date':a.due_date,
                            'status':'submitted' if sub else 'pending'})
    return render_template('index.html', page='student_dashboard',
        student={'name':user.name,'email':user.email,'phone':user.phone,'photo':user.photo,
                 'branch':profile.branch or '','div':profile.div or '',
                 'roll_no':profile.roll_no or '','year':profile.year or '',
                 'dob':profile.dob or '','address':profile.address or ''},
        timetable=build_timetable(profile.branch or 'CMPN', profile.div or 'A'),
        time_slots=TIME_SLOTS,
        attendance=build_attendance_summary(user.id),
        admin_notices=[n.to_dict() for n in Notice.query.filter_by(notice_type='admin')
                       .order_by(Notice.created_at.desc()).limit(3).all()],
        teacher_notices=[n.to_dict() for n in Notice.query.filter_by(notice_type='teacher')
                         .order_by(Notice.created_at.desc()).limit(3).all()],
        assignments=assignments, subjects=SUBJECTS)


@app.route('/student/study-material')
@login_required('student')
def student_study_material():
    user    = get_user(session['uid'])
    profile = user.student_profile
    subject = request.args.get('subject', '')
    subjects = [s[0] for s in db.session.query(StudyMaterial.subject).distinct().all()] or SUBJECTS
    return render_template('index.html', page='student_study_material',
        student={'name':user.name,'photo':user.photo,
                 'branch':profile.branch or '','div':profile.div or ''},
        subjects=subjects, selected_subject=subject,
        material=build_study_material(subject) if subject else {})


@app.route('/student/exams')
@login_required('student')
def student_exams():
    user    = get_user(session['uid'])
    profile = user.student_profile
    return render_template('index.html', page='student_exams',
        student={'name':user.name,'photo':user.photo,'branch':profile.branch or ''},
        exam_data=build_exam_data(user.id))


@app.route('/student/calendar')
@login_required('student')
def student_calendar():
    user    = get_user(session['uid'])
    profile = user.student_profile
    events  = [{'date':e.date,'title':e.title,'type':e.event_type}
               for e in CalendarEvent.query.order_by(CalendarEvent.date).all()]
    return render_template('index.html', page='student_calendar',
        student={'name':user.name,'photo':user.photo,'branch':profile.branch or ''},
        events=events)


@app.route('/student/assignments')
@login_required('student')
def student_assignments():
    user    = get_user(session['uid'])
    profile = user.student_profile
    subject_filter = request.args.get('subject', '')
    query = Assignment.query.filter_by(branch=profile.branch or 'CMPN',
                                       div=profile.div or 'A')
    if subject_filter:
        query = query.filter_by(subject=subject_filter)
    assignments, student_marks = [], {}
    for a in query.all():
        sub = AssignmentSubmission.query.filter_by(
            assignment_id=a.id, student_id=user.id).first()
        assignments.append({'id':a.id,'subject':a.subject,'module':a.module,
                            'title':a.title,'marks':a.marks,'due_date':a.due_date,
                            'status':'submitted' if sub else 'pending'})
        if sub and sub.marks_given is not None:
            student_marks[f"{a.id}-{user.uid}"] = sub.marks_given
    return render_template('index.html', page='student_assignments',
        student={'name':user.name,'photo':user.photo,
                 'branch':profile.branch or '','div':profile.div or ''},
        assignments=assignments, subjects=SUBJECTS,
        selected_subject=subject_filter, student_marks=student_marks)


@app.route('/student/submit-assignment/<int:assignment_id>', methods=['POST'])
@login_required('student')
def submit_assignment(assignment_id):
    user = get_user(session['uid'])
    existing = AssignmentSubmission.query.filter_by(
        assignment_id=assignment_id, student_id=user.id).first()
    if not existing:
        file_path = save_upload(
            request.files.get('file'),
            subfolder='assignments',
            allowed_ext={'pdf', 'doc', 'docx', 'zip'})
        db.session.add(AssignmentSubmission(
            assignment_id=assignment_id, student_id=user.id,
            file_path=file_path))
        db.session.commit()
    return redirect(url_for('student_assignments'))


@app.route('/student/noticeboard')
@login_required('student')
def student_noticeboard():
    user    = get_user(session['uid'])
    profile = user.student_profile
    return render_template('index.html', page='student_noticeboard',
        student={'name':user.name,'photo':user.photo,'branch':profile.branch or ''},
        admin_notices=[n.to_dict() for n in Notice.query.filter_by(notice_type='admin')
                       .order_by(Notice.created_at.desc()).all()],
        teacher_notices=[n.to_dict() for n in Notice.query.filter_by(notice_type='teacher')
                         .order_by(Notice.created_at.desc()).all()])


@app.route('/student/support', methods=['GET', 'POST'])
@login_required('student')
def student_support():
    user    = get_user(session['uid'])
    profile = user.student_profile
    success = False
    if request.method == 'POST':
        subject = request.form.get('subject','')
        body    = request.form.get('body','')
        if subject and body:
            photo_path = save_upload(
                request.files.get('photo'),
                subfolder='complaints',
                allowed_ext={'jpg', 'jpeg', 'png', 'gif', 'webp'})
            db.session.add(Complaint(student_id=user.id,
                           from_name=f"{user.name} ({user.uid})",
                           subject=subject, body=body, status='pending',
                           photo_path=photo_path))
            db.session.commit()
            success = True
    return render_template('index.html', page='student_support',
        student={'name':user.name,'photo':user.photo,'branch':profile.branch or ''},
        faqs=FAQS, success=success)

# ── Teacher pages ─────────────────────────────────────────────────────────────
@app.route('/teacher/dashboard')
@login_required('teacher')
def teacher_dashboard():
    user    = get_user(session['uid'])
    teacher = _teacher_dict(user)
    first_student = User.query.filter_by(role='student').first()
    return render_template('index.html', page='teacher_dashboard',
        teacher=teacher,
        timetable=build_timetable(teacher['branch'] or 'CMPN'),
        time_slots=TIME_SLOTS,
        attendance=build_attendance_summary(first_student.id if first_student else 0),
        admin_notices=[n.to_dict() for n in Notice.query.filter_by(notice_type='admin')
                       .order_by(Notice.created_at.desc()).limit(3).all()],
        complaints=[c.to_dict() for c in Complaint.query.order_by(
                    Complaint.created_at.desc()).limit(3).all()],
        branches=BRANCHES, divisions=DIVISIONS)


@app.route('/teacher/take-attendance', methods=['GET', 'POST'])
@login_required('teacher')
def teacher_take_attendance():
    user     = get_user(session['uid'])
    teacher  = _teacher_dict(user)
    branch   = request.args.get('branch', '')
    division = request.args.get('division', '')
    students = []
    if branch and division:
        students = build_student_list(branch, division) or [
            {'roll_no':f'{i:02d}','name':f'Student {i}','uid':f'STU{i:03d}',
             'photo':f'https://ui-avatars.com/api/?name=S{i}&background=E8B84B&color=4A4A4A&size=100&bold=true'}
            for i in range(1, 11)]
    return render_template('index.html', page='teacher_take_attendance',
        teacher=teacher, students=students, branch=branch, division=division,
        branches=BRANCHES, divisions=DIVISIONS, subjects=SUBJECTS)


@app.route('/teacher/submit-attendance', methods=['POST'])
@login_required('teacher')
def submit_attendance():
    data     = request.get_json()
    subject  = data.get('subject','')
    att_date = datetime.strptime(data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
    teacher  = get_user(session['uid'])
    count    = 0
    for uid, status in data.get('attendance', {}).items():
        student = User.query.filter_by(uid=uid, role='student').first()
        if not student:
            continue
        rec = AttendanceRecord.query.filter_by(
            student_id=student.id, subject=subject, date=att_date).first()
        if rec:
            rec.status = status
        else:
            rec = AttendanceRecord(student_id=student.id, teacher_id=teacher.id,
                                   branch=data.get('branch',''), div=data.get('division',''),
                                   subject=subject, date=att_date, status=status)
            db.session.add(rec)
        if status == 'present':
            count += 1
    db.session.commit()
    return jsonify({'success': True, 'present': count, 'total': len(data.get('attendance',{}))})


@app.route('/teacher/attendance-list')
@login_required('teacher')
def teacher_attendance_list():
    user     = get_user(session['uid'])
    teacher  = _teacher_dict(user)
    branch   = request.args.get('branch', 'CMPN')
    division = request.args.get('division', 'A')
    students = build_student_list(branch, division) or [
        {'roll_no':f'{i:02d}','name':f'Student {i}','uid':f'STU{i:03d}',
         'photo':f'https://ui-avatars.com/api/?name=S{i}&background=E8B84B&color=4A4A4A&size=100&bold=true',
         'attendance':{'present':i+10,'total':22,'percent':round(((i+10)/22)*100)}}
        for i in range(1, 11)]
    return render_template('index.html', page='teacher_attendance_list',
        teacher=teacher, students=students, branch=branch, division=division,
        branches=BRANCHES, divisions=DIVISIONS)


@app.route('/teacher/send-notice', methods=['GET', 'POST'])
@login_required('teacher')
def teacher_send_notice():
    user    = get_user(session['uid'])
    teacher = _teacher_dict(user)
    success = False
    if request.method == 'POST':
        title = request.form.get('title','')
        body  = request.form.get('body','')
        if title and body:
            photo_path = save_upload(
                request.files.get('photo'),
                subfolder='notices',
                allowed_ext={'jpg', 'jpeg', 'png', 'gif', 'webp'})
            db.session.add(Notice(posted_by=user.id, notice_type='teacher',
                branch=request.form.get('branch',''), div=request.form.get('division',''),
                subject=request.form.get('subject',''),
                title=title, body=body, from_name=user.name,
                photo_path=photo_path))
            db.session.commit()
            success = True
    return render_template('index.html', page='teacher_send_notice',
        teacher=teacher, branches=BRANCHES, divisions=DIVISIONS,
        subjects=SUBJECTS, success=success)


@app.route('/teacher/study-material', methods=['GET', 'POST'])
@login_required('teacher')
def teacher_study_material():
    user    = get_user(session['uid'])
    teacher = _teacher_dict(user)
    success = False
    if request.method == 'POST':
        subject  = request.form.get('subject','')
        module   = request.form.get('module','')
        mtype    = request.form.get('material_type','')
        name     = request.form.get('name','')
        url      = request.form.get('url','')
        if subject and name and mtype:
            db.session.add(StudyMaterial(
                uploaded_by=user.id, branch=teacher['branch'],
                subject=subject, module=module, material_type=mtype,
                name=f"{module} - {name}" if module else name,
                file_path='#' if mtype != 'youtube' else None,
                url=url if mtype == 'youtube' else None))
            db.session.commit()
            success = True
    return render_template('index.html', page='teacher_study_material',
        teacher=teacher, branches=BRANCHES, divisions=DIVISIONS,
        subjects=SUBJECTS, success=success)


@app.route('/teacher/assignments')
@login_required('teacher')
def teacher_assignments():
    user    = get_user(session['uid'])
    teacher = _teacher_dict(user)
    branch  = request.args.get('branch', teacher['branch'] or 'CMPN')
    div     = request.args.get('division', 'A')
    class_key = f"{branch}-{div}"
    return render_template('index.html', page='teacher_assignments',
        teacher=teacher, branches=BRANCHES, divisions=DIVISIONS, subjects=SUBJECTS,
        assignments={branch: {class_key: build_assignments(branch, div)}})


@app.route('/teacher/upload-assignment', methods=['POST'])
@login_required('teacher')
def teacher_upload_assignment():
    user    = get_user(session['uid'])
    title   = request.form.get('title','')
    subject = request.form.get('subject','')
    if title and subject:
        file_path = save_upload(
            request.files.get('file'),
            subfolder='assignment_questions',
            allowed_ext={'pdf', 'doc', 'docx'})
        db.session.add(Assignment(teacher_id=user.id,
            branch=request.form.get('branch','CMPN'),
            div=request.form.get('division','A'),
            subject=subject, module=request.form.get('module',''),
            title=title, marks=int(request.form.get('marks','10')),
            due_date=request.form.get('due_date',''),
            file_path=file_path))
        db.session.commit()
    return redirect(url_for('teacher_assignments'))


@app.route('/teacher/check-assignments')
@login_required('teacher')
def teacher_check_assignments():
    user     = get_user(session['uid'])
    teacher  = _teacher_dict(user)
    branch   = request.args.get('branch', 'CMPN')
    division = request.args.get('division', 'A')
    return render_template('index.html', page='teacher_check_assignments',
        teacher=teacher, branches=BRANCHES, divisions=DIVISIONS,
        assignments=build_assignments(branch, division),
        student_list=build_student_list(branch, division),
        branch=branch, division=division)


@app.route('/teacher/give-marks', methods=['POST'])
@login_required('teacher')
def give_marks():
    data    = request.get_json()
    student = User.query.filter_by(uid=data.get('student_uid','')).first()
    if not student:
        return jsonify({'success': False, 'error': 'Student not found'})
    sub = AssignmentSubmission.query.filter_by(
        assignment_id=data.get('assignment_id'), student_id=student.id).first()
    if sub:
        sub.marks_given = data.get('marks')
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Submission not found'})

# ── Admin pages ───────────────────────────────────────────────────────────────
@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    user = get_user(session['uid'])
    p    = user.admin_profile
    return render_template('index.html', page='admin_dashboard',
        admin={'name':user.name,'photo':user.photo,
               'role':p.role_desc if p else 'Administrator'},
        total_students=User.query.filter_by(role='student').count(),
        total_teachers=User.query.filter_by(role='teacher').count(),
        total_branches=len(BRANCHES),
        admin_notices=[n.to_dict() for n in Notice.query.filter_by(notice_type='admin')
                       .order_by(Notice.created_at.desc()).all()],
        complaints=[c.to_dict() for c in Complaint.query.order_by(
                    Complaint.created_at.desc()).all()],
        branches=BRANCHES)


@app.route('/admin/post-notice', methods=['POST'])
@login_required('admin')
def admin_post_notice():
    user  = get_user(session['uid'])
    title = request.form.get('title','')
    body  = request.form.get('body','')
    if title and body:
        photo_path = save_upload(
            request.files.get('photo'),
            subfolder='notices',
            allowed_ext={'jpg', 'jpeg', 'png', 'gif', 'webp'})
        db.session.add(Notice(posted_by=user.id, notice_type='admin',
            title=title, body=body, from_name=request.form.get('sender','Admin'),
            photo_path=photo_path))
        db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/resolve-complaint/<int:complaint_id>', methods=['POST'])
@login_required('admin')
def resolve_complaint(complaint_id):
    c = Complaint.query.get_or_404(complaint_id)
    c.status = 'resolved'
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# ── API ────────────────────────────────────────────────────────────────────────
@app.route('/api/attendance-data')
def api_attendance():
    uid  = session.get('uid','')
    user = get_user(uid) if uid else None
    return jsonify(build_attendance_summary(user.id)) if user else jsonify({})


@app.route('/api/calendar-events')
def api_calendar_events():
    return jsonify([{'date':e.date,'title':e.title,'type':e.event_type}
                    for e in CalendarEvent.query.order_by(CalendarEvent.date).all()])

# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True, port=5000)
