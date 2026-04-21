"""
SLRTCE Smart Campus — Database Models
SQLAlchemy ORM definitions for all application tables.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ─── USER & AUTH ──────────────────────────────────────────────────────────────

class User(db.Model):
    """Base user account — role discriminator: student / teacher / admin"""
    __tablename__ = 'users'

    id       = db.Column(db.Integer, primary_key=True)
    uid      = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)   # hashed
    name     = db.Column(db.String(100), nullable=False)
    email    = db.Column(db.String(150))
    phone    = db.Column(db.String(20))
    photo    = db.Column(db.String(300))
    role     = db.Column(db.String(20), nullable=False)    # student / teacher / admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # back-references added by child models
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all,delete')
    teacher_profile = db.relationship('TeacherProfile', backref='user', uselist=False, cascade='all,delete')
    admin_profile   = db.relationship('AdminProfile',   backref='user', uselist=False, cascade='all,delete')


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    roll_no  = db.Column(db.String(10))
    branch   = db.Column(db.String(20))
    div      = db.Column(db.String(5))
    year     = db.Column(db.String(5))
    dob      = db.Column(db.String(20))
    address  = db.Column(db.String(300))


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

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_desc = db.Column(db.String(100))


# ─── TIMETABLE ────────────────────────────────────────────────────────────────

class TimetableEntry(db.Model):
    __tablename__ = 'timetable_entries'

    id          = db.Column(db.Integer, primary_key=True)
    branch      = db.Column(db.String(20), nullable=False)
    div         = db.Column(db.String(5))
    year        = db.Column(db.String(5))
    day         = db.Column(db.String(15), nullable=False)
    slot_index  = db.Column(db.Integer, nullable=False)   # 0-5
    slot_label  = db.Column(db.String(20))                # e.g. "9:00-10:00"
    subject     = db.Column(db.String(100))


# ─── ATTENDANCE ───────────────────────────────────────────────────────────────

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'

    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    branch     = db.Column(db.String(20))
    div        = db.Column(db.String(5))
    subject    = db.Column(db.String(100))
    date       = db.Column(db.Date, nullable=False)
    status     = db.Column(db.String(10), nullable=False, default='absent')  # present/absent/late
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', foreign_keys=[student_id], backref='attendance_as_student')
    teacher = db.relationship('User', foreign_keys=[teacher_id])


# ─── STUDY MATERIALS ──────────────────────────────────────────────────────────

class StudyMaterial(db.Model):
    __tablename__ = 'study_materials'

    id            = db.Column(db.Integer, primary_key=True)
    uploaded_by   = db.Column(db.Integer, db.ForeignKey('users.id'))
    branch        = db.Column(db.String(20))
    subject       = db.Column(db.String(100), nullable=False)
    module        = db.Column(db.String(100))
    material_type = db.Column(db.String(30))   # handwritten / ppt_pdf / reference_books / youtube
    name          = db.Column(db.String(200), nullable=False)
    file_path     = db.Column(db.String(300))  # relative path or external URL
    url           = db.Column(db.String(500))  # for youtube links
    uploaded_at   = db.Column(db.DateTime, default=datetime.utcnow)

    uploader = db.relationship('User', foreign_keys=[uploaded_by])


# ─── ASSIGNMENTS ──────────────────────────────────────────────────────────────

class Assignment(db.Model):
    __tablename__ = 'assignments'

    id          = db.Column(db.Integer, primary_key=True)
    teacher_id  = db.Column(db.Integer, db.ForeignKey('users.id'))
    branch      = db.Column(db.String(20), nullable=False)
    div         = db.Column(db.String(5), nullable=False)
    subject     = db.Column(db.String(100), nullable=False)
    module      = db.Column(db.String(100))
    title       = db.Column(db.String(300), nullable=False)
    marks       = db.Column(db.Integer, default=10)
    due_date    = db.Column(db.String(30))
    file_path   = db.Column(db.String(300))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

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

    student = db.relationship('User', foreign_keys=[student_id])


# ─── NOTICES ──────────────────────────────────────────────────────────────────

class Notice(db.Model):
    __tablename__ = 'notices'

    id          = db.Column(db.Integer, primary_key=True)
    posted_by   = db.Column(db.Integer, db.ForeignKey('users.id'))
    notice_type = db.Column(db.String(20), nullable=False)  # admin / teacher
    branch      = db.Column(db.String(20))
    div         = db.Column(db.String(5))
    subject     = db.Column(db.String(100))
    title       = db.Column(db.String(300), nullable=False)
    body        = db.Column(db.Text, nullable=False)
    from_name   = db.Column(db.String(100))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    poster = db.relationship('User', foreign_keys=[posted_by])

    # ── Template compatibility properties ──────────────────────────────────────
    # Templates reference notice.from and notice.date (legacy dict-key style)

    @property
    def date(self):
        """Formatted date string for template display."""
        return self.created_at.strftime('%d %b %Y') if self.created_at else ''

    def to_dict(self):
        """Return plain dict so templates can use notice.from without keyword issues."""
        return {
            'id':          self.id,
            'title':       self.title,
            'body':        self.body,
            'subject':     self.subject,
            'from':        self.from_name or '',
            'date':        self.date,
            'notice_type': self.notice_type,
            'branch':      self.branch,
            'div':         self.div,
        }



# ─── COMPLAINTS ───────────────────────────────────────────────────────────────

class Complaint(db.Model):
    __tablename__ = 'complaints'

    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    from_name  = db.Column(db.String(100))
    subject    = db.Column(db.String(200), nullable=False)
    body       = db.Column(db.Text, nullable=False)
    status     = db.Column(db.String(20), default='pending')  # pending / resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', foreign_keys=[student_id])

    @property
    def date(self):
        return self.created_at.strftime('%d %b %Y') if self.created_at else ''

    def to_dict(self):
        return {
            'id':      self.id,
            'from':    self.from_name or '',
            'subject': self.subject,
            'body':    self.body,
            'status':  self.status,
            'date':    self.date,
        }



# ─── EXAMS ────────────────────────────────────────────────────────────────────

class Exam(db.Model):
    __tablename__ = 'exams'

    id       = db.Column(db.Integer, primary_key=True)
    branch   = db.Column(db.String(20))
    div      = db.Column(db.String(5))
    subject  = db.Column(db.String(100), nullable=False)
    exam_type = db.Column(db.String(20))    # IAT-1 / IAT-2 / End-Sem
    date     = db.Column(db.String(30))
    time     = db.Column(db.String(20))
    venue    = db.Column(db.String(100))


class ExamMark(db.Model):
    __tablename__ = 'exam_marks'

    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject    = db.Column(db.String(100), nullable=False)
    exam_type  = db.Column(db.String(20))   # iat1 / iat2 / sem1 / sem2
    marks      = db.Column(db.Float)
    max_marks  = db.Column(db.Float, default=20)

    student = db.relationship('User', foreign_keys=[student_id])


# ─── CALENDAR ─────────────────────────────────────────────────────────────────

class CalendarEvent(db.Model):
    __tablename__ = 'calendar_events'

    id         = db.Column(db.Integer, primary_key=True)
    date       = db.Column(db.String(20), nullable=False)   # YYYY-MM-DD
    title      = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(20))   # holiday / exam / event / important
