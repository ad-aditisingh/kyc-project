

<!DOCTYPE html> <html lang="en"> <head> <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>KYC Registration Form</title> <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

pasted


<!DOCTYPE html> <html lang="en"> <head> <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>KYC Submissions</title> <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"> <link

pasted


<!DOCTYPE html> <html lang="en"> <head> <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>KYC Submitted</title> <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"> <link h

pasted


<!DOCTYPE html> <html lang="en"> <head> <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>Update KYC</title> <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"> <link href

pasted


from flask import Flask, render_template, request, jsonify, redirect, url_for, flash #import mysql.connector import psycopg #from config import DB_CONFIG from config import DATABASE_URL import psycopg.rows import os from werkzeug.utils import secure_filename app = Flask(__name__) app.secr

pasted


import psycopg from config import DATABASE_URL def get_connection(): return psycopg.connect(DATABASE_URL) def init_db(): conn = get_connection() cursor = conn.cursor() # States table cursor.execute(''' CREATE TABLE IF N

pasted

venv/
__pycache__/
*.pyc
*.db
.env
static/uploads/
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kyc_database_user:aiEcoZcqPwehsoisESvm5YGSP5re0HLD@dpg-d7b4mtpr0fns738b0qpg-a/kyc_database")
web: gunicorn app:app this is my Kyc application but there are inconsistensies and when i deploy on render it is giving error Select row
kyc-project
Options
Status
Failed deploy
Runtime
Python 3
Region
virginia
Updated
2d
1. Select row
kyc-database
Options
Status
Available
Runtime
PostgreSQL 18
Region
virginia
Updated
2d

Show more
8:41 AM
Let me analyze your code carefully for all the bugs and inconsistencies before fixing them.


Check skills available
Check skills available
Here's a comprehensive breakdown of every bug I found, followed by the fully corrected files:

Bugs Found in app.py:

