# Fully Corrected app.py (Clean Version)
from flask import Flask, render_template, request, redirect, session
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
from werkzeug.utils import secure_filename

app = Flask(__name__)

# =========================
# CONFIGURATION
# =========================

UPLOAD_FOLDER = 'static/uploads/assignments'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = "secretkey"

# =========================
# DATABASE CONNECTION
# =========================
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT"))
)

# =========================
# HOME PAGE
# =========================

@app.route('/')
def home():
    return render_template('index.html')

# =========================
# REGISTER
# =========================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        cursor = db.cursor(dictionary=True)

        query = """
        INSERT INTO users(name, email, password, role)
        VALUES(%s, %s, %s, %s)
        """

        values = (name, email, password, role)

        cursor.execute(query, values)
        db.commit()

        cursor.close()

        return redirect('/login')

    return render_template('register.html')


# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor(dictionary=True)

        # FIND USER

        cursor.execute("""
            SELECT *
            FROM users
            WHERE email=%s
        """, (email,))

        user = cursor.fetchone()

        # CHECK PASSWORD

        if user and user['password'] == password:

            session['user'] = user['name']
            session['role'] = user['role']

            # REDIRECT BASED ON ROLE

            if user['role'] == 'student':
                return redirect('/student')

            elif user['role'] == 'teacher':
                return redirect('/teacher')

            elif user['role'] == 'admin':
                return redirect('/admin')

        return "Invalid Email or Password"

    return render_template('login.html')

# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

# =========================
# STUDENT DASHBOARD
# =========================

@app.route('/student')
def student():

    if session.get('role') != 'student':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    # TOTAL COURSES

    cursor.execute("""
        SELECT COUNT(*) AS total_courses
        FROM courses
    """)

    total_courses = cursor.fetchone()['total_courses']

    # TOTAL ASSIGNMENTS

    cursor.execute("""
        SELECT COUNT(*) AS total_assignments
        FROM assignments
    """)

    total_assignments = cursor.fetchone()['total_assignments']

    # TOTAL SUBMISSIONS

    cursor.execute("""
        SELECT COUNT(*) AS total_submissions
        FROM submissions
        WHERE student_name=%s
    """, (session['user'],))

    total_submissions = cursor.fetchone()['total_submissions']

    # ATTENDANCE COUNT

    cursor.execute("""
        SELECT COUNT(*) AS attendance_records
        FROM attendance
        WHERE student_name=%s
    """, (session['user'],))

    attendance = cursor.fetchone()['attendance_records']

    # RECENT ASSIGNMENTS

    cursor.execute("""
        SELECT *
        FROM assignments
        ORDER BY id DESC
        LIMIT 3
    """)

    recent_assignments = cursor.fetchall()

    cursor.close()

    return render_template(
        'student_dashboard.html',
        user=session['user'],
        total_courses=total_courses,
        total_assignments=total_assignments,
        total_submissions=total_submissions,
        attendance=attendance,
        recent_assignments=recent_assignments
    )
# =========================
# TEACHER DASHBOARD
# =========================

@app.route('/teacher')
def teacher():

    if session.get('role') != 'teacher':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    # Total Courses

    cursor.execute("""
        SELECT COUNT(*) AS total_courses
        FROM courses
    """)

    total_courses = cursor.fetchone()['total_courses']

    # Total Assignments

    cursor.execute("""
        SELECT COUNT(*) AS total_assignments
        FROM assignments
    """)

    total_assignments = cursor.fetchone()['total_assignments']

    # Total Students

    cursor.execute("""
        SELECT COUNT(*) AS total_students
        FROM users
        WHERE role='student'
    """)

    total_students = cursor.fetchone()['total_students']

    # Total Submissions

    cursor.execute("""
        SELECT COUNT(*) AS total_submissions
        FROM submissions
    """)

    total_submissions = cursor.fetchone()['total_submissions']

    # Recent Submissions

    cursor.execute("""
        SELECT *
        FROM submissions
        ORDER BY submitted_at DESC
        LIMIT 5
    """)

    recent_submissions = cursor.fetchall()

    cursor.close()

    return render_template(
        'teacher_dashboard.html',
        user=session['user'],
        total_courses=total_courses,
        total_assignments=total_assignments,
        total_students=total_students,
        total_submissions=total_submissions,
        recent_submissions=recent_submissions
    )

