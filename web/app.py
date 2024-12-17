from flask import Flask, request, render_template, send_file, redirect, session, url_for, flash
from pymongo import MongoClient
import pandas as pd
import qrcode
import os
import zipfile
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')  # Replace with your connection string
db = client['vehicle_qr']  # Database name
admin_credentials = db['admin_credentials']  # Collection name

# Add admin credentials if not already present
if not admin_credentials.find_one({"username": "admin"}):
    admin_credentials.insert_one({
        "username": "admin",
        "password": generate_password_hash("admin123")  # Replace with a secure password
    })

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch admin details from MongoDB
        admin = admin_credentials.find_one({"username": username})
        if admin and check_password_hash(admin['password'], password):
            session['admin_logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@admin_required
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Folder to store generated QR codes
qr_code_folder = "qr_codes"
os.makedirs(qr_code_folder, exist_ok=True)

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@admin_required
def index():
    # Display all vehicles initially
    vehicles = pd.read_csv(r'C:\Users\KPRCAS\Desktop\JSExample\vehicle-qrcode\data\vehicle_data.csv').to_dict(orient='records')
    return render_template('index.html', vehicles=vehicles)

@app.route('/search', methods=['GET'])
@admin_required
def search():
    query = request.args.get('q', '').strip()  # Get the search query
    data = pd.read_csv(r'C:\Users\KPRCAS\Desktop\JSExample\vehicle-qrcode\data\vehicle_data.csv')
    if query:
        # Filter data based on vehicle number (case-insensitive)
        filtered_data = data[data['Vehicle_Number'].str.contains(query, case=False, na=False)]
    else:
        filtered_data = data  # No query, show all data
    return render_template('index.html', vehicles=filtered_data.to_dict(orient='records'))

@app.route('/generate_qr/<vehicle_number>')
@admin_required
def generate_qr(vehicle_number):
    # Find the vehicle in the data
    data = pd.read_csv(r'C:\Users\KPRCAS\Desktop\JSExample\vehicle-qrcode\data\vehicle_data.csv')
    vehicle = data[data['Vehicle_Number'] == vehicle_number].to_dict(orient='records')
    if not vehicle:
        return "Vehicle not found", 404

    vehicle = vehicle[0]  # Get the first matching record
    qr_data = f"Vehicle Number: {vehicle['Vehicle_Number']}\nStudent Name: {vehicle['Student_Name']}\nRoll Number: {vehicle['Roll_Number']}\nBatch: {vehicle['Batch']}\nOwner Name: {vehicle['Owner_Name']}\nLicence Verified: {vehicle['Licence_Verified']}\nRC Verified: {vehicle['RC_Verified']}\nInsurance_Verified: {vehicle['Insurance_Verified']}"
    qr_path = os.path.join(qr_code_folder, f"{vehicle_number}.png")

    # Generate QR code if it doesn't exist
    if not os.path.exists(qr_path):
        qr = qrcode.make(qr_data)
        qr.save(qr_path)

    return send_file(qr_path, mimetype='image/png')
@app.route('/upload', methods=['GET', 'POST'])
@admin_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(qr_code_folder, filename)
            file.save(file_path)
            flash(f"File uploaded successfully: {filename}")

            # Process the CSV to generate QR codes
            try:
                csv_data = pd.read_csv(file_path)
                if csv_data.empty:
                    flash("The uploaded file is empty.")
                    return redirect(request.url)

                # Create a ZIP file for QR codes
                zip_path = os.path.join(qr_code_folder, "qr_codes.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for _, row in csv_data.iterrows():
                        try:
                            vehicle_number = row['Vehicle_Number']
                            qr_data = f"""Vehicle Number: {vehicle_number}
Owner: {row['Owner_Name']}
Batch: {row['Batch']}
Department: {row['Department']}
License Verified: {row['Licence_Verified']}
Documents Verified: {row['Documents_Verified']}"""
                            qr_path = os.path.join(qr_code_folder, f"{vehicle_number}.png")
                            qr = qrcode.make(qr_data)
                            qr.save(qr_path)
                            zipf.write(qr_path, os.path.basename(qr_path))
                        except KeyError as e:
                            flash(f"Missing column in CSV: {e}")
                            return redirect(request.url)
                        except Exception as e:
                            flash(f"Error generating QR for {vehicle_number}: {e}")
                            continue
                return send_file(zip_path, mimetype='application/zip', as_attachment=True, download_name="qr_codes.zip")
            except Exception as e:
                flash(f"Error processing file: {e}")
                return redirect(request.url)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)