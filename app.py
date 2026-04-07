from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import mysql.connector
from config import DB_CONFIG
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'kyc_secret_key_2024'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

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
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT id, name FROM states ORDER BY name')
    states = cursor.fetchall()

    cursor.execute('SELECT id, name FROM occupations ORDER BY name')
    occupations = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('kyc_form.html', states=states, occupations=occupations)

# Get districts by state (for dropdown)
@app.route('/get_districts/<int:state_id>')
def get_districts(state_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, name FROM districts WHERE state_id = %s ORDER BY name', (state_id,))
    districts = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(districts)

# Get cities by district (for dropdown)
@app.route('/get_cities/<int:district_id>')
def get_cities(district_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
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

        # Get all form fields
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
            request.form.get('place_of_birth'),
            request.form.get('street'),
            request.form.get('area'),
            request.form.get('post_office'),
            request.form.get('pincode'),
            request.form.get('address_type'),
            request.form.get('permanent_same_as_current'),
            request.form.get('permanent_address'),
            request.form.get('city_id') or None,
            request.form.get('district_id') or None,
            request.form.get('state_id') or None,
            request.form.get('occupation_id') or None,
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
            )
        ''', data)

        account_id = cursor.lastrowid

        # Handle file uploads
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
    cursor = conn.cursor(dictionary=True)
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
    cursor = conn.cursor(dictionary=True)

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