import requests, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
s = requests.Session()
b = 'http://127.0.0.1:5000'

def chk(cond, label):
    print(f"  {'OK  ' if cond else 'MISS'} {label}")

# Student login
s.post(b+'/login/student', data={'uid':'Bharat009','password':'Bharat@1234'})

# Check all 5 subjects present in study material page
r = s.get(b+'/student/study-material')
for subj in ['Data Structures', 'DBMS', 'Mathematics III', 'Operating Systems', 'Computer Networks']:
    chk(subj.encode() in r.content, f"Subject chip: {subj}")

# Check all subjects have materials
for subj in ['Data Structures', 'DBMS', 'Mathematics III', 'Operating Systems', 'Computer Networks']:
    r2 = s.get(b+'/student/study-material?subject='+subj.replace(' ', '+'))
    chk(b'Handwritten Notes' in r2.content, f"Materials for: {subj}")

# Assignments show 5
r = s.get(b+'/student/assignments')
count = r.content.count(b'Due:')
chk(count >= 5, f"Assignments shown (found {count})")

# Teacher checks
s.get(b+'/logout')
s.post(b+'/login/faculty', data={'uid':'Nigina0001','password':'nigina@1234'})

r = s.get(b+'/teacher/take-attendance?branch=CMPN&division=A')
chk(b'Aditya Patil' in r.content, "Take attendance: real student names")

r = s.get(b+'/teacher/check-assignments?branch=CMPN&division=A')
chk(b'Linked List' in r.content, "Check assignments: shows assignment data")

r = s.get(b+'/teacher/attendance-list?branch=CMPN&division=A')
chk(b'Aditya Patil' in r.content, "Attendance list: real names")
chk(b'91%' in r.content or b'86%' in r.content, "Attendance list: percentage bars")

# Admin stats
s.get(b+'/logout')
s.post(b+'/login/admin', data={'uid':'admin001','password':'admin@1234'})
r = s.get(b+'/admin/dashboard')
chk(b'1,920' in r.content or b'1920' in r.content, "Admin: shows 1920 students")

print()
print("=== VERIFICATION COMPLETE ===")
