import os
import fitz  # PyMuPDF for PDF processing
import pandas as pd
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.oauth2 import service_account

print(" Script started...")

# Google Service Account Setup
SERVICE_ACCOUNT_FILE = "path/to/your/service_account.json"  # Update with actual path
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']

# Authenticate and initialize the Google API clients
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)
sheets_service = build('sheets', 'v4', credentials=credentials)

# Google Drive Folder IDs
FOLDER_ID_SOURCE = 'your-source-folder-id'  # Replace with actual source folder ID
FOLDER_ID_DESTINATION = 'your-destination-folder-id'  # Replace with actual destination folder ID

# Google Sheets ID
SPREADSHEET_ID = 'your-google-sheet-id'  # Replace with actual spreadsheet ID
SHEET_NAME = 'Sheet2'

# Read Data from Google Sheets
def read_google_sheet():
    sheet = sheets_service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"{SHEET_NAME}!A:C").execute()
    values = result.get('values', [])
    
    if not values:
        print(" No data found in the Google Sheet.")
        return None

    df = pd.DataFrame(values[1:], columns=values[0])  # Convert data to DataFrame
    return df

# Download Source PDF from Google Drive
def download_pdf(file_id):
    request = drive_service.files().get_media(fileId=file_id)
    pdf_data = io.BytesIO()
    downloader = MediaIoBaseDownload(pdf_data, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    
    pdf_data.seek(0)
    if pdf_data.getbuffer().nbytes == 0:
        print(" Error: Downloaded PDF is empty!")
        return None

    return pdf_data

# Add Watermark to PDF
def add_watermark(input_pdf_data, watermark_text):
    try:
        doc = fitz.open("pdf", input_pdf_data.read())  # Load the PDF document
    except Exception as e:
        print(f" Error opening PDF: {e}")
        return None

    for page in doc:
        rect = page.rect  # Get page dimensions
        for x in range(50, int(rect.width), 100):
            for y in range(50, int(rect.height), 100):
                page.insert_text(
                    (x, y),  # Position of watermark
                    watermark_text,
                    fontsize=10,
                    rotate=0,
                    color=(0.7, 0.7, 0.7),  # Light gray watermark
                    overlay=False  # Place watermark below content
                )

    output_pdf = io.BytesIO()
    doc.save(output_pdf)  # Save the modified PDF
    doc.close()
    output_pdf.seek(0)
    return output_pdf

# Upload PDF to Google Drive
def upload_to_drive(pdf_data, file_name, folder_id):
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(pdf_data, mimetype='application/pdf', resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

# Update Google Sheets Status
def update_sheet_status(row_index, status):
    range_to_update = f"{SHEET_NAME}!C{row_index + 2}"
    body = {"values": [[status]]}
    sheets_service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_to_update,
        valueInputOption="RAW",
        body=body
    ).execute()
    print(f" Updated Google Sheet: C{row_index + 2} -> {status}")

# Main PDF Processing Function
def process_pdfs():
    df = read_google_sheet()
    if df is None:
        return

    # Fetch PDF files from the source folder in Google Drive
    response = drive_service.files().list(q=f"'{FOLDER_ID_SOURCE}' in parents and mimeType='application/pdf'",
                                          fields="files(id, name)").execute()
    files = response.get('files', [])
    if not files:
        print(" No PDF found in Source folder.")
        return

    sample_pdf_id = files[0]['id']  # Get the first available PDF
    sample_pdf_data = download_pdf(sample_pdf_id)
    if not sample_pdf_data:
        print(" Error: Source PDF download failed.")
        return

    for index, row in df.iterrows():
        name = row.get("NAME", "").strip()
        mmid = row.get("MMID", "").strip()
        status = row.get("Status", "").strip()
        
        # Process only if student is marked as 'Enroll'
        if not name or not mmid or status.lower() != "enroll":
            continue
        
        try:
            new_pdf_name = f"{name}-{mmid}.pdf"  # Format output file name
            sample_pdf_data.seek(0)  # Reset pointer before reading
            watermarked_pdf = add_watermark(sample_pdf_data, mmid)
            if not watermarked_pdf:
                print(f" Error: Watermarking failed for {new_pdf_name}")
                update_sheet_status(index, "Error")
                continue

            # Upload processed PDF to destination folder
            upload_to_drive(watermarked_pdf, new_pdf_name, FOLDER_ID_DESTINATION)
            update_sheet_status(index, "Done")

        except Exception as e:
            print(f" Error processing {name}: {e}")
            update_sheet_status(index, "Error")

    print(" Processing completed!")

# Run Script
if __name__ == "__main__":
    process_pdfs()
