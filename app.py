from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import psycopg
import psycopg.rows
from config import DATABASE_URL
import os
import re
from datetime import datetime, date
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-dev-secret")

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_connection():
    return psycopg.connect(DATABASE_URL, sslmode="require")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_form_data(form, files=None):
    errors = []
    today = date.today()

    #  EMAIL
    email = form.get('email', '').strip()
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        errors.append('Invalid email address.')

    #  MOBILE 
    mobile = form.get('mobile', '').strip()
    if not re.fullmatch(r'\d{10}', mobile):
        errors.append('Mobile number must be exactly 10 digits.')

    alt_mobile = form.get('alternate_mobile', '').strip()
    if alt_mobile and not re.fullmatch(r'\d{10}', alt_mobile):
        errors.append('Alternate mobile number must be exactly 10 digits.')

    #  AADHAAR 
    aadhaar = form.get('aadhaar_number', '').strip()
    if not re.fullmatch(r'\d{12}', aadhaar):
        errors.append('Aadhaar number must be exactly 12 digits.')

    #  PAN 
    if not re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', pan):
        errors.append('Invalid PAN number. Expected format: ABCDE1234F')

    #  PINCODE 
    pincode = form.get('pincode', '').strip()
    if not re.fullmatch(r'\d{6}', pincode):
        errors.append('Pincode must be exactly 6 digits.')

    #  OTPs (4–6 numeric digits) 
    for field in ['email_otp', 'mobile_otp', 'aadhaar_otp']:
        otp = form.get(field, '').strip()
        if not re.fullmatch(r'\d{4,6}', otp):
            errors.append(f'OTP ({field}) must be 4–6 numeric digits.')
            break

    #  DATE VALIDATION 
    doa_val = form.get('date_of_application', '').strip()
    if not doa_val:
        errors.append('Date of Application is required.')
    else:
        try:
            doa_date = datetime.strptime(doa_val, '%Y-%m-%d').date()
            if doa_date > today:
                errors.append('Date of Application cannot be a future date.')
        except ValueError:
            errors.append('Date of Application has an invalid date format.')

    # Date of Birth: 
    dob_val = form.get('dob', '').strip()
    if not dob_val:
        errors.append('Date of Birth is required.')
    else:
        try:
            dob_date = datetime.strptime(dob_val, '%Y-%m-%d').date()
            if dob_date > today:
                errors.append('Date of Birth cannot be a future date.')
            elif dob_date.year < 1900:
                errors.append('Date of Birth seems invalid (before 1900).')
        except ValueError:
            errors.append('Date of Birth has an invalid date format.')

    #  REQUIRED DROPDOWNS  
    required_dropdowns = {
        'account_type':       'Account Type',
        'customer_type':      'Customer Type',
        'gender':             'Gender',
        'marital_status':     'Marital Status',
        'residential_status': 'Residential Status',
        'address_type':       'Address Type',
        'occupation_id':      'Occupation Type',
        'annual_income':      'Annual Income Range',
        'source_of_funds':    'Source of Funds',
    }
    for field, label in required_dropdowns.items():
        val = form.get(field, '').strip()
        if not val or val.startswith('--') or val == '0':
            errors.append(f'{label} is required. Please select a valid option.')

    #  NAME FIELDS  
    
    name_fields = {
        'full_name':       ('Full Legal Name',   2, 100),
        'father_name':     ("Father's Name",     2, 100),
        'mother_name':     ("Mother's Name",     2, 100),
        'aadhaar_name':    ('Aadhaar Name',      2, 100),
        'pan_holder_name': ('PAN Holder Name',   2, 100),
        'nationality':     ('Nationality',        2,  50),
    }
    for field, (label, min_len, max_len) in name_fields.items():
        val = form.get(field, '').strip()
        if not val:
            errors.append(f'{label} is required.')
        elif not re.fullmatch(r"[A-Za-z\s.'-]+", val):
            errors.append(f'{label} must contain letters and spaces only (no numbers or special characters).')
        elif len(val) < min_len:
            errors.append(f'{label} must be at least {min_len} characters.')
        elif len(val) > max_len:
            errors.append(f'{label} must be at most {max_len} characters.')

    branch = form.get('preferred_branch', '').strip()
    if not branch:
        errors.append('Preferred Branch is required.')
    elif len(branch) < 2:
        errors.append('Preferred Branch must be at least 2 characters.')
    elif len(branch) > 100:
        errors.append('Preferred Branch must be at most 100 characters.')
    elif re.search(r'[@#$%^&*<>{}|\\]', branch):
        errors.append('Preferred Branch contains invalid special characters.')

    optional_name_fields = {
        'spouse_name': 'Spouse/Guardian Name',
        'driving_licence_name': 'Driving Licence Name',
    }

    for field, label in optional_name_fields.items():
        val = form.get(field, '').strip()

        if val and not re.fullmatch(r"[A-Za-z\s.'-]+", val):
            errors.append(f'{label} must contain letters and spaces only.')

    employer_name = form.get('employer_name', '').strip()

    if employer_name:
        if len(employer_name) < 2 or len(employer_name) > 100:
            errors.append('Employer Name must be between 2 and 100 characters.')

        elif re.search(r'[@#$%^*<>{}|\\]', employer_name):
            errors.append('Employer Name contains invalid special characters.')

    #  ADDRESS FIELDS (min/max length) 
    address_fields = {
        'street':           ('Street/House/Landmark', 5, 200),
        'area':             ('Area/Locality',          2, 100),
        'location_village': ('Location/Village/Town',  2, 100),
        'post_office':      ('Post Office',            2, 100),
    }
    for field, (label, min_len, max_len) in address_fields.items():
        val = form.get(field, '').strip()
        if not val:
            errors.append(f'{label} is required.')
        elif len(val) < min_len:
            errors.append(f'{label} must be at least {min_len} characters.')
        elif len(val) > max_len:
            errors.append(f'{label} must be at most {max_len} characters.')

    #  COUNTRY (required) 
    country_val = form.get('country', '').strip()

    if not country_val:
        errors.append('Country is required.')

    elif not re.fullmatch(r"[A-Za-z\s.'-]+", country_val):
        errors.append('Country must contain letters and spaces only.')

    elif len(country_val) < 2 or len(country_val) > 50:
        errors.append('Country must be between 2 and 50 characters.')

    #  MANDATORY FILE UPLOADS 
    if files is not None:
        mandatory_files = {
            'aadhaar_front': 'Aadhaar Card Front',
            'aadhaar_back':  'Aadhaar Card Back',
            'pan_card':      'PAN Card',
            'signature':     'Signature Scan',
        }
        allowed_exts = {'pdf', 'jpg', 'jpeg'}
        for field, label in mandatory_files.items():
            file = files.get(field)
            if not file or not file.filename:
                errors.append(f'{label} upload is required.')
            else:
                ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
                if ext not in allowed_exts:
                    errors.append(f'{label} must be a PDF or JPG/JPEG file.')

        for field in ['passport_dl', 'address_proof']:
            file = files.get(field)
            if file and file.filename:
                ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
                if ext not in allowed_exts:
                    errors.append(f'{field.replace("_", " ").title()} must be a PDF or JPG/JPEG file.')

    return errors




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
    conn = None
    try:
        validation_errors = validate_form_data(request.form, files=request.files)
        if validation_errors:
            for error in validation_errors:
                flash(error, 'danger')
            return redirect(url_for('kyc_form'))

        conn = get_connection()
        cursor = conn.cursor()

        #  FOREIGN KEY VALIDATION 
        state_id_val = request.form.get('state_id', '').strip()
        if not state_id_val:
            flash('State is required. Please select a state.', 'danger')
            return redirect(url_for('kyc_form'))
        cursor.execute('SELECT id FROM states WHERE id = %s', (int(state_id_val),))
        if not cursor.fetchone():
            flash('Selected State does not exist. Please select a valid state.', 'danger')
            return redirect(url_for('kyc_form'))

        # Validate district_id exists
        district_id_val = request.form.get('district_id', '').strip()
        if not district_id_val:
            flash('District is required. Please select a district.', 'danger')
            return redirect(url_for('kyc_form'))
        cursor.execute('SELECT id FROM districts WHERE id = %s', (int(district_id_val),))
        if not cursor.fetchone():
            flash('Selected District does not exist. Please select a valid district.', 'danger')
            return redirect(url_for('kyc_form'))

        # Validate city_id exists (optional — may be None if district has no cities)
        city_id_val = request.form.get('city_id', '').strip()
        if city_id_val:
            cursor.execute('SELECT id FROM cities WHERE id = %s', (int(city_id_val),))
            if not cursor.fetchone():
                flash('Selected City does not exist. Please select a valid city.', 'danger')
                return redirect(url_for('kyc_form'))

        # Validate occupation_id exists
        occupation_id_val = request.form.get('occupation_id', '').strip()
        if not occupation_id_val:
            flash('Occupation Type is required.', 'danger')
            return redirect(url_for('kyc_form'))
        cursor.execute('SELECT id FROM occupations WHERE id = %s', (int(occupation_id_val),))
        if not cursor.fetchone():
            flash('Selected Occupation does not exist. Please select a valid occupation.', 'danger')
            return redirect(url_for('kyc_form'))

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
            int(city_id_val) if city_id_val else None,
            int(district_id_val),
            int(state_id_val),
            int(occupation_id_val),
            request.form.get('employer_name') or None,
            request.form.get('nature_of_business') or None,
            request.form.get('designation') or None,
            request.form.get('annual_income'),
            request.form.get('source_of_funds'),
            request.form.get('pan_number', '').strip().upper(),
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
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
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
        if conn is not None:
            conn.rollback()
        flash(f'An error occurred while submitting the form. Please try again. ({str(e)})', 'danger')
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
        update_errors = []

        # Validate email
        email_val = request.form.get('email', '').strip()
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email_val):
            update_errors.append('Invalid email address.')

        # Validate mobile
        mobile_val = request.form.get('mobile', '').strip()
        if not re.fullmatch(r'\d{10}', mobile_val):
            update_errors.append('Mobile number must be exactly 10 digits.')

        # Validate alternate mobile (optional)
        alt_mob = request.form.get('alternate_mobile', '').strip()
        if alt_mob and not re.fullmatch(r'\d{10}', alt_mob):
            update_errors.append('Alternate mobile must be exactly 10 digits.')

        branch_val = request.form.get('preferred_branch', '').strip()
        if not branch_val:
            update_errors.append('Preferred Branch is required.')
        elif len(branch_val) < 2 or len(branch_val) > 100:
            update_errors.append('Preferred Branch must be between 2 and 100 characters.')
        elif re.search(r'[@#$%^&*<>{}|\\]', branch_val):
            update_errors.append('Preferred Branch contains invalid special characters.')

        # Validate employer_name (optional)
        employer_val = request.form.get('employer_name', '').strip()
        if employer_val and re.search(r'[@#$%^*<>{}|\\]', employer_val):
            update_errors.append('Employer Name contains invalid special characters.')

        # Validate required dropdowns
        account_type_val = request.form.get('account_type', '').strip()
        if not account_type_val or account_type_val.startswith('--'):
            update_errors.append('Account Type is required.')

        customer_type_val = request.form.get('customer_type', '').strip()
        if not customer_type_val or customer_type_val.startswith('--'):
            update_errors.append('Customer Type is required.')

        annual_income_val = request.form.get('annual_income', '').strip()
        if not annual_income_val or annual_income_val.startswith('--'):
            update_errors.append('Annual Income Range is required.')

        source_of_funds_val = request.form.get('source_of_funds', '').strip()
        if not source_of_funds_val or source_of_funds_val.startswith('--'):
            update_errors.append('Source of Funds is required.')

        if update_errors:
            for err in update_errors:
                flash(err, 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('update_kyc', account_id=account_id))

        data = (
            account_type_val,
            customer_type_val,
            branch_val,
            email_val,
            mobile_val,
            alt_mob or None,
            employer_val or None,
            annual_income_val,
            source_of_funds_val,
            account_id
        )
        cursor.execute('''
            UPDATE accounts SET
                account_type = %s,
                customer_type = %s,
                preferred_branch = %s,
                email = %s,
                mobile = %s,
                alternate_mobile = %s,
                employer_name = %s,
                annual_income = %s,
                source_of_funds = %s
            WHERE id = %s
        ''', data)
        conn.commit()
        cursor.close()
        conn.close()
        flash('KYC updated successfully!', 'success')
        return redirect(url_for('submissions'))

    cursor.execute('SELECT * FROM accounts WHERE id = %s', (account_id,))
    account = cursor.fetchone()
    if not account:
        cursor.close()
        conn.close()
        flash('Account not found.', 'danger')
        return redirect(url_for('submissions'))

    cursor.execute('SELECT id, name FROM states ORDER BY name')
    states = cursor.fetchall()
    cursor.execute('SELECT id, name FROM occupations ORDER BY name')
    occupations = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('update_kyc.html', account=account, states=states, occupations=occupations)


if __name__ == '__main__':
    app.run(debug=True)