# =========================
# ADMIN DASHBOARD
# =========================

@app.route('/admin')
def admin():

    if session.get('role') != 'admin':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    # TOTAL STUDENTS

    cursor.execute("""
        SELECT COUNT(*) AS total_students
        FROM users
        WHERE role='student'
    """)

    total_students = cursor.fetchone()['total_students']

    # TOTAL TEACHERS

    cursor.execute("""
        SELECT COUNT(*) AS total_teachers
        FROM users
        WHERE role='teacher'
    """)

    total_teachers = cursor.fetchone()['total_teachers']

    # TOTAL COURSES

    cursor.execute("""
        SELECT COUNT(*) AS total_courses
        FROM courses
    """)

    total_courses = cursor.fetchone()['total_courses']

    # TOTAL ASSIGNMENTS

    cursor.execute("""
        SELECT COUNT(*) AS total_assignments
        FROM assignments
    """)

    total_assignments = cursor.fetchone()['total_assignments']

    # TOTAL SUBMISSIONS

    cursor.execute("""
        SELECT COUNT(*) AS total_submissions
        FROM submissions
    """)

    total_submissions = cursor.fetchone()['total_submissions']

    # FETCH USERS

    cursor.execute("""
        SELECT * FROM users
        ORDER BY id DESC
    """)

    users = cursor.fetchall()

    cursor.close()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_teachers=total_teachers,
        total_courses=total_courses,
        total_assignments=total_assignments,
        total_submissions=total_submissions,
        users=users,
        user=session['user']
    )

# =========================
# ADMIN DELETE USERS 
# =========================

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):

    if session.get('role') != 'admin':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        DELETE FROM users
        WHERE id=%s
    """, (user_id,))

    db.commit()

    cursor.close()

    return redirect('/admin')

# =========================
# ADMIN COURSES
# =========================

@app.route('/admin/courses')
def admin_courses():

    if session.get('role') != 'admin':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM courses
        ORDER BY id DESC
    """)

    courses = cursor.fetchall()

    cursor.close()

    return render_template(
        'admin_courses.html',
        courses=courses
    )

# =========================
# ADMIN COURSES DELETE
# =========================
@app.route('/delete_course/<int:course_id>')
def admin_delete_course(course_id):

    if session.get('role') != 'admin':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        DELETE FROM course_content
        WHERE course_id=%s
    """, (course_id,))

    cursor.execute("""
        DELETE FROM courses
        WHERE id=%s
    """, (course_id,))

    db.commit()

    cursor.close()

    return redirect('/admin/courses')
# =========================
# ADMIN AI INSIGHTS
# =========================
@app.route('/admin/ai-insights')
def admin_ai_insights():

    if session.get('role') != 'admin':
        return redirect('/login')

    cursor = db.cursor(
        dictionary=True,
        buffered=True
    )

    # TOP STUDENT

    cursor.execute("""
        SELECT student_name,
               AVG(grade) AS avg_grade
        FROM submissions
        WHERE grade IS NOT NULL
        GROUP BY student_name
        ORDER BY avg_grade DESC
        LIMIT 1
    """)

    top_student = cursor.fetchone()

    # LOW PERFORMANCE STUDENTS

    cursor.execute("""
        SELECT student_name,
               AVG(grade) AS avg_grade
        FROM submissions
        WHERE grade IS NOT NULL
        GROUP BY student_name
        HAVING avg_grade < 40
    """)

    weak_students = cursor.fetchall()

    # TOTAL PRESENT

    cursor.execute("""
        SELECT COUNT(*) AS present_count
        FROM attendance
        WHERE status='Present'
    """)

    present = cursor.fetchone()['present_count']

    # TOTAL ABSENT

    cursor.execute("""
        SELECT COUNT(*) AS absent_count
        FROM attendance
        WHERE status='Absent'
    """)

    absent = cursor.fetchone()['absent_count']

    # MOST ACTIVE COURSE
    cursor.execute("""
        SELECT
        course_name,
        instructor
        FROM courses
        ORDER BY id DESC
    """)

    active_course = cursor.fetchone()

    cursor.close()

    return render_template(
        'admin_ai_insights.html',
        top_student=top_student,
        weak_students=weak_students,
        present=present,
        absent=absent,
        active_course=active_course
    )
# =========================
# DELETE COURSES
# =========================
@app.route('/delete_course/<int:course_id>')
def delete_course(course_id):

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        DELETE FROM courses
        WHERE id=%s
    """, (course_id,))

    db.commit()

    cursor.close()

    return redirect('/teacher/courses')