Mixed DB drivers — psycopg (v3) is imported but psycopg2.extras.RealDictCursor is used in most routes. psycopg3 uses row_factory=psycopg.rows.dict_row instead.
get_districts and get_cities — still use the old psycopg2 cursor syntax.
submissions() and update_kyc() — same wrong cursor syntax.
update_kyc POST — missing conn.commit() before cursor/conn close (it's there but cursor is not closed before redirect).
Bugs Found in init_db.py:

id INT SERIAL PRIMARY KEY — invalid PostgreSQL syntax. Should be id SERIAL PRIMARY KEY.
FOREIGN KEY syntax — PostgreSQL doesn't use inline FOREIGN KEY (col) REFERENCES in CREATE TABLE the same way; must use REFERENCES inline or a separate constraint. The inline FOREIGN KEY keyword is wrong syntax in psycopg.
Indentation errors — the for state in states: loop and everything after it is wrongly indented (outside the function body).
district_ids[name] = cursor.fetchone()[0] — after an INSERT without RETURNING id, fetchone() returns None. Needs RETURNING id.
Missing RETURNING id on district insert.

Created 2 files, read a file
Created 2 files, read a file
Here's a full summary of every bug that was fixed:

app.py — 4 bugs fixed
Bug 1 — Mixed psycopg2 / psycopg3 cursor syntax (critical) Every route except kyc_form was still using cursor_factory=psycopg2.extras.RealDictCursor, which doesn't exist in psycopg3. All cursors are now unified to use row_factory=psycopg.rows.dict_row.

Bug 2 — get_districts and get_cities used wrong cursor Both API routes were using the psycopg2 cursor style and would crash on every dropdown load.

Bug 3 — submissions() and update_kyc() used wrong cursor Same issue — both would crash when loading the submissions list or edit page.

Bug 4 — update_kyc POST didn't close cursor before redirect Cursor and connection are now properly closed before the redirect on POST.

init_db.py — 4 bugs fixed
Bug 5 — id INT SERIAL PRIMARY KEY is invalid PostgreSQL PostgreSQL doesn't allow INT SERIAL together — SERIAL already implies integer. Fixed to id SERIAL PRIMARY KEY on both accounts and document_uploads tables.

Bug 6 — Inline FOREIGN KEY (col) REFERENCES syntax is invalid in psycopg The original used FOREIGN KEY (city_id) REFERENCES cities(id) as a column-level clause, which is wrong syntax. Changed all foreign keys to inline column-level REFERENCES, e.g. city_id INT REFERENCES cities(id).

Bug 7 — Entire data seeding block was outside the function (indentation error) The for state in states: loop and everything after it was indented incorrectly, making it module-level code that ran before the function was even called properly.

Bug 8 — District insert missing RETURNING id cursor.execute('INSERT INTO districts ...') was followed by cursor.fetchone()[0] but without RETURNING id in the SQL, fetchone() returns None, causing a crash. Added RETURNING id to the district insert.


App
PY 

Init db
PY 

Want to be notified when Claude responds?



Claude is AI and can make mistakes. Please double-check responses.
App · PY
Copy

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import psycopg
import psycopg.rows
from config import DATABASE_URL
import os
from werkzeug.utils import secure_filename
 
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-dev-secret")
 
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
 
 
def get_connection():
    return psycopg.connect(DATABASE_URL)
 
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
 
# Home route
@app.route('/')
def index():
    return redirect(url_for('kyc_form'))
 
 
# KYC Form route
@app.route('/kyc', methods=['GET'])
def kyc_form():
    conn = get_connection()
    cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
 
    cursor.execute('SELECT id, name FROM states ORDER BY name')
    states = cursor.fetchall()
 
    cursor.execute('SELECT id, name FROM occupations ORDER BY name')
    occupations = cursor.fetchall()
 
    cursor.close()
    conn.close()
 
    return render_template('kyc_form.html', states=states, occupations=occupations)
 
 
# Get districts by state for dropdown
@app.route('/get_districts/<int:state_id>')
def get_districts(state_id):
    conn = get_connection()
    cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
    cursor.execute('SELECT id, name FROM districts WHERE state_id = %s ORDER BY name', (state_id,))
    districts = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(districts)
 
 
# Get cities by district for dropdown
@app.route('/get_cities/<int:district_id>')
def get_cities(district_id):
    conn = get_connection()
    cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
    cursor.execute('SELECT id, name FROM cities WHERE district_id = %s ORDER BY name', (district_id,))
    cities = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(cities)
 
 
# Submit KYC form
@app.route('/submit_kyc', methods=['POST'])
def submit_kyc():
    try:
        conn = get_connection()
        cursor = conn.cursor()
 
        data = (
            request.form.get('account_type'),
            request.form.get('customer_type'),
            request.form.get('preferred_branch'),
            request.form.get('date_of_application'),
            request.form.get('email'),
            request.form.get('mobile'),
            request.form.get('alternate_mobile'),
            request.form.get('aadhaar_number'),
            request.form.get('aadhaar_name'),
            request.form.get('dob'),
            request.form.get('gender'),
            request.form.get('full_name'),
            request.form.get('father_name'),
            request.form.get('mother_name'),
            request.form.get('spouse_name'),
            request.form.get('marital_status'),
            request.form.get('nationality'),
            request.form.get('religion'),
            request.form.get('residential_status'),
            request.form.get('place_of_birth') or request.form.get('place_of_birth_other'),
            request.form.get('street'),
            request.form.get('area'),
            request.form.get('post_office'),
            request.form.get('pincode'),
            request.form.get('address_type'),
            request.form.get('permanent_same_as_current'),
            request.form.get('permanent_address'),
            int(request.form.get('city_id')) if request.form.get('city_id') else None,
            int(request.form.get('district_id')) if request.form.get('district_id') else None,
            int(request.form.get('state_id')) if request.form.get('state_id') else None,
            int(request.form.get('occupation_id')) if request.form.get('occupation_id') else None,
            request.form.get('employer_name'),
            request.form.get('nature_of_business'),
            request.form.get('designation'),
            request.form.get('annual_income'),
            request.form.get('source_of_funds'),
            request.form.get('pan_number'),
            request.form.get('pan_holder_name'),
            request.form.get('driving_licence'),
            request.form.get('driving_licence_dob') or None,
            request.form.get('driving_licence_name'),
            request.form.get('location_village'),
            request.form.get('country'),
        )
 
        cursor.execute('''
            INSERT INTO accounts (
                account_type, customer_type, preferred_branch,
                date_of_application, email, mobile, alternate_mobile,
                aadhaar_number, aadhaar_name, dob, gender,
                full_name, father_name, mother_name, spouse_name,
                marital_status, nationality, religion, residential_status,
                place_of_birth, street, area, post_office, pincode,
                address_type, permanent_same_as_current, permanent_address,
                city_id, district_id, state_id, occupation_id,
                employer_name, nature_of_business, designation,
                annual_income, source_of_funds, pan_number,
                pan_holder_name, driving_licence, driving_licence_dob,
                driving_licence_name, location_village, country
            ) VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
            ) RETURNING id
        ''', data)
 
        account_id = cursor.fetchone()[0]
 
        def save_file(field_name):
            file = request.files.get(field_name)
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{account_id}_{field_name}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return filename
            return None
 
        cursor.execute('''
            INSERT INTO document_uploads (
                account_id, aadhaar_front, aadhaar_back,
                pan_card, passport_dl, address_proof, signature
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            account_id,
            save_file('aadhaar_front'),
            save_file('aadhaar_back'),
            save_file('pan_card'),
            save_file('passport_dl'),
            save_file('address_proof'),
            save_file('signature')
        ))
 
        conn.commit()
        cursor.close()
        conn.close()
 
        flash('KYC Form submitted successfully!', 'success')
        return redirect(url_for('success', account_id=account_id))
 
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('kyc_form'))
 
 
# Success page
@app.route('/success/<int:account_id>')
def success(account_id):
    return render_template('success.html', account_id=account_id)
 
 
# View all submissions
@app.route('/submissions')
def submissions():
    conn = get_connection()
    cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
    cursor.execute('''
        SELECT a.id, a.full_name, a.email, a.mobile,
               a.pan_number, a.account_type, a.created_at,
               s.name as state_name
        FROM accounts a
        LEFT JOIN states s ON a.state_id = s.id
        ORDER BY a.created_at DESC
    ''')
    accounts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('submissions.html', accounts=accounts)
 
 
# Update KYC
@app.route('/update/<int:account_id>', methods=['GET', 'POST'])
def update_kyc(account_id):
    conn = get_connection()
    cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
 
    if request.method == 'POST':
        data = (
            request.form.get('account_type'),
            request.form.get('customer_type'),
            request.form.get('preferred_branch'),
            request.form.get('email'),
            request.form.get('mobile'),
            request.form.get('alternate_mobile'),
            request.form.get('employer_name'),
            request.form.get('annual_income'),
            request.form.get('source_of_funds'),
            account_id
        )
        cursor.execute('''
            UPDATE accounts SET
                account_type=%s, customer_type=%s,
                preferred_branch=%s, email=%s, mobile=%s,
                alternate_mobile=%s, employer_name=%s,
                annual_income=%s, source_of_funds=%s
            WHERE id=%s
        ''', data)
        conn.commit()
        cursor.close()
        conn.close()
        flash('KYC updated successfully!', 'success')
        return redirect(url_for('submissions'))
 
    cursor.execute('SELECT * FROM accounts WHERE id = %s', (account_id,))
    account = cursor.fetchone()
    cursor.execute('SELECT id, name FROM states ORDER BY name')
    states = cursor.fetchall()
    cursor.execute('SELECT id, name FROM occupations ORDER BY name')
    occupations = cursor.fetchall()
    cursor.close()
    conn.close()
 
    return render_template('update_kyc.html', account=account, states=states, occupations=occupations)
 
 
if __name__ == '__main__':
    app.run(debug=True)
 
