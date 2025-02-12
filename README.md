# PDF-Watermark-Automation

## Overview

This Python script automates the process of downloading PDF files from Google Drive, adding a watermark to each page, and re-uploading the processed files to a designated folder in Google Drive. The script also updates a Google Sheet to track the processing status of each file.

## Features

- Reads data from a Google Sheet containing student details (MMID, Name, Status)
- Downloads PDF files from a specified Google Drive folder
- Adds a **semi-transparent watermark** with the MMID to each page
- Uploads the processed PDF back to another Google Drive folder
- Updates the Google Sheet to indicate processing status

## Folder & File Structure

```
WaterSheet_GCP/
│-- script.py                    # Main script
│-- credentials.json             # Google Service Account credentials
│-- README.md                    # Project documentation
```

## Prerequisites

Ensure you have the following before running the script:

- Python 3.7+
- A Google Cloud project with API access to Google Drive and Google Sheets
- A Google Service Account with the correct permissions
- Installed Python dependencies

## Installation

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/PDF-Watermark-Automation.git
cd PDF-Watermark-Automation
```

### 2. Install Dependencies

```sh
pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 googleapiclient pandas pymupdf
```

### 3. Set Up Google Cloud Credentials

- Obtain a **Service Account JSON key** from Google Cloud.
- Place it in the project directory and update the script with its path:

```python
SERVICE_ACCOUNT_FILE = "credentials.json"
```

### 4. Configure Google Drive and Sheets IDs

Update the following variables in `script.py` with your own Google Drive folder IDs and Google Sheet ID:

```python
FOLDER_ID_SOURCE = 'your-source-folder-id'
FOLDER_ID_DESTINATION = 'your-destination-folder-id'
SPREADSHEET_ID = 'your-google-sheet-id'
```

## Usage

Run the script using:

```sh
python script.py
```

The script will:

1. Read student details from the Google Sheet.
2. Download PDFs from the source Google Drive folder.
3. Apply a **semi-transparent watermark** with MMID.
4. Upload the processed PDFs to the destination folder.
5. Update the Google Sheet with "Done" or "Error" status.

## Troubleshooting

### Common Errors:

- **Invalid Credentials**: Ensure the Service Account JSON file is correct and has the right permissions.
- **Empty PDFs**: If PDFs appear blank after processing, verify the watermark placement and transparency settings.
- **Sheet Not Updating**: Check if the Service Account has edit access to Google Sheets.


## Contributing

Feel free to submit pull requests or open issues to improve the script!
