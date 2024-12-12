import qrcode
import pandas as pd

# Load vehicle data
data = pd.read_csv('../data/vehicle_data.csv')

# Generate QR codes
for _, row in data.iterrows():
    content = f"""
    Vehicle Number: {row['Vehicle_Number']}
    Owner Name: {row['Owner_Name']}
    Model: {row['Vehicle_Model']}
    Registration Year: {row['Registration_Year']}
    """
    qr = qrcode.make(content)
    qr.save(f"../qrcodes/{row['Vehicle_Number']}.png")

print("QR codes generated successfully!")