# =========================
# TEACHER COURSES
# =========================

@app.route('/teacher/courses', methods=['GET', 'POST'])
def teacher_courses():

    if session.get('role') != 'teacher':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    # ADD COURSE

    if request.method == 'POST':

        course_name = request.form['course_name']
        instructor = request.form['instructor']
        description = request.form['description']
        image_url = request.form['image_url']

        query = """
        INSERT INTO courses
        (course_name, instructor, description, image_url)

        VALUES(%s,%s,%s,%s,%s)
        """

        values = (
            course_name,
            instructor,
            description,
            image_url
        )

        cursor.execute(query, values)
        db.commit()

    # FETCH COURSES

    cursor.execute("""
        SELECT * FROM courses
        ORDER BY id DESC
    """)

    courses = cursor.fetchall()

    cursor.close()

    return render_template(
        'teacher_courses.html',
        courses=courses
    )

# =========================
# TEACHER MANAGE  COURSES 
# =========================

@app.route('/teacher/course-content/<int:course_id>',
           methods=['GET', 'POST'])
def teacher_course_content(course_id):

    if session.get('role') != 'teacher':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    # GET COURSE

    cursor.execute("""
        SELECT *
        FROM courses
        WHERE id=%s
    """, (course_id,))

    course = cursor.fetchone()

    # ADD CONTENT

    if request.method == 'POST':

        title = request.form['title']
        content_type = request.form['content_type']
        content_url = request.form['content_url']
        description = request.form['description']

        query = """
        INSERT INTO course_content
        (
            course_id,
            title,
            content_type,
            content_url,
            description
        )
        VALUES(%s,%s,%s,%s,%s)
        """

        values = (
            course_id,
            title,
            content_type,
            content_url,
            description
        )

        cursor.execute(query, values)

        db.commit()

    # FETCH CONTENT

    cursor.execute("""
        SELECT *
        FROM course_content
        WHERE course_id=%s
    """, (course_id,))

    content = cursor.fetchall()

    cursor.close()

    return render_template(
        'teacher_course_content.html',
        course=course,
        content=content
    )
# =========================
# EDIT COURSE
# =========================

@app.route('/edit_course/<int:course_id>',
           methods=['GET', 'POST'])
def edit_course(course_id):

    if session.get('role') != 'teacher':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    # FETCH COURSE

    cursor.execute("""
        SELECT *
        FROM courses
        WHERE id=%s
    """, (course_id,))

    course = cursor.fetchone()

    # UPDATE COURSE

    if request.method == 'POST':

        course_name = request.form['course_name']
        instructor = request.form['instructor']
        description = request.form['description']
        image_url = request.form['image_url']

        query = """
        UPDATE courses

        SET
        course_name=%s,
        instructor=%s,
        description=%s,
        image_url=%s

        WHERE id=%s
        """

        values = (
            course_name,
            instructor,
            description,
            image_url,
            course_id
        )

        cursor.execute(query, values)

        db.commit()

        cursor.close()

        return redirect('/teacher/courses')

    return render_template(
        'edit_course.html',
        course=course
    )
# =========================
# CHATBOT
# =========================

