import qrcode
import pandas as pd

# Load vehicle data
data = pd.read_csv(r'C:\Users\KPRCAS\Desktop\JSExample\vehicle-qrcode\data\vehicle_data.csv')

# Generate QR codes
for _, row in data.iterrows():
    content = f"""
    Vehicle Number: {row['Vehicle_Number']}
    Owner Name: {row['Owner_Name']}
    Batch: {row['Batch']}
    Department: {row['Department']}
    Licence Verified: {row['Licence_Verified']}
    Documents Verified: {row['Documents_Verified']}
    Click the link: {row['Document_Link']}

    """
    qr = qrcode.make(content)
    qr.save(f"../qrcodes/{row['Vehicle_Number']}.png")

print("QR codes generated successfully!")
