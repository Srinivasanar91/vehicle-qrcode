import os
import pandas as pd
import qrcode

# Read vehicle data
data = pd.read_csv(r'C:\Users\KPRCAS\Desktop\JSExample\vehicle-qrcode\data\vehicle_data.csv')

# Generate QR codes
for _, row in data.iterrows():
    content = f"""
    Vehicle Number: {row['Vehicle_Number']}
    Owner Name: {row['Owner_Name']}
    Model: {row['Vehicle_Model']}
    Registration Year: {row['Registration_Year']}
    """
    vehicle_number = row['Vehicle_Number']
    filepath = rf"C:\Users\KPRCAS\Desktop\JSExample\vehicle-qrcode\qrcodes\{vehicle_number}.png"
    qr = qrcode.make(content)
    qr.save(filepath)

print("QR codes generated successfully!")