@app.route('/student/ai-chatbot', methods=['GET', 'POST'])
def ai_chatbot():

    if session.get('role') != 'student':
        return redirect('/login')

    ai_response = ""
    user_question = ""

    if request.method == 'POST':

        user_question = request.form['question']

        try:

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """
                        You are IntelliAI,
                        a smart educational assistant inside
                        an Intelligent LMS.
                        Help students clearly and simply.
                        """
                    },
                    {
                        "role": "user",
                        "content": user_question
                    }
                ]
            )

            ai_response = response.choices[0].message.content

        except Exception:

            question = user_question.lower()

            # CLOUD

            if "cloud" in question:

                ai_response = """
Cloud computing is the delivery of computing services
such as storage, servers, databases, networking,
and software over the internet.

It helps users access resources anytime without
managing physical hardware.
                """

            # MACHINE LEARNING

            elif "machine learning" in question:

                ai_response = """
Machine learning is a branch of Artificial Intelligence
that allows systems to learn from data and improve
automatically without explicit programming.
                """

            # AI

            elif "artificial intelligence" in question or "ai" in question:

                ai_response = """
Artificial Intelligence (AI) is the simulation of
human intelligence by machines.

AI systems can learn, reason, solve problems,
and make decisions intelligently.
                """

            # PYTHON

            elif "python" in question:

                ai_response = """
Python is a high-level programming language known
for simplicity and readability.

It is widely used in:
- AI
- Machine Learning
- Web Development
- Automation
- Data Science
                """

            # DATABASE

            elif "mysql" in question or "database" in question:

                ai_response = """
MySQL is a relational database management system
used to store, organize, and manage data efficiently.

It is commonly used in web applications and LMS systems.
                """

            # DEFAULT RESPONSE

            else:

                ai_response = """
IntelliAI is currently running in offline smart mode.

Try asking educational questions like:
- What is cloud computing?
- Explain AI
- What is Python?
- Explain machine learning
                """

    return render_template(
        'ai_chatbot.html',
        ai_response=ai_response,
        user_question=user_question
    )
# =========================
# STUDENT COURSES
# =========================

@app.route('/student/courses')
def student_courses():

    if session.get('role') != 'student':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM courses")

    courses = cursor.fetchall()

    cursor.close()

    return render_template(
        'student_courses.html',
        courses=courses
    )

# =========================
# COURSE DETAIL PAGE
# =========================

@app.route('/course/<int:course_id>')
def course_detail(course_id):

    if session.get('role') != 'student':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM courses WHERE id=%s",
        (course_id,)
    )

    course = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM course_content WHERE course_id=%s",
        (course_id,)
    )

    content = cursor.fetchall()

    cursor.close()

    return render_template(
        'course_detail.html',
        course=course,
        content=content
    )

# =========================
# TEACHER ASSIGNMENTS
# =========================

@app.route('/teacher/assignments', methods=['GET', 'POST'])
def teacher_assignments():

    if session.get('role') != 'teacher':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    # CREATE ASSIGNMENT

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']
        subject = request.form['subject']
        deadline = request.form['deadline']
        total_marks = request.form['total_marks']

        query = """
        INSERT INTO assignments
        (
            title,
            description,
            subject,
            deadline,
            total_marks,
            created_by
        )

        VALUES(%s,%s,%s,%s,%s,%s)
        """

        values = (
            title,
            description,
            subject,
            deadline,
            total_marks,
            session['user']
        )

        cursor.execute(query, values)

        db.commit()

    # FETCH ASSIGNMENTS

    cursor.execute("""
        SELECT * FROM assignments
        ORDER BY id DESC
    """)

    assignments = cursor.fetchall()

    cursor.close()

    return render_template(
        'teacher_assignments.html',
        assignments=assignments
    )

# =========================
# DELETE ASSIGNMENTS
# =========================
@app.route('/delete_assignment/<int:assignment_id>')
def delete_assignment(assignment_id):

    if session.get('role') != 'teacher':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        DELETE FROM assignments
        WHERE id=%s
    """, (assignment_id,))

    db.commit()

    cursor.close()

    return redirect('/teacher/assignments')
# =========================
# STUDENT ASSIGNMENTS
# =========================
@app.route('/student/assignments')
def student_assignments():

    if session.get('role') != 'student':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM assignments
        ORDER BY id DESC
    """)

    assignments = cursor.fetchall()

    cursor.close()

    return render_template(
        'student_assignments.html',
        assignments=assignments
    )

