# KYC Form Application

A full-stack web application for digital KYC (Know Your Customer) onboarding built using Flask and PostgreSQL.

This application digitizes the Extended KYC registration process commonly used in banking and fintech operations. Users can securely submit KYC information, upload required documents, and manage records through a web interface.

---

## Features

- Complete 8-section Extended KYC form
- Backend + frontend validation
- Dynamic State → District → City dropdown system
- PostgreSQL database integration
- Document uploads (PDF/JPG)
- PAN, Aadhaar, Email, Mobile validation
- Mock OTP validation (4–6 digit verification)
- Edit/update functionality
- Read-only protection for sensitive fields
- Submission dashboard
- Responsive Bootstrap UI
- Render cloud deployment

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript |
| Backend | Python, Flask |
| Database | PostgreSQL |
| Hosting | Render |
| ORM/Driver | psycopg3 |

---

## Project Structure

```
kyc_project/
├── app.py
├── config.py
├── database.py
├── requirements.txt
├── Procfile
├── templates/
│   ├── kyc_form.html
│   ├── success.html
│   ├── submissions.html
│   └── update_kyc.html
├── static/
│   └── uploads/
└── README.md
```

---

## Database Tables

- states
- districts
- cities
- occupations
- accounts
- document_uploads

---

## KYC Form Sections

1. Basic Account Information
2. Contact & Verification
3. Aadhaar Details
4. Personal Information
5. Address Details
6. Employment & Financials
7. Banking & ID Details
8. Document Uploads

---

## Validation Rules Implemented

| Field | Validation |
|---|---|
| Email | Valid email format |
| Mobile | 10-digit numeric |
| OTP | 4–6 digit numeric |
| Aadhaar | 12-digit numeric |
| PAN | PAN card regex validation |
| Pincode | 6-digit numeric |
| Dropdowns | Required selection |
| Dates | Future dates blocked |
| File Uploads | PDF/JPG only |

---

## Deployment

The application is deployed on Render using:

- Flask web service
- PostgreSQL database
- Environment variables for secure DB connection

---

## Installation (Local Setup)

**Clone Repository**
```bash
git clone https://github.com/ad-aditisingh/kyc-project.git
cd kyc-project
```

**Create Virtual Environment**
```bash
python -m venv venv
```

**Activate Environment**

Windows:
```bash
venv\Scripts\activate
```

**Install Dependencies**
```bash
pip install -r requirements.txt
```

**Initialize Database**
```bash
python database.py
```

**Run Application**
```bash
python app.py
```

---

## Notes

- OTP verification is mock/demo validation only.
- Uploaded files are stored locally in `static/uploads/`.
- Render free filesystem storage is temporary and resets on redeploy.

---

## Author

Aditi Singh