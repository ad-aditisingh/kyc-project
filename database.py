import mysql.connector
from config import DATABASE_URL

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # States table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS states (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
    ''')

    # Districts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS districts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            state_id INT,
            FOREIGN KEY (state_id) REFERENCES states(id)
        )
    ''')

    # Cities table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cities (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            district_id INT,
            FOREIGN KEY (district_id) REFERENCES districts(id)
        )
    ''')

    # Occupations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS occupations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
    ''')

    # Main KYC accounts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            account_type VARCHAR(50) NOT NULL,
            customer_type VARCHAR(50) NOT NULL,
            preferred_branch VARCHAR(100) NOT NULL,
            date_of_application DATE NOT NULL,
            email VARCHAR(100) NOT NULL,
            mobile VARCHAR(10) NOT NULL,
            alternate_mobile VARCHAR(10),
            aadhaar_number VARCHAR(12) NOT NULL,
            aadhaar_name VARCHAR(100) NOT NULL,
            dob DATE NOT NULL,
            gender VARCHAR(10) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            father_name VARCHAR(100) NOT NULL,
            mother_name VARCHAR(100) NOT NULL,
            spouse_name VARCHAR(100),
            marital_status VARCHAR(20) NOT NULL,
            nationality VARCHAR(50) NOT NULL,
            religion VARCHAR(50),
            residential_status VARCHAR(20) NOT NULL,
            place_of_birth VARCHAR(100),
            street VARCHAR(200) NOT NULL,
            area VARCHAR(100) NOT NULL,
            post_office VARCHAR(100) NOT NULL,
            pincode VARCHAR(6) NOT NULL,
            address_type VARCHAR(20) NOT NULL,
            permanent_same_as_current VARCHAR(3),
            permanent_address TEXT,
            city_id INT,
            district_id INT,
            state_id INT,
            occupation_id INT,
            employer_name VARCHAR(100),
            nature_of_business VARCHAR(100),
            designation VARCHAR(100),
            annual_income VARCHAR(50) NOT NULL,
            source_of_funds VARCHAR(50) NOT NULL,
            pan_number VARCHAR(10) NOT NULL,
            pan_holder_name VARCHAR(100) NOT NULL,
            driving_licence VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (city_id) REFERENCES cities(id),
            FOREIGN KEY (district_id) REFERENCES districts(id),
            FOREIGN KEY (state_id) REFERENCES states(id),
            FOREIGN KEY (occupation_id) REFERENCES occupations(id)
        )
    ''')

    # Document uploads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS document_uploads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            account_id INT NOT NULL,
            aadhaar_front VARCHAR(200),
            aadhaar_back VARCHAR(200),
            pan_card VARCHAR(200),
            passport_dl VARCHAR(200),
            address_proof VARCHAR(200),
            signature VARCHAR(200),
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
    ''')