# =========================
# ADMIN ASSIGNMENTS
# =========================
@app.route('/admin/assignments')
def admin_assignments():

    if session.get('role') != 'admin':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM assignments
        ORDER BY id DESC
    """)

    assignments = cursor.fetchall()

    cursor.close()

    return render_template(
        'admin_assignments.html',
        assignments=assignments
    )

# =========================
# ADMIN ASSIGNMENTS DELETE
# =========================
@app.route('/delete_assignment/<int:assignment_id>')
def admin_delete_assignment(assignment_id):

    if session.get('role') != 'admin':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    # DELETE SUBMISSIONS

    cursor.execute("""
        DELETE FROM submissions
        WHERE assignment_id=%s
    """, (assignment_id,))

    # DELETE ASSIGNMENT

    cursor.execute("""
        DELETE FROM assignments
        WHERE id=%s
    """, (assignment_id,))

    db.commit()

    cursor.close()

    return redirect('/admin/assignments')
# =========================
# SUBMIT ASSIGNMENT
# =========================
@app.route('/submit_assignment/<int:assignment_id>',
           methods=['POST'])
def submit_assignment(assignment_id):

    if session.get('role') != 'student':
        return redirect('/login')

    file = request.files['submission_file']

    if file:

        filename = secure_filename(file.filename)

        filepath = os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )

        file.save(filepath)

        cursor = db.cursor()

        query = """
        INSERT INTO submissions
        (
            assignment_id,
            student_name,
            file_path
        )
        VALUES(%s,%s,%s)
        """

        values = (
            assignment_id,
            session['user'],
            filepath
        )

        cursor.execute(query, values)

        db.commit()

        cursor.close()

    return redirect('/student/assignments')
# =========================
# TEACHER SUBMISSIONS
# =========================

@app.route('/teacher/submissions')
def teacher_submissions():

    if session.get('role') != 'teacher':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    query = """
    SELECT
        submissions.id,
        submissions.student_name,
        submissions.file_path,
        submissions.submitted_at,
        submissions.status,
        submissions.grade,
        submissions.feedback,

        assignments.title,
        assignments.subject,
        assignments.total_marks

    FROM submissions

    JOIN assignments
    ON submissions.assignment_id = assignments.id

    ORDER BY submissions.id DESC
    """

    cursor.execute(query)

    submissions = cursor.fetchall()

    cursor.close()

    return render_template(
        'teacher_submissions.html',
        submissions=submissions
    )

# =========================
# ADMIN SUBMISSIONS
# =========================

@app.route('/admin/submissions')
def admin_submissions():

    if session.get('role') != 'admin':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            submissions.id,
            submissions.student_name,
            submissions.file_path,
            submissions.status,
            submissions.grade,
            submissions.feedback,
            assignments.title

        FROM submissions

        JOIN assignments
        ON submissions.assignment_id = assignments.id

        ORDER BY submissions.id DESC
    """)

    submissions = cursor.fetchall()

    cursor.close()

    return render_template(
        'admin_submissions.html',
        submissions=submissions
    )
# =========================
# GRADE SUBMISSION
# =========================

@app.route('/grade_submission/<int:submission_id>',
           methods=['POST'])
def grade_submission(submission_id):

    if session.get('role') != 'teacher':
        return redirect('/login')

    grade = request.form['grade']
    feedback = request.form['feedback']

    cursor = db.cursor(dictionary=True)

    query = """
    UPDATE submissions

    SET
        grade=%s,
        feedback=%s,
        status='Graded'

    WHERE id=%s
    """

    values = (
        grade,
        feedback,
        submission_id
    )

    cursor.execute(query, values)

    db.commit()

    cursor.close()

    return redirect('/teacher/submissions')

# =========================
# TEACHER ATTENDANCE
# =========================

@app.route('/teacher/attendance', methods=['GET', 'POST'])
def teacher_attendance():

    if session.get('role') != 'teacher':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    # MARK ATTENDANCE

    if request.method == 'POST':

        student_name = request.form['student_name']
        attendance_date = request.form['attendance_date']
        status = request.form['status']

        query = """
        INSERT INTO attendance
        (
            student_name,
            attendance_date,
            status
        )

        VALUES(%s,%s,%s)
        """

        values = (
            student_name,
            attendance_date,
            status
        )

        cursor.execute(query, values)

        db.commit()

    # FETCH RECORDS

    cursor.execute("""
        SELECT * FROM attendance
        ORDER BY attendance_date DESC
    """)

    records = cursor.fetchall()

    cursor.close()

    return render_template(
        'teacher_attendance.html',
        records=records
    )
# =========================
# STUDENT ATTENDANCE
# =========================

