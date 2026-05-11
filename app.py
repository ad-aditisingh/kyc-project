from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import psycopg
import psycopg.rows
from config import DATABASE_URL
import os
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-dev-secret")

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_connection():
    # FIX 1: Added sslmode="require" for Render/Neon PostgreSQL compatibility
    return psycopg.connect(DATABASE_URL, sslmode="require")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_form_data(form):
    errors = []

    email = form.get('email', '').strip()
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        errors.append('Invalid email address.')

    mobile = form.get('mobile', '').strip()
    if not re.fullmatch(r'\d{10}', mobile):
        errors.append('Mobile number must be exactly 10 digits.')

    alt_mobile = form.get('alternate_mobile', '').strip()
    if alt_mobile and not re.fullmatch(r'\d{10}', alt_mobile):
        errors.append('Alternate mobile number must be exactly 10 digits.')

    aadhaar = form.get('aadhaar_number', '').strip()
    if not re.fullmatch(r'\d{12}', aadhaar):
        errors.append('Aadhaar number must be exactly 12 digits.')

    pan = form.get('pan_number', '').strip().upper()
    if not re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', pan):
        errors.append('Invalid PAN number. Expected format: ABCDE1234F')

    pincode = form.get('pincode', '').strip()
    if not re.fullmatch(r'\d{6}', pincode):
        errors.append('Pincode must be exactly 6 digits.')

    # FIX 4 verified: field names match kyc_form.html exactly
    for field in ['email_otp', 'mobile_otp', 'aadhaar_otp']:
        otp = form.get(field, '').strip()
        if not re.fullmatch(r'\d{4,6}', otp):
            errors.append('OTP must be 4-6 digits.')
            break

    return errors


# FIX 2: Removed automatic init_db() execution block entirely.
# Run `python database.py` manually once before first deployment.
# Auto-running on every startup causes slow startups and Render health check failures.


@app.route('/')
def index():
    return redirect(url_for('kyc_form'))


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


@app.route('/get_districts/<int:state_id>')
def get_districts(state_id):
    conn = get_connection()
    cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
    cursor.execute('SELECT id, name FROM districts WHERE state_id = %s ORDER BY name', (state_id,))
    districts = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(districts)


@app.route('/get_cities/<int:district_id>')
def get_cities(district_id):
    conn = get_connection()
    cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
    cursor.execute('SELECT id, name FROM cities WHERE district_id = %s ORDER BY name', (district_id,))
    cities = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(cities)


@app.route('/submit_kyc', methods=['POST'])
def submit_kyc():
    try:
        validation_errors = validate_form_data(request.form)
        if validation_errors:
            for error in validation_errors:
                flash(error, 'danger')
            return redirect(url_for('kyc_form'))

        conn = get_connection()
        cursor = conn.cursor()

        # FIX 3 verified: 43 columns, 43 placeholders, 43 tuple items — all match
        data = (
            request.form.get('account_type'),
            request.form.get('customer_type'),
            request.form.get('preferred_branch'),
            request.form.get('date_of_application'),
            request.form.get('email'),
            request.form.get('mobile'),
            request.form.get('alternate_mobile') or None,
            request.form.get('aadhaar_number'),
            request.form.get('aadhaar_name'),
            request.form.get('dob'),
            request.form.get('gender'),
            request.form.get('full_name'),
            request.form.get('father_name'),
            request.form.get('mother_name'),
            request.form.get('spouse_name') or None,
            request.form.get('marital_status'),
            request.form.get('nationality'),
            request.form.get('religion') or None,
            request.form.get('residential_status'),
            request.form.get('place_of_birth') or request.form.get('place_of_birth_other') or None,
            request.form.get('street'),
            request.form.get('area'),
            request.form.get('post_office'),
            request.form.get('pincode'),
            request.form.get('address_type'),
            request.form.get('permanent_same_as_current'),
            request.form.get('permanent_address') or None,
            int(request.form.get('city_id')) if request.form.get('city_id') else None,
            int(request.form.get('district_id')) if request.form.get('district_id') else None,
            int(request.form.get('state_id')) if request.form.get('state_id') else None,
            int(request.form.get('occupation_id')) if request.form.get('occupation_id') else None,
            request.form.get('employer_name') or None,
            request.form.get('nature_of_business') or None,
            request.form.get('designation') or None,
            request.form.get('annual_income'),
            request.form.get('source_of_funds'),
            request.form.get('pan_number'),
            request.form.get('pan_holder_name'),
            request.form.get('driving_licence') or None,
            request.form.get('driving_licence_dob') or None,
            request.form.get('driving_licence_name') or None,
            request.form.get('location_village') or None,
            request.form.get('country') or None,
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
            if file and file.filename and allowed_file(file.filename):
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
            save_file('signature'),
        ))

        conn.commit()
        cursor.close()
        conn.close()

        flash('KYC Form submitted successfully!', 'success')
        return redirect(url_for('success', account_id=account_id))

    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('kyc_form'))


@app.route('/success/<int:account_id>')
def success(account_id):
    return render_template('success.html', account_id=account_id)


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
            request.form.get('alternate_mobile') or None,
            request.form.get('employer_name') or None,
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