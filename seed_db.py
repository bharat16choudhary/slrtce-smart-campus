"""
SLRTCE Smart Campus — Database Seeder  (seed_db.py)
All SQLAlchemy models live in app.py — this file only seeds data.
Run:  python seed_db.py
"""

from app import app, db
from app import (
    User, StudentProfile, TeacherProfile, AdminProfile,
    TimetableEntry, StudyMaterial, Assignment, AssignmentSubmission,
    Notice, Complaint, Exam, ExamMark, CalendarEvent, AttendanceRecord
)
from werkzeug.security import generate_password_hash
from datetime import date, timedelta


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("[OK] Tables created.")

        # ── USERS ──────────────────────────────────────────────────────────────

        student1 = User(
            uid='Bharat009',
            password=generate_password_hash('Bharat@1234'),
            name='Bharat Sharma',
            email='bharat.sharma@slrtce.in',
            phone='9876543210',
            photo='https://ui-avatars.com/api/?name=Bharat+Sharma&background=E8B84B&color=4A4A4A&size=200&bold=true',
            role='student'
        )
        db.session.add(student1)
        db.session.flush()
        db.session.add(StudentProfile(
            user_id=student1.id,
            roll_no='09', branch='CMPN', div='A', year='SE',
            dob='15-Aug-2004', address='Mira Road, Thane, Maharashtra'
        ))

        student2 = User(
            uid='shivam009',
            password=generate_password_hash('shivam@1234'),
            name='Shivam Sharma',
            email='shivam.sharma@slrtce.in',
            phone='9876543212',
            photo='https://ui-avatars.com/api/?name=Shivam+Sharma&background=E8B84B&color=4A4A4A&size=200&bold=true',
            role='student'
        )
        db.session.add(student2)
        db.session.flush()
        db.session.add(StudentProfile(
            user_id=student2.id,
            roll_no='11', branch='CMPN', div='A', year='SE',
            dob='21-Nov-2004', address='Borivali, Mumbai, Maharashtra'
        ))

        teacher = User(
            uid='Nijina0001',
            password=generate_password_hash('nijina@1234'),
            name='Prof. Nijina Shaikh',
            email='nijina.shaikh@slrtce.in',
            phone='9876543211',
            photo='https://ui-avatars.com/api/?name=Nijina+Shaikh&background=C0392B&color=ffffff&size=200&bold=true',
            role='teacher'
        )
        db.session.add(teacher)
        db.session.flush()
        db.session.add(TeacherProfile(
            user_id=teacher.id,
            branch='CMPN', subject='Data Structures',
            designation='Assistant Professor', employee_id='EMP0001'
        ))

        admin = User(
            uid='admin001',
            password=generate_password_hash('admin@1234'),
            name='Admin User',
            email='admin@slrtce.in',
            photo='https://ui-avatars.com/api/?name=Admin&background=4A4A4A&color=ffffff&size=200&bold=true',
            role='admin'
        )
        db.session.add(admin)
        db.session.flush()
        db.session.add(AdminProfile(user_id=admin.id, role_desc='System Administrator'))

        db.session.commit()
        print("[OK] Users seeded.")

        # ── TIMETABLE ──────────────────────────────────────────────────────────

        timetable_data = {
            'Monday':    ['Data Structures', 'DBMS',           'Maths III', '---', 'OS',             'CN'],
            'Tuesday':   ['OS',              'CN',             '---',        'Data Structures', 'DBMS', 'Lab'],
            'Wednesday': ['Maths III',       'Data Structures','OS',         '---', 'CN',             'DBMS'],
            'Thursday':  ['Lab',             'Lab',            '---',        'OS',  'Data Structures','Maths III'],
            'Friday':    ['CN',              'DBMS',           'Maths III',  '---', 'Data Structures','OS'],
            'Saturday':  ['Tutorial',        '---',            'Library',    '---', '---',            '---'],
        }
        time_slots = ['9:00-10:00','10:00-11:00','11:00-12:00','12:00-1:00','1:00-2:00','2:00-3:00']

        for day, subjects in timetable_data.items():
            for idx, subj in enumerate(subjects):
                db.session.add(TimetableEntry(
                    branch='CMPN', div='A', year='SE',
                    day=day, slot_index=idx,
                    slot_label=time_slots[idx], subject=subj
                ))
        db.session.commit()
        print("[OK] Timetable seeded.")

        # ── STUDY MATERIALS ────────────────────────────────────────────────────

        materials = {
            'Data Structures': {
                'handwritten': [
                    ('Module 1 - Arrays & Linked Lists', '05 Apr 2024'),
                    ('Module 2 - Stacks & Queues',        '10 Apr 2024'),
                    ('Module 3 - Trees & BST',            '12 Apr 2024'),
                ],
                'ppt_pdf': [
                    ('DS Unit 1 Slides',               '01 Apr 2024'),
                    ('DS Unit 2 PDF',                  '08 Apr 2024'),
                    ('DS Unit 3 - Graph Algorithms',   '11 Apr 2024'),
                ],
                'reference_books': [
                    ('Data Structures - Lipschutz',              None),
                    ('Introduction to Algorithms - CLRS',        None),
                    ('Data Structures Using C - Reema Thareja',  None),
                ],
                'youtube': [
                    ('DS Playlist - Abdul Bari',          'https://www.youtube.com/playlist?list=PLIY8eNdw5tW_zX3OCzX7NJ8bL1p6pWfgG'),
                    ('Linked List in depth',               'https://www.youtube.com/watch?v=njTh_OwMljA'),
                    ('Sorting Algorithms Visualized',      'https://www.youtube.com/watch?v=kPRA0W1kECg'),
                ],
            },
            'DBMS': {
                'handwritten': [
                    ('Module 1 - ER Model & Relational Model', '03 Apr 2024'),
                    ('Module 2 - SQL Queries',                 '09 Apr 2024'),
                ],
                'ppt_pdf': [
                    ('DBMS Unit 1 Slides',           '02 Apr 2024'),
                    ('DBMS Unit 2 - Normalization',  '07 Apr 2024'),
                ],
                'reference_books': [
                    ('Database System Concepts - Silberschatz',    None),
                    ('Fundamentals of DB Systems - Elmasri',       None),
                ],
                'youtube': [
                    ('DBMS Full Course - Neso Academy', 'https://www.youtube.com/watch?v=kBdlM6hNDAE'),
                    ('SQL Tutorial - W3Schools',         'https://www.youtube.com/watch?v=HXV3zeQKqGY'),
                ],
            },
            'Mathematics III': {
                'handwritten': [
                    ('Module 1 - Laplace Transforms', '04 Apr 2024'),
                    ('Module 2 - Fourier Series',     '08 Apr 2024'),
                ],
                'ppt_pdf': [
                    ('Maths III Unit 1 Notes',   '01 Apr 2024'),
                    ('Numerical Methods PDF',    '06 Apr 2024'),
                ],
                'reference_books': [
                    ('Higher Engineering Mathematics - B.S. Grewal', None),
                    ('Advanced Engineering Mathematics - Kreyszig',   None),
                ],
                'youtube': [
                    ('Laplace Transform - Khan Academy', 'https://www.youtube.com/watch?v=ofvkZXgmCEo'),
                    ('Fourier Series - Neso Academy',    'https://www.youtube.com/watch?v=Cb3HpOf2V1g'),
                ],
            },
            'Operating Systems': {
                'handwritten': [
                    ('Module 1 - Process Management', '02 Apr 2024'),
                    ('Module 2 - Memory Management',  '10 Apr 2024'),
                ],
                'ppt_pdf': [
                    ('OS Unit 1 Slides',                    '01 Apr 2024'),
                    ('Deadlock & Synchronization PDF',      '08 Apr 2024'),
                ],
                'reference_books': [
                    ('Operating System Concepts - Silberschatz', None),
                    ('Modern Operating Systems - Tanenbaum',     None),
                ],
                'youtube': [
                    ('OS Full Course - Gate Smashers',     'https://www.youtube.com/watch?v=LNL5d8DJRGU'),
                    ('Process Scheduling Algorithms',      'https://www.youtube.com/watch?v=EWkQl0n0w5M'),
                ],
            },
            'Computer Networks': {
                'handwritten': [
                    ('Module 1 - OSI Model & TCP/IP',        '03 Apr 2024'),
                    ('Module 2 - Network Layer Protocols',   '09 Apr 2024'),
                ],
                'ppt_pdf': [
                    ('CN Unit 1 Slides',         '01 Apr 2024'),
                    ('Routing Algorithms PDF',   '07 Apr 2024'),
                ],
                'reference_books': [
                    ('Computer Networks - Tanenbaum',            None),
                    ('Data Communications & Networking - Forouzan', None),
                ],
                'youtube': [
                    ('Computer Networks - Neso Academy', 'https://www.youtube.com/watch?v=VwN91x5i25g'),
                    ('TCP/IP Model Explained',           'https://www.youtube.com/watch?v=2QGgEk20RXM'),
                ],
            },
        }

        for subject, types in materials.items():
            for mtype, items in types.items():
                for name, extra in items:
                    is_yt = (mtype == 'youtube')
                    db.session.add(StudyMaterial(
                        uploaded_by=teacher.id, branch='CMPN',
                        subject=subject, material_type=mtype, name=name,
                        file_path=None if is_yt else '#',
                        url=extra if is_yt else None
                    ))
        db.session.commit()
        print("[OK] Study materials seeded.")

        # ── ASSIGNMENTS ────────────────────────────────────────────────────────

        assignments_data = [
            ('Data Structures',  'Module 2', 'Implementation of Linked List Operations',                     10, '15 Apr 2024'),
            ('DBMS',             'Module 1', 'ER Diagram for College Database',                               10, '17 Apr 2024'),
            ('Operating Systems','Module 1', 'Process Scheduling Simulation (Round Robin)',                   15, '12 Apr 2024'),
            ('Computer Networks','Module 2', 'Simulate TCP/IP Packet Flow using Socket Programming',          20, '20 Apr 2024'),
            ('Mathematics III',  'Module 1', 'Solve Laplace Transform Problems (10 Questions)',               10, '14 Apr 2024'),
        ]
        assignment_objs = []
        for subj, mod, title, marks, due in assignments_data:
            a = Assignment(
                teacher_id=teacher.id, branch='CMPN', div='A',
                subject=subj, module=mod, title=title, marks=marks, due_date=due
            )
            db.session.add(a)
            assignment_objs.append(a)
        db.session.flush()

        # OS assignment already submitted by Bharat
        db.session.add(AssignmentSubmission(
            assignment_id=assignment_objs[2].id,
            student_id=student1.id
        ))
        db.session.commit()
        print("[OK] Assignments seeded.")

        # ── NOTICES ────────────────────────────────────────────────────────────

        admin_notices = [
            ('Annual Day Celebration',
             'Annual day celebration will be held on 25th April 2024. All students are requested to participate.',
             'Principal'),
            ('Exam Schedule Released',
             'IAT-2 examination schedule has been released. Please check the exam section for details.',
             'HOD CMPN'),
            ('Workshop on AI/ML',
             'A two-day workshop on AI & Machine Learning is scheduled from 18-19 April 2024. Register at the department office.',
             'Training Cell'),
        ]
        for title, body, from_name in admin_notices:
            db.session.add(Notice(posted_by=admin.id, notice_type='admin',
                                  title=title, body=body, from_name=from_name))

        teacher_notices = [
            ('DS Assignment Submission',
             'Module 2 assignment for Data Structures must be submitted by 15th April 2024. Late submissions will not be accepted.',
             'Prof. Nijina Shaikh', 'Data Structures'),
            ('DBMS Practical Viva',
             'Practical viva for DBMS will be conducted on 16th April. Students should revise all practicals from 1-10.',
             'Prof. Rajesh Gupta', 'DBMS'),
            ('Extra Lecture - Maths',
             'Extra lecture for Mathematics III will be held on Saturday (13 Apr) at 10 AM in Room 305.',
             'Prof. Priya Nair', 'Maths III'),
        ]
        for title, body, from_name, subj in teacher_notices:
            db.session.add(Notice(posted_by=teacher.id, notice_type='teacher',
                                  subject=subj, title=title, body=body, from_name=from_name))
        db.session.commit()
        print("[OK] Notices seeded.")

        # ── COMPLAINTS ─────────────────────────────────────────────────────────

        db.session.add(Complaint(
            student_id=student1.id,
            from_name='Bharat Sharma (Bharat009)',
            subject='Projector not working in Room 301',
            body='The projector in Room 301 has been malfunctioning for the past week. It affects lecture quality.',
            status='pending'
        ))
        db.session.add(Complaint(
            from_name='Anjali Mehta (SE-A)',
            subject='Library books not returned on time',
            body='Several students have not returned books borrowed from the library. Strict action requested.',
            status='resolved'
        ))
        db.session.commit()
        print("[OK] Complaints seeded.")

        # ── EXAMS ──────────────────────────────────────────────────────────────

        upcoming_exams = [
            ('Data Structures', '20 Apr 2024', '10:00 AM', 'IAT-2', 'Seminar Hall A'),
            ('DBMS',            '22 Apr 2024', '10:00 AM', 'IAT-2', 'Room 301'),
            ('Maths III',       '25 Apr 2024', '11:00 AM', 'IAT-2', 'Room 205'),
        ]
        for subj, dt, tm, etype, venue in upcoming_exams:
            db.session.add(Exam(branch='CMPN', div='A', subject=subj,
                                date=dt, time=tm, exam_type=etype, venue=venue))

        # IAT marks for Bharat
        iat_data = [
            ('Data Structures',   18, 20, 20),
            ('DBMS',              17, None, 20),
            ('Mathematics III',   15, None, 20),
            ('Operating Systems', 19, None, 20),
            ('Computer Networks', 16, None, 20),
        ]
        for subj, i1, i2, mx in iat_data:
            db.session.add(ExamMark(student_id=student1.id, subject=subj,
                                    exam_type='iat1', marks=i1, max_marks=mx))
            if i2 is not None:
                db.session.add(ExamMark(student_id=student1.id, subject=subj,
                                        exam_type='iat2', marks=i2, max_marks=mx))

        # Semester scorecard
        for subj, score in [('Data Structures', 82), ('DBMS', 78), ('Maths II', 71)]:
            db.session.add(ExamMark(student_id=student1.id, subject=subj,
                                    exam_type='sem1', marks=score, max_marks=100))
        db.session.commit()
        print("[OK] Exams & marks seeded.")

        # ── ATTENDANCE ─────────────────────────────────────────────────────────

        attendance_subjects = {
            'Data Structures': (18, 22),
            'DBMS':            (20, 22),
            'Maths III':       (15, 20),
            'OS':              (19, 22),
            'CN':              (21, 22),
        }
        base_date = date(2024, 4, 1)
        for subj, (present, total) in attendance_subjects.items():
            for i in range(total):
                db.session.add(AttendanceRecord(
                    student_id=student1.id, teacher_id=teacher.id,
                    branch='CMPN', div='A', subject=subj,
                    date=base_date + timedelta(days=i),
                    status='present' if i < present else 'absent'
                ))
        db.session.commit()
        print("[OK] Attendance records seeded.")

        # ── CALENDAR EVENTS ────────────────────────────────────────────────────

        events = [
            ('2024-04-10', 'Last date for fee payment',     'important'),
            ('2024-04-14', 'Dr. Ambedkar Jayanti - Holiday','holiday'),
            ('2024-04-17', 'Mahavir Jayanti - Holiday',     'holiday'),
            ('2024-04-18', 'Workshop: AI/ML Day 1',         'event'),
            ('2024-04-19', 'Workshop: AI/ML Day 2',         'event'),
            ('2024-04-20', 'IAT-2 Begins',                  'exam'),
            ('2024-04-25', 'Annual Day Celebration',         'event'),
            ('2024-05-01', 'Maharashtra Day - Holiday',      'holiday'),
            ('2024-05-23', 'End Semester Exams Begin',       'exam'),
        ]
        for dt, title, etype in events:
            db.session.add(CalendarEvent(date=dt, title=title, event_type=etype))
        db.session.commit()
        print("[OK] Calendar events seeded.")

        print("\n[DONE] Database seeded successfully! -> slrtce.db")
        print("\nLogin credentials:")
        print("  Student  : uid=Bharat009    password=Bharat@1234")
        print("  Student  : uid=shivam009    password=shivam@1234")
        print("  Teacher  : uid=Nijina0001   password=nijina@1234")
        print("  Admin    : uid=admin001     password=admin@1234")


if __name__ == '__main__':
    seed()