@app.route('/student/attendance')
def student_attendance():

    if session.get('role') != 'student':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM attendance
        WHERE student_name=%s
        ORDER BY attendance_date DESC
    """, (session['user'],))

    records = cursor.fetchall()

    # Attendance Stats

    total_classes = len(records)

    present_count = 0

    absent_count = 0

    late_count = 0

    for record in records:

        if record['status'] == 'Present':
            present_count += 1

        elif record['status'] == 'Absent':
            absent_count += 1

        elif record['status'] == 'Late':
            late_count += 1

    attendance_percentage = 0

    if total_classes > 0:
        attendance_percentage = round(
            (present_count / total_classes) * 100,
            2
        )

    cursor.close()

    return render_template(
        'student_attendance.html',
        records=records,
        total_classes=total_classes,
        present_count=present_count,
        absent_count=absent_count,
        late_count=late_count,
        attendance_percentage=attendance_percentage
    )
# =========================
# STUDENT ANALYTICS
# =========================

@app.route('/student/analytics')
def student_analytics():

    if session.get('role') != 'student':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    # Student submissions

    cursor.execute("""
        SELECT *
        FROM submissions
        WHERE student_name=%s
    """, (session['user'],))

    submissions = cursor.fetchall()

    total_submissions = len(submissions)

    graded_submissions = 0

    total_marks = 0

    marks_list = []

    for submission in submissions:

        if submission['grade']:

            graded_submissions += 1

            grade = int(submission['grade'])

            total_marks += grade

            marks_list.append(grade)

    average_grade = 0

    if graded_submissions > 0:

        average_grade = round(
            total_marks / graded_submissions,
            2
        )

    # Attendance

    cursor.execute("""
        SELECT *
        FROM attendance
        WHERE student_name=%s
    """, (session['user'],))

    attendance_records = cursor.fetchall()

    total_classes = len(attendance_records)

    present_count = 0

    for record in attendance_records:

        if record['status'] == 'Present':

            present_count += 1

    attendance_percentage = 0

    if total_classes > 0:

        attendance_percentage = round(
            (present_count / total_classes) * 100,
            2
        )

    # Performance Status

    performance_status = ""

    if average_grade < 40:

        performance_status = "Needs Improvement"

    elif average_grade < 75:

        performance_status = "Good Performance"

    else:

        performance_status = "Excellent Performance"

    cursor.close()

    return render_template(
        'student_analytics.html',
        total_submissions=total_submissions,
        graded_submissions=graded_submissions,
        average_grade=average_grade,
        attendance_percentage=attendance_percentage,
        performance_status=performance_status,
        marks_list=marks_list
    )

# =========================
# STUDENT RECOMMENDATIONS
# =========================

@app.route('/student/recommendations')
def student_recommendations():

    if session.get('role') != 'student':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    # Grades

    cursor.execute("""
        SELECT grade
        FROM submissions
        WHERE student_name=%s
        AND grade IS NOT NULL
    """, (session['user'],))

    grades = cursor.fetchall()

    average_grade = 0

    if grades:

        total = 0

        for g in grades:

            total += int(g['grade'])

        average_grade = round(total / len(grades), 2)

    # Attendance

    cursor.execute("""
        SELECT *
        FROM attendance
        WHERE student_name=%s
    """, (session['user'],))

    attendance_records = cursor.fetchall()

    total_classes = len(attendance_records)

    present = 0

    for record in attendance_records:

        if record['status'] == 'Present':

            present += 1

    attendance_percentage = 0

    if total_classes > 0:

        attendance_percentage = round(
            (present / total_classes) * 100,
            2
        )

    # AI Recommendation Logic

    recommendations = []

    if average_grade < 40:

        recommendations.append(
            "Focus more on assignment practice and revision."
        )

        recommendations.append(
            "Watch beginner-level course videos again carefully."
        )

    elif average_grade < 75:

        recommendations.append(
            "Your performance is good, but consistency can improve results."
        )

        recommendations.append(
            "Practice more quizzes and real-world projects."
        )

    else:

        recommendations.append(
            "Excellent academic performance detected."
        )

        recommendations.append(
            "Start advanced AI and cloud computing projects."
        )

    if attendance_percentage < 75:

        recommendations.append(
            "Your attendance is low. Attend more live classes."
        )

    else:

        recommendations.append(
            "Great attendance consistency maintained."
        )

    recommendations.append(
        "Recommended Study Time: 2-3 focused hours daily."
    )

    recommendations.append(
        "AI suggests revising weak topics every weekend."
    )

    cursor.close()

    return render_template(
        'student_recommendations.html',
        average_grade=average_grade,
        attendance_percentage=attendance_percentage,
        recommendations=recommendations
    )

# =========================
# STUDENT VIDEOS
# =========================

@app.route('/student/videos')
def student_videos():

    if session.get('role') != 'student':
        return redirect('/login')

    return render_template('videos.html')

# =========================
# AI RECOMMENDATION
# =========================

@app.route('/ai_recommendation', methods=['GET', 'POST'])
def ai_recommendation():

    recommendation = ""
    student_name = ""
    score = ""

    if request.method == 'POST':

        student_name = request.form['student_name']
        score = int(request.form['score'])

        if score < 40:

            recommendation = """
            Your performance is low.
            Practice more quizzes and revise fundamentals.
            """

        elif score >= 40 and score < 75:

            recommendation = """
            Good performance.
            Revise notes regularly and practice assignments.
            """

        else:

            recommendation = """
            Excellent performance.
            Try advanced learning resources and projects.
            """

        cursor = db.cursor(dictionary=True)

        query = """
        INSERT INTO recommendations
        (student_name, score, recommendation)
        VALUES(%s, %s, %s)
        """

        values = (
            student_name,
            score,
            recommendation
        )

        cursor.execute(query, values)

        db.commit()

        cursor.close()

    return render_template(
        'ai_recommendation.html',
        recommendation=recommendation,
        student_name=student_name,
        score=score
    )

# =========================
# TEACHER ANALYTICS
# =========================

@app.route('/teacher/analytics')
def teacher_analytics():

    if session.get('role') != 'teacher':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    # TOTAL STUDENTS

    cursor.execute("""
        SELECT COUNT(*) AS total_students
        FROM users
        WHERE role='student'
    """)

    total_students = cursor.fetchone()['total_students']

    # TOTAL COURSES

    cursor.execute("""
        SELECT COUNT(*) AS total_courses
        FROM courses
    """)

    total_courses = cursor.fetchone()['total_courses']

    # TOTAL ASSIGNMENTS

    cursor.execute("""
        SELECT COUNT(*) AS total_assignments
        FROM assignments
    """)

    total_assignments = cursor.fetchone()['total_assignments']

    # TOTAL SUBMISSIONS

    cursor.execute("""
        SELECT COUNT(*) AS total_submissions
        FROM submissions
    """)

    total_submissions = cursor.fetchone()['total_submissions']

    # PRESENT COUNT

    cursor.execute("""
        SELECT COUNT(*) AS present_count
        FROM attendance
        WHERE status='Present'
    """)

    present_count = cursor.fetchone()['present_count']

    # ABSENT COUNT

    cursor.execute("""
        SELECT COUNT(*) AS absent_count
        FROM attendance
        WHERE status='Absent'
    """)

    absent_count = cursor.fetchone()['absent_count']

    # AVERAGE GRADE

    cursor.execute("""
        SELECT AVG(grade) AS average_grade
        FROM submissions
        WHERE grade IS NOT NULL
    """)

    avg_grade = cursor.fetchone()['average_grade']

    if avg_grade is None:
        avg_grade = 0

    cursor.close()

    return render_template(
        'teacher_analytics.html',
        total_students=total_students,
        total_courses=total_courses,
        total_assignments=total_assignments,
        total_submissions=total_submissions,
        present_count=present_count,
        absent_count=absent_count,
        avg_grade=round(avg_grade, 2)
    )

# =========================
# ADMIN ANALYTICS
# =========================

@app.route('/admin/analytics')
def admin_analytics():

    if session.get('role') != 'admin':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    # TOTAL STUDENTS

    cursor.execute("""
        SELECT COUNT(*) AS total_students
        FROM users
        WHERE role='student'
    """)

    students = cursor.fetchone()['total_students']

    # TOTAL TEACHERS

    cursor.execute("""
        SELECT COUNT(*) AS total_teachers
        FROM users
        WHERE role='teacher'
    """)

    teachers = cursor.fetchone()['total_teachers']

    # TOTAL COURSES

    cursor.execute("""
        SELECT COUNT(*) AS total_courses
        FROM courses
    """)

    courses = cursor.fetchone()['total_courses']

    # TOTAL ASSIGNMENTS

    cursor.execute("""
        SELECT COUNT(*) AS total_assignments
        FROM assignments
    """)

    assignments = cursor.fetchone()['total_assignments']

    # TOTAL SUBMISSIONS

    cursor.execute("""
        SELECT COUNT(*) AS total_submissions
        FROM submissions
    """)

    submissions = cursor.fetchone()['total_submissions']

    # GRADED

    cursor.execute("""
        SELECT COUNT(*) AS graded
        FROM submissions
        WHERE status='Graded'
    """)

    graded = cursor.fetchone()['graded']

    # PENDING

    cursor.execute("""
        SELECT COUNT(*) AS pending
        FROM submissions
        WHERE status!='Graded'
        OR status IS NULL
    """)

    pending = cursor.fetchone()['pending']

    cursor.close()

    return render_template(
        'admin_analytics.html',
        students=students,
        teachers=teachers,
        courses=courses,
        assignments=assignments,
        submissions=submissions,
        graded=graded,
        pending=pending
    )

# =========================
# TEACHER QUIZ
# =========================

@app.route('/quiz_management', methods=['GET', 'POST'])
def quiz_management():

    if session.get('role') != 'teacher':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    # CREATE QUIZ

    if request.method == 'POST':

        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_answer = request.form['correct_answer']

        query = """
        INSERT INTO quizzes
        (
            question,
            option1,
            option2,
            option3,
            option4,
            correct_answer
        )

        VALUES(%s,%s,%s,%s,%s,%s)
        """

        values = (
            question,
            option1,
            option2,
            option3,
            option4,
            correct_answer
        )

        cursor.execute(query, values)

        db.commit()

    # FETCH QUIZZES

    cursor.execute("""
        SELECT * FROM quizzes
        ORDER BY id DESC
    """)

    quizzes = cursor.fetchall()

    cursor.close()

    return render_template(
        'quiz_management.html',
        quizzes=quizzes
    )

# =========================
# TEACHER DELETE QUIZ
# =========================
@app.route('/delete_quiz/<int:quiz_id>')
def delete_quiz(quiz_id):

    if session.get('role') != 'teacher':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        DELETE FROM quizzes
        WHERE id=%s
    """, (quiz_id,))

    db.commit()

    cursor.close()

    return redirect('/quiz_management')
