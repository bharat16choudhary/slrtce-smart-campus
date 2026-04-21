import requests, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
s = requests.Session()
b = 'http://127.0.0.1:5000'

def chk(cond, label):
    print(f"  {'OK  ' if cond else 'MISS'} {label}")

# Test 1: Admin posts a notice
s.post(b+'/login/admin', data={'uid':'admin001','password':'admin@1234'})
r = s.post(b+'/admin/post-notice', data={'title':'Test Admin Notice', 'body':'Admin notice body', 'sender':'Principal'})
chk(r.status_code in [200, 302], "Admin notice submission status")
s.get(b+'/logout')

# Test 2: Teacher posts a notice
s.post(b+'/login/faculty', data={'uid':'Nigina0001','password':'nigina@1234'})
r = s.post(b+'/teacher/send-notice', data={'title':'Test Teacher Notice', 'body':'Teacher notice body'})
chk(r.status_code in [200, 302], "Teacher notice submission status")

# Test 3: Teacher submits attendance
r = s.post(b+'/teacher/submit-attendance', json={'branch':'CMPN', 'division':'A', 'attendance':{'01':'present', '02':'absent'}})
chk(r.status_code in [200], "Teacher attendance submission status")
chk(b'true' in r.content.lower(), "Attendance success true")

# Test 4: Teacher uploads an assignment
r = s.post(b+'/teacher/upload-assignment', data={
    'branch':'CMPN', 'division':'A', 'subject':'DBMS', 'module':'Module 3', 'title':'Test Upload', 'marks':'20', 'due_date':'20 Apr 2024'
})
chk(r.status_code in [200, 302], "Teacher upload assignment status")

# Test 5: Teacher gives marks
r = s.post(b+'/teacher/give-marks', json={'assignment_id':3, 'student_uid':'Bharat009', 'marks':15})
chk(r.status_code in [200], "Teacher give marks status")
s.get(b+'/logout')

# Test 6: Student checks notices and assignments
s.post(b+'/login/student', data={'uid':'Bharat009','password':'Bharat@1234'})
r = s.get(b+'/student/noticeboard')
chk(b'Test Admin Notice' in r.content, "Student sees admin notice")
chk(b'Test Teacher Notice' in r.content, "Student sees teacher notice")

r = s.get(b+'/student/assignments')
chk(b'Test Upload' in r.content, "Student sees uploaded assignment")

r = s.post(b+'/student/submit-assignment/3', data={})
chk(r.status_code in [200, 302], "Student assignment submission status: " + str(r.status_code))

print()
print("=== VERIFICATION COMPLETE ===")
