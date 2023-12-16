from googleapiclient.discovery import build


def download_g_drive_file(creds):
    # Replace with your Google Drive API credentials
    credentials = creds
    drive_service = build('drive', 'v3', credentials=credentials)

    # Get the file ID from the Google Drive URL or file name
    file_id = "1dinlLxwnpok4SbYoDN_l2qYvb6aWegVl"

    # Download the PDF
    request = drive_service.files().get_media(fileId=file_id).execute()
    with open("downloaded_pdf.pdf", "wb") as f:
        f.write(request.content)

    print("PDF downloaded successfully!")