# =========================
# STUDENT QUIZZES
# =========================

@app.route('/student/quizzes')
def student_quizzes():

    if session.get('role') != 'student':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM quizzes
        ORDER BY id DESC
    """)

    quizzes = cursor.fetchall()

    cursor.close()

    return render_template(
        'student_quizzes.html',
        quizzes=quizzes
    )


# =========================
# SUBMIT QUIZ
# =========================

@app.route('/submit_quiz/<int:quiz_id>',
           methods=['POST'])
def submit_quiz(quiz_id):

    if session.get('role') != 'student':
        return redirect('/login')

    selected_answer = request.form['answer']

    cursor = db.cursor(dictionary=True)

    # GET QUIZ

    cursor.execute("""
        SELECT *
        FROM quizzes
        WHERE id=%s
    """, (quiz_id,))

    quiz = cursor.fetchone()

    # CHECK ANSWER

    if selected_answer == quiz['correct_answer']:

        result = "✅ Correct Answer!"
        score = 1

    else:

        result = f"❌ Wrong Answer! Correct Answer: {quiz['correct_answer']}"
        score = 0

    # SAVE QUIZ RESULT

    insert_query = """
    INSERT INTO quiz_results
    (
        student_name,
        quiz_id,
        question,
        selected_answer,
        correct_answer,
        score
    )
    VALUES(%s,%s,%s,%s,%s,%s)
    """

    values = (
        session['user'],
        quiz_id,
        quiz['question'],
        selected_answer,
        quiz['correct_answer'],
        score
    )

    cursor.execute(insert_query, values)

    db.commit()

    cursor.close()

    return render_template(
        'quiz_result.html',
        result=result
    )
# =========================
# TEACHER QUIZ RESULTS
# =========================

@app.route('/teacher/quiz-results')
def teacher_quiz_results():

    if session.get('role') != 'teacher':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM quiz_results
        ORDER BY submitted_at DESC
    """)

    results = cursor.fetchall()

    cursor.close()

    return render_template(
        'teacher_quiz_results.html',
        results=results
    )
# =========================
# CLOUD PAGE
# =========================

@app.route('/cloud')
def cloud():

    return render_template('cloud.html')

# =========================
# RUN APP
# =========================

if __name__ == '__main__':
    app.run(debug=True)

