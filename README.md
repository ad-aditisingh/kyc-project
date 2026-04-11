# KYC Form

A full-stack web application for digital KYC (Know Your Customer) onboarding.
This application digitizes the Extended KYC registration process used in fintech and banking operations. It allows customers to submit their KYC details online with document uploads, OTP verification, and admin review capabilities.

## Features

- 8-section KYC form covering all regulatory requirements
- Mock OTP verification for Email, Mobile, and Aadhaar
- Cascading dropdowns for State → District → City (all Indian states)
- Document uploads with 2MB size validation (Aadhaar, PAN, Signature, etc.)
- Form validation — required fields, PAN format, Aadhaar/mobile patterns
- Submissions dashboard to view all KYC records
- Update functionality for editable fields
- Read-only protection for sensitive fields (Aadhaar, PAN, DOB)
- Clean corporate UI design

## Tech Stack
 Frontend - HTML, CSS, Bootstrap 5, JavaScript 
 Backend - Python, Flask 
 Database - PostgreSQL 
 Hosting - Render 

## Project Structure
kyc_project/

│

├── app.py              # Flask routes and backend logic

├── config.py           # Database configuration

├── database.py         # Table creation and seed data

├── requirements.txt    # Python dependencies

├── Procfile            # Render deployment config

│

├── templates/

│   ├── kyc_form.html       # Main KYC form

│   ├── success.html        # Submission confirmation

│   ├── submissions.html    # view of all records

│   └── update_kyc.html     # Edit existing KYC

│

└── static/

└── uploads/        # Uploaded documents
## Database Schema

- `states` — All 36 Indian states and union territories
- `districts` — Districts linked to states
- `cities` — Cities linked to districts
- `occupations` — Occupation types
- `accounts` — Main KYC records (39 fields)
- `document_uploads` — Uploaded file references per account

## Form Sections

1. Basic Account Information
2. Contact & Verification (with OTP 123456)
3. Aadhaar Details (with OTP 123456)
4. Personal Information
5. Address Details (with location cascade)
6. Employment & Financials
7. Banking & ID Details
8. Document Uploads

