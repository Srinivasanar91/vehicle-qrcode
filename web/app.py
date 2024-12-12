from flask import Flask, render_template, send_file
import pandas as pd

app = Flask(__name__)

# Load vehicle data
data = pd.read_csv(r'C:\Users\KPRCAS\Desktop\JSExample\vehicle-qrcode\data\vehicle_data.csv')

@app.route('/')
def index():
    return render_template('index.html', vehicles=data.to_dict(orient='records'))

@app.route('/qr/<vehicle_number>')
def get_qr(vehicle_number):
    filepath = f"../qrcodes/{vehicle_number}.png"
    return send_file(filepath, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