# Insert all Indian states
    states = [
        'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar',
        'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh',
        'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra',
        'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
        'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
        'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
        # Union Territories
        'Andaman and Nicobar Islands', 'Chandigarh',
        'Dadra and Nagar Haveli and Daman and Diu', 'Delhi',
        'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry'
    ]

    state_ids = {}
    for state in states:
        cursor.execute('SELECT id FROM states WHERE name = %s', (state,))
        result = cursor.fetchone()
        if not result:
            cursor.execute('INSERT INTO states (name) VALUES (%s)', (state,))
            state_ids[state] = cursor.lastrowid
        else:
            state_ids[state] = result[0]

    # Insert districts for every state
    districts = [
        # Andhra Pradesh
        ('Anantapur', state_ids['Andhra Pradesh']),
        ('Chittoor', state_ids['Andhra Pradesh']),
        ('East Godavari', state_ids['Andhra Pradesh']),
        ('Guntur', state_ids['Andhra Pradesh']),
        ('Krishna', state_ids['Andhra Pradesh']),
        ('Kurnool', state_ids['Andhra Pradesh']),
        ('Nellore', state_ids['Andhra Pradesh']),
        ('Prakasam', state_ids['Andhra Pradesh']),
        ('Srikakulam', state_ids['Andhra Pradesh']),
        ('Visakhapatnam', state_ids['Andhra Pradesh']),
        ('Vizianagaram', state_ids['Andhra Pradesh']),
        ('West Godavari', state_ids['Andhra Pradesh']),
        ('YSR Kadapa', state_ids['Andhra Pradesh']),

        # Arunachal Pradesh
        ('Anjaw', state_ids['Arunachal Pradesh']),
        ('Changlang', state_ids['Arunachal Pradesh']),
        ('East Kameng', state_ids['Arunachal Pradesh']),
        ('Itanagar', state_ids['Arunachal Pradesh']),
        ('Tawang', state_ids['Arunachal Pradesh']),

        # Assam
        ('Baksa', state_ids['Assam']),
        ('Barpeta', state_ids['Assam']),
        ('Cachar', state_ids['Assam']),
        ('Dibrugarh', state_ids['Assam']),
        ('Guwahati', state_ids['Assam']),
        ('Jorhat', state_ids['Assam']),
        ('Kamrup', state_ids['Assam']),
        ('Nagaon', state_ids['Assam']),
        ('Silchar', state_ids['Assam']),

        # Bihar
        ('Araria', state_ids['Bihar']),
        ('Aurangabad', state_ids['Bihar']),
        ('Bhagalpur', state_ids['Bihar']),
        ('Gaya', state_ids['Bihar']),
        ('Muzaffarpur', state_ids['Bihar']),
        ('Nalanda', state_ids['Bihar']),
        ('Patna', state_ids['Bihar']),
        ('Purnia', state_ids['Bihar']),
        ('Rohtas', state_ids['Bihar']),
        ('Saran', state_ids['Bihar']),

        # Chhattisgarh
        ('Bastar', state_ids['Chhattisgarh']),
        ('Bilaspur', state_ids['Chhattisgarh']),
        ('Durg', state_ids['Chhattisgarh']),
        ('Korba', state_ids['Chhattisgarh']),
        ('Raipur', state_ids['Chhattisgarh']),
        ('Rajnandgaon', state_ids['Chhattisgarh']),
        ('Surguja', state_ids['Chhattisgarh']),

        # Goa
        ('North Goa', state_ids['Goa']),
        ('South Goa', state_ids['Goa']),

        # Gujarat
        ('Ahmedabad', state_ids['Gujarat']),
        ('Amreli', state_ids['Gujarat']),
        ('Anand', state_ids['Gujarat']),
        ('Bharuch', state_ids['Gujarat']),
        ('Bhavnagar', state_ids['Gujarat']),
        ('Gandhinagar', state_ids['Gujarat']),
        ('Jamnagar', state_ids['Gujarat']),
        ('Junagadh', state_ids['Gujarat']),
        ('Kutch', state_ids['Gujarat']),
        ('Rajkot', state_ids['Gujarat']),
        ('Surat', state_ids['Gujarat']),
        ('Vadodara', state_ids['Gujarat']),

        # Haryana
        ('Ambala', state_ids['Haryana']),
        ('Faridabad', state_ids['Haryana']),
        ('Gurugram', state_ids['Haryana']),
        ('Hisar', state_ids['Haryana']),
        ('Karnal', state_ids['Haryana']),
        ('Panipat', state_ids['Haryana']),
        ('Rohtak', state_ids['Haryana']),
        ('Sonipat', state_ids['Haryana']),
        ('Yamunanagar', state_ids['Haryana']),

        # Himachal Pradesh
        ('Bilaspur', state_ids['Himachal Pradesh']),
        ('Chamba', state_ids['Himachal Pradesh']),
        ('Hamirpur', state_ids['Himachal Pradesh']),
        ('Kangra', state_ids['Himachal Pradesh']),
        ('Kullu', state_ids['Himachal Pradesh']),
        ('Mandi', state_ids['Himachal Pradesh']),
        ('Shimla', state_ids['Himachal Pradesh']),
        ('Solan', state_ids['Himachal Pradesh']),

        # Jharkhand
        ('Bokaro', state_ids['Jharkhand']),
        ('Deoghar', state_ids['Jharkhand']),
        ('Dhanbad', state_ids['Jharkhand']),
        ('Dumka', state_ids['Jharkhand']),
        ('Giridih', state_ids['Jharkhand']),
        ('Hazaribagh', state_ids['Jharkhand']),
        ('Jamshedpur', state_ids['Jharkhand']),
        ('Ranchi', state_ids['Jharkhand']),

        # Karnataka
        ('Bagalkot', state_ids['Karnataka']),
        ('Ballari', state_ids['Karnataka']),
        ('Belagavi', state_ids['Karnataka']),
        ('Bengaluru Rural', state_ids['Karnataka']),
        ('Bengaluru Urban', state_ids['Karnataka']),
        ('Bidar', state_ids['Karnataka']),
        ('Chamarajanagar', state_ids['Karnataka']),
        ('Chikkamagaluru', state_ids['Karnataka']),
        ('Dakshina Kannada', state_ids['Karnataka']),
        ('Davangere', state_ids['Karnataka']),
        ('Dharwad', state_ids['Karnataka']),
        ('Gadag', state_ids['Karnataka']),
        ('Hassan', state_ids['Karnataka']),
        ('Haveri', state_ids['Karnataka']),
        ('Kalaburagi', state_ids['Karnataka']),
        ('Kodagu', state_ids['Karnataka']),
        ('Kolar', state_ids['Karnataka']),
        ('Koppal', state_ids['Karnataka']),
        ('Mandya', state_ids['Karnataka']),
        ('Mysuru', state_ids['Karnataka']),
        ('Raichur', state_ids['Karnataka']),
        ('Ramanagara', state_ids['Karnataka']),
        ('Shivamogga', state_ids['Karnataka']),
        ('Tumakuru', state_ids['Karnataka']),
        ('Udupi', state_ids['Karnataka']),
        ('Uttara Kannada', state_ids['Karnataka']),
        ('Vijayapura', state_ids['Karnataka']),
        ('Yadgir', state_ids['Karnataka']),

        # Kerala
        ('Alappuzha', state_ids['Kerala']),
        ('Ernakulam', state_ids['Kerala']),
        ('Idukki', state_ids['Kerala']),
        ('Kannur', state_ids['Kerala']),
        ('Kasaragod', state_ids['Kerala']),
        ('Kollam', state_ids['Kerala']),
        ('Kottayam', state_ids['Kerala']),
        ('Kozhikode', state_ids['Kerala']),
        ('Malappuram', state_ids['Kerala']),
        ('Palakkad', state_ids['Kerala']),
        ('Pathanamthitta', state_ids['Kerala']),
        ('Thiruvananthapuram', state_ids['Kerala']),
        ('Thrissur', state_ids['Kerala']),
        ('Wayanad', state_ids['Kerala']),

        # Madhya Pradesh
        ('Bhopal', state_ids['Madhya Pradesh']),
        ('Gwalior', state_ids['Madhya Pradesh']),
        ('Indore', state_ids['Madhya Pradesh']),
        ('Jabalpur', state_ids['Madhya Pradesh']),
        ('Morena', state_ids['Madhya Pradesh']),
        ('Rewa', state_ids['Madhya Pradesh']),
        ('Sagar', state_ids['Madhya Pradesh']),
        ('Satna', state_ids['Madhya Pradesh']),
        ('Ujjain', state_ids['Madhya Pradesh']),

        # Maharashtra
        ('Ahmednagar', state_ids['Maharashtra']),
        ('Akola', state_ids['Maharashtra']),
        ('Amravati', state_ids['Maharashtra']),
        ('Aurangabad', state_ids['Maharashtra']),
        ('Beed', state_ids['Maharashtra']),
        ('Bhandara', state_ids['Maharashtra']),
        ('Buldhana', state_ids['Maharashtra']),
        ('Chandrapur', state_ids['Maharashtra']),
        ('Dhule', state_ids['Maharashtra']),
        ('Gadchiroli', state_ids['Maharashtra']),
        ('Gondia', state_ids['Maharashtra']),
        ('Hingoli', state_ids['Maharashtra']),
        ('Jalgaon', state_ids['Maharashtra']),
        ('Jalna', state_ids['Maharashtra']),
        ('Kolhapur', state_ids['Maharashtra']),
        ('Latur', state_ids['Maharashtra']),
        ('Mumbai City', state_ids['Maharashtra']),
        ('Mumbai Suburban', state_ids['Maharashtra']),
        ('Nagpur', state_ids['Maharashtra']),
        ('Nanded', state_ids['Maharashtra']),
        ('Nandurbar', state_ids['Maharashtra']),
        ('Nashik', state_ids['Maharashtra']),
        ('Osmanabad', state_ids['Maharashtra']),
        ('Palghar', state_ids['Maharashtra']),
        ('Parbhani', state_ids['Maharashtra']),
        ('Pune', state_ids['Maharashtra']),
        ('Raigad', state_ids['Maharashtra']),
        ('Ratnagiri', state_ids['Maharashtra']),
        ('Sangli', state_ids['Maharashtra']),
        ('Satara', state_ids['Maharashtra']),
        ('Sindhudurg', state_ids['Maharashtra']),
        ('Solapur', state_ids['Maharashtra']),
        ('Thane', state_ids['Maharashtra']),
        ('Wardha', state_ids['Maharashtra']),
        ('Washim', state_ids['Maharashtra']),
        ('Yavatmal', state_ids['Maharashtra']),

        # Manipur
        ('Bishnupur', state_ids['Manipur']),
        ('Churachandpur', state_ids['Manipur']),
        ('Imphal East', state_ids['Manipur']),
        ('Imphal West', state_ids['Manipur']),
        ('Senapati', state_ids['Manipur']),

        # Meghalaya
        ('East Khasi Hills', state_ids['Meghalaya']),
        ('Jaintia Hills', state_ids['Meghalaya']),
        ('West Garo Hills', state_ids['Meghalaya']),

        # Mizoram
        ('Aizawl', state_ids['Mizoram']),
        ('Champhai', state_ids['Mizoram']),
        ('Lunglei', state_ids['Mizoram']),

        # Nagaland
        ('Dimapur', state_ids['Nagaland']),
        ('Kohima', state_ids['Nagaland']),
        ('Mokokchung', state_ids['Nagaland']),

        # Odisha
        ('Angul', state_ids['Odisha']),
        ('Balasore', state_ids['Odisha']),
        ('Bargarh', state_ids['Odisha']),
        ('Bhubaneswar', state_ids['Odisha']),
        ('Cuttack', state_ids['Odisha']),
        ('Dhenkanal', state_ids['Odisha']),
        ('Ganjam', state_ids['Odisha']),
        ('Kendujhar', state_ids['Odisha']),
        ('Khordha', state_ids['Odisha']),
        ('Koraput', state_ids['Odisha']),
        ('Mayurbhanj', state_ids['Odisha']),
        ('Puri', state_ids['Odisha']),
        ('Sambalpur', state_ids['Odisha']),
        ('Sundargarh', state_ids['Odisha']),

        # Punjab
        ('Amritsar', state_ids['Punjab']),
        ('Bathinda', state_ids['Punjab']),
        ('Faridkot', state_ids['Punjab']),
        ('Fatehgarh Sahib', state_ids['Punjab']),
        ('Gurdaspur', state_ids['Punjab']),
        ('Hoshiarpur', state_ids['Punjab']),
        ('Jalandhar', state_ids['Punjab']),
        ('Ludhiana', state_ids['Punjab']),
        ('Moga', state_ids['Punjab']),
        ('Mohali', state_ids['Punjab']),
        ('Pathankot', state_ids['Punjab']),
        ('Patiala', state_ids['Punjab']),
        ('Rupnagar', state_ids['Punjab']),
        ('Sangrur', state_ids['Punjab']),

        # Rajasthan
        ('Ajmer', state_ids['Rajasthan']),
        ('Alwar', state_ids['Rajasthan']),
        ('Banswara', state_ids['Rajasthan']),
        ('Baran', state_ids['Rajasthan']),
        ('Barmer', state_ids['Rajasthan']),
        ('Bharatpur', state_ids['Rajasthan']),
        ('Bhilwara', state_ids['Rajasthan']),
        ('Bikaner', state_ids['Rajasthan']),
        ('Bundi', state_ids['Rajasthan']),
        ('Chittorgarh', state_ids['Rajasthan']),
        ('Churu', state_ids['Rajasthan']),
        ('Dausa', state_ids['Rajasthan']),
        ('Dholpur', state_ids['Rajasthan']),
        ('Dungarpur', state_ids['Rajasthan']),
        ('Hanumangarh', state_ids['Rajasthan']),
        ('Jaipur', state_ids['Rajasthan']),
        ('Jaisalmer', state_ids['Rajasthan']),
        ('Jalore', state_ids['Rajasthan']),
        ('Jhalawar', state_ids['Rajasthan']),
        ('Jhunjhunu', state_ids['Rajasthan']),
        ('Jodhpur', state_ids['Rajasthan']),
        ('Karauli', state_ids['Rajasthan']),
        ('Kota', state_ids['Rajasthan']),
        ('Nagaur', state_ids['Rajasthan']),
        ('Pali', state_ids['Rajasthan']),
        ('Pratapgarh', state_ids['Rajasthan']),
        ('Rajsamand', state_ids['Rajasthan']),
        ('Sawai Madhopur', state_ids['Rajasthan']),
        ('Sikar', state_ids['Rajasthan']),
        ('Sirohi', state_ids['Rajasthan']),
        ('Sri Ganganagar', state_ids['Rajasthan']),
        ('Tonk', state_ids['Rajasthan']),
        ('Udaipur', state_ids['Rajasthan']),

        # Sikkim
        ('East Sikkim', state_ids['Sikkim']),
        ('North Sikkim', state_ids['Sikkim']),
        ('South Sikkim', state_ids['Sikkim']),
        ('West Sikkim', state_ids['Sikkim']),

        # Tamil Nadu
        ('Chennai', state_ids['Tamil Nadu']),
        ('Coimbatore', state_ids['Tamil Nadu']),
        ('Cuddalore', state_ids['Tamil Nadu']),
        ('Dharmapuri', state_ids['Tamil Nadu']),
        ('Dindigul', state_ids['Tamil Nadu']),
        ('Erode', state_ids['Tamil Nadu']),
        ('Kanchipuram', state_ids['Tamil Nadu']),
        ('Kanyakumari', state_ids['Tamil Nadu']),
        ('Karur', state_ids['Tamil Nadu']),
        ('Krishnagiri', state_ids['Tamil Nadu']),
        ('Madurai', state_ids['Tamil Nadu']),
        ('Nagapattinam', state_ids['Tamil Nadu']),
        ('Namakkal', state_ids['Tamil Nadu']),
        ('Nilgiris', state_ids['Tamil Nadu']),
        ('Perambalur', state_ids['Tamil Nadu']),
        ('Pudukkottai', state_ids['Tamil Nadu']),
        ('Ramanathapuram', state_ids['Tamil Nadu']),
        ('Salem', state_ids['Tamil Nadu']),
        ('Sivaganga', state_ids['Tamil Nadu']),
        ('Thanjavur', state_ids['Tamil Nadu']),
        ('Theni', state_ids['Tamil Nadu']),
        ('Thoothukudi', state_ids['Tamil Nadu']),
        ('Tiruchirappalli', state_ids['Tamil Nadu']),
        ('Tirunelveli', state_ids['Tamil Nadu']),
        ('Tiruppur', state_ids['Tamil Nadu']),
        ('Tiruvallur', state_ids['Tamil Nadu']),
        ('Tiruvannamalai', state_ids['Tamil Nadu']),
        ('Tiruvarur', state_ids['Tamil Nadu']),
        ('Vellore', state_ids['Tamil Nadu']),
        ('Viluppuram', state_ids['Tamil Nadu']),
        ('Virudhunagar', state_ids['Tamil Nadu']),

        # Telangana
        ('Adilabad', state_ids['Telangana']),
        ('Hyderabad', state_ids['Telangana']),
        ('Karimnagar', state_ids['Telangana']),
        ('Khammam', state_ids['Telangana']),
        ('Mahabubnagar', state_ids['Telangana']),
        ('Medak', state_ids['Telangana']),
        ('Nalgonda', state_ids['Telangana']),
        ('Nizamabad', state_ids['Telangana']),
        ('Rangareddy', state_ids['Telangana']),
        ('Warangal', state_ids['Telangana']),

        # Tripura
        ('Dhalai', state_ids['Tripura']),
        ('Gomati', state_ids['Tripura']),
        ('Khowai', state_ids['Tripura']),
        ('North Tripura', state_ids['Tripura']),
        ('Sepahijala', state_ids['Tripura']),
        ('South Tripura', state_ids['Tripura']),
        ('Unakoti', state_ids['Tripura']),
        ('West Tripura', state_ids['Tripura']),

        # Uttar Pradesh
        ('Agra', state_ids['Uttar Pradesh']),
        ('Aligarh', state_ids['Uttar Pradesh']),
        ('Allahabad', state_ids['Uttar Pradesh']),
        ('Ambedkar Nagar', state_ids['Uttar Pradesh']),
        ('Ayodhya', state_ids['Uttar Pradesh']),
        ('Azamgarh', state_ids['Uttar Pradesh']),
        ('Baghpat', state_ids['Uttar Pradesh']),
        ('Bahraich', state_ids['Uttar Pradesh']),
        ('Ballia', state_ids['Uttar Pradesh']),
        ('Balrampur', state_ids['Uttar Pradesh']),
        ('Banda', state_ids['Uttar Pradesh']),
        ('Barabanki', state_ids['Uttar Pradesh']),
        ('Bareilly', state_ids['Uttar Pradesh']),
        ('Basti', state_ids['Uttar Pradesh']),
        ('Bijnor', state_ids['Uttar Pradesh']),
        ('Budaun', state_ids['Uttar Pradesh']),
        ('Bulandshahr', state_ids['Uttar Pradesh']),
        ('Chandauli', state_ids['Uttar Pradesh']),
        ('Chitrakoot', state_ids['Uttar Pradesh']),
        ('Deoria', state_ids['Uttar Pradesh']),
        ('Etah', state_ids['Uttar Pradesh']),
        ('Etawah', state_ids['Uttar Pradesh']),
        ('Farrukhabad', state_ids['Uttar Pradesh']),
        ('Fatehpur', state_ids['Uttar Pradesh']),
        ('Firozabad', state_ids['Uttar Pradesh']),
        ('Gautam Buddha Nagar', state_ids['Uttar Pradesh']),
        ('Ghaziabad', state_ids['Uttar Pradesh']),
        ('Ghazipur', state_ids['Uttar Pradesh']),
        ('Gonda', state_ids['Uttar Pradesh']),
        ('Gorakhpur', state_ids['Uttar Pradesh']),
        ('Hamirpur', state_ids['Uttar Pradesh']),
        ('Hapur', state_ids['Uttar Pradesh']),
        ('Hardoi', state_ids['Uttar Pradesh']),
        ('Hathras', state_ids['Uttar Pradesh']),
        ('Jalaun', state_ids['Uttar Pradesh']),
        ('Jaunpur', state_ids['Uttar Pradesh']),
        ('Jhansi', state_ids['Uttar Pradesh']),
        ('Kannauj', state_ids['Uttar Pradesh']),
        ('Kanpur Dehat', state_ids['Uttar Pradesh']),
        ('Kanpur Nagar', state_ids['Uttar Pradesh']),
        ('Kasganj', state_ids['Uttar Pradesh']),
        ('Kaushambi', state_ids['Uttar Pradesh']),
        ('Kushinagar', state_ids['Uttar Pradesh']),
        ('Lakhimpur Kheri', state_ids['Uttar Pradesh']),
        ('Lalitpur', state_ids['Uttar Pradesh']),
        ('Lucknow', state_ids['Uttar Pradesh']),
        ('Maharajganj', state_ids['Uttar Pradesh']),
        ('Mahoba', state_ids['Uttar Pradesh']),
        ('Mainpuri', state_ids['Uttar Pradesh']),
        ('Mathura', state_ids['Uttar Pradesh']),
        ('Mau', state_ids['Uttar Pradesh']),
        ('Meerut', state_ids['Uttar Pradesh']),
        ('Mirzapur', state_ids['Uttar Pradesh']),
        ('Moradabad', state_ids['Uttar Pradesh']),
        ('Muzaffarnagar', state_ids['Uttar Pradesh']),
        ('Pilibhit', state_ids['Uttar Pradesh']),
        ('Pratapgarh', state_ids['Uttar Pradesh']),
        ('Raebareli', state_ids['Uttar Pradesh']),
        ('Rampur', state_ids['Uttar Pradesh']),
        ('Saharanpur', state_ids['Uttar Pradesh']),
        ('Sambhal', state_ids['Uttar Pradesh']),
        ('Sant Kabir Nagar', state_ids['Uttar Pradesh']),
        ('Shahjahanpur', state_ids['Uttar Pradesh']),
        ('Shamli', state_ids['Uttar Pradesh']),
        ('Shravasti', state_ids['Uttar Pradesh']),
        ('Siddharthnagar', state_ids['Uttar Pradesh']),
        ('Sitapur', state_ids['Uttar Pradesh']),
        ('Sonbhadra', state_ids['Uttar Pradesh']),
        ('Sultanpur', state_ids['Uttar Pradesh']),
        ('Unnao', state_ids['Uttar Pradesh']),
        ('Varanasi', state_ids['Uttar Pradesh']),

        # Uttarakhand
        ('Almora', state_ids['Uttarakhand']),
        ('Bageshwar', state_ids['Uttarakhand']),
        ('Chamoli', state_ids['Uttarakhand']),
        ('Champawat', state_ids['Uttarakhand']),
        ('Dehradun', state_ids['Uttarakhand']),
        ('Haridwar', state_ids['Uttarakhand']),
        ('Nainital', state_ids['Uttarakhand']),
        ('Pauri Garhwal', state_ids['Uttarakhand']),
        ('Pithoragarh', state_ids['Uttarakhand']),
        ('Rudraprayag', state_ids['Uttarakhand']),
        ('Tehri Garhwal', state_ids['Uttarakhand']),
        ('Udham Singh Nagar', state_ids['Uttarakhand']),
        ('Uttarkashi', state_ids['Uttarakhand']),

        # West Bengal
        ('Alipurduar', state_ids['West Bengal']),
        ('Bankura', state_ids['West Bengal']),
        ('Birbhum', state_ids['West Bengal']),
        ('Cooch Behar', state_ids['West Bengal']),
        ('Dakshin Dinajpur', state_ids['West Bengal']),
        ('Darjeeling', state_ids['West Bengal']),
        ('Hooghly', state_ids['West Bengal']),
        ('Howrah', state_ids['West Bengal']),
        ('Jalpaiguri', state_ids['West Bengal']),
        ('Jhargram', state_ids['West Bengal']),
        ('Kalimpong', state_ids['West Bengal']),
        ('Kolkata', state_ids['West Bengal']),
        ('Malda', state_ids['West Bengal']),
        ('Murshidabad', state_ids['West Bengal']),
        ('Nadia', state_ids['West Bengal']),
        ('North 24 Parganas', state_ids['West Bengal']),
        ('Paschim Bardhaman', state_ids['West Bengal']),
        ('Paschim Medinipur', state_ids['West Bengal']),
        ('Purba Bardhaman', state_ids['West Bengal']),
        ('Purba Medinipur', state_ids['West Bengal']),
        ('Purulia', state_ids['West Bengal']),
        ('South 24 Parganas', state_ids['West Bengal']),
        ('Uttar Dinajpur', state_ids['West Bengal']),

        # Union Territories
        ('Nicobar', state_ids['Andaman and Nicobar Islands']),
        ('North and Middle Andaman', state_ids['Andaman and Nicobar Islands']),
        ('South Andaman', state_ids['Andaman and Nicobar Islands']),
        ('Chandigarh', state_ids['Chandigarh']),
        ('Dadra and Nagar Haveli', state_ids['Dadra and Nagar Haveli and Daman and Diu']),
        ('Daman', state_ids['Dadra and Nagar Haveli and Daman and Diu']),
        ('Diu', state_ids['Dadra and Nagar Haveli and Daman and Diu']),
        ('Central Delhi', state_ids['Delhi']),
        ('East Delhi', state_ids['Delhi']),
        ('New Delhi', state_ids['Delhi']),
        ('North Delhi', state_ids['Delhi']),
        ('North East Delhi', state_ids['Delhi']),
        ('North West Delhi', state_ids['Delhi']),
        ('Shahdara', state_ids['Delhi']),
        ('South Delhi', state_ids['Delhi']),
        ('South East Delhi', state_ids['Delhi']),
        ('South West Delhi', state_ids['Delhi']),
        ('West Delhi', state_ids['Delhi']),
        ('Jammu', state_ids['Jammu and Kashmir']),
        ('Kashmir', state_ids['Jammu and Kashmir']),
        ('Kargil', state_ids['Ladakh']),
        ('Leh', state_ids['Ladakh']),
        ('Lakshadweep', state_ids['Lakshadweep']),
        ('Karaikal', state_ids['Puducherry']),
        ('Mahe', state_ids['Puducherry']),
        ('Puducherry', state_ids['Puducherry']),
        ('Yanam', state_ids['Puducherry']),
    ]

    district_ids = {}
    for name, state_id in districts:
        cursor.execute('SELECT id FROM districts WHERE name = %s AND state_id = %s', (name, state_id))
        result = cursor.fetchone()
        if not result:
            cursor.execute('INSERT INTO districts (name, state_id) VALUES (%s, %s)', (name, state_id))
            district_ids[name] = cursor.lastrowid
        else:
            district_ids[name] = result[0]

    # Insert major cities per district
    cities = [
        ('Jaipur', district_ids['Jaipur']),
        ('Bagru', district_ids['Jaipur']),
        ('Amber', district_ids['Jaipur']),
        ('Sanganer', district_ids['Jaipur']),
        ('Jodhpur City', district_ids['Jodhpur']),
        ('Udaipur City', district_ids['Udaipur']),
        ('Ajmer City', district_ids['Ajmer']),
        ('Kota City', district_ids['Kota']),
        ('Bikaner City', district_ids['Bikaner']),
        ('Alwar City', district_ids['Alwar']),
        ('Mumbai', district_ids['Mumbai City']),
        ('Nagpur City', district_ids['Nagpur']),
        ('Pune City', district_ids['Pune']),
        ('Thane City', district_ids['Thane']),
        ('Nashik City', district_ids['Nashik']),
        ('Aurangabad City', district_ids['Aurangabad']),
        ('New Delhi', district_ids['New Delhi']),
        ('Bengaluru', district_ids['Bengaluru Urban']),
        ('Mysuru City', district_ids['Mysuru']),
        ('Hubli', district_ids['Dharwad']),
        ('Chennai City', district_ids['Chennai']),
        ('Coimbatore City', district_ids['Coimbatore']),
        ('Madurai City', district_ids['Madurai']),
        ('Ahmedabad City', district_ids['Ahmedabad']),
        ('Surat City', district_ids['Surat']),
        ('Vadodara City', district_ids['Vadodara']),
        ('Hyderabad City', district_ids['Hyderabad']),
        ('Warangal City', district_ids['Warangal']),
        ('Lucknow City', district_ids['Lucknow']),
        ('Kanpur City', district_ids['Kanpur Nagar']),
        ('Agra City', district_ids['Agra']),
        ('Varanasi City', district_ids['Varanasi']),
        ('Patna City', district_ids['Patna']),
        ('Guwahati City', district_ids['Guwahati']),
        ('Bhopal City', district_ids['Bhopal']),
        ('Indore City', district_ids['Indore']),
        ('Kolkata City', district_ids['Kolkata']),
        ('Dehradun City', district_ids['Dehradun']),
        ('Ranchi City', district_ids['Ranchi']),
        ('Chandigarh City', district_ids['Chandigarh']),
        ('Puducherry City', district_ids['Puducherry']),
        ('Jammu City', district_ids['Jammu']),
        ('Leh City', district_ids['Leh']),
    ]

    for name, district_id in cities:
        cursor.execute('SELECT id FROM cities WHERE name = %s AND district_id = %s', (name, district_id))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO cities (name, district_id) VALUES (%s, %s)', (name, district_id))

    # Insert occupations
    occupations = ['Salaried', 'Business', 'Retired', 'Student', 'Housewife', 'Other']
    for occ in occupations:
        cursor.execute('SELECT id FROM occupations WHERE name = %s', (occ,))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO occupations (name) VALUES (%s)', (occ,))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database and tables created successfully with all Indian states and districts!")
if __name__ == '__main__':
    init_db()