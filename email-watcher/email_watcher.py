import email
import imaplib
import requests
import time
import os

# --- CONFIGURATION ---
GMAIL_USER = "usquarevsquare@gmail.com"
GMAIL_APP_PASSWORD = "ycco qlps mrbh wpby" # YOU MUST CHANGE THIS
IMAP_SERVER = "imap.gmail.com"
UPLOAD_ENDPOINT = "http://module-a:8000/upload/"

def check_for_new_mail():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        mail.select("inbox")
        print("Connected. Searching for unread mail...", flush=True)

        status, messages = mail.search(None, "UNSEEN")
        if status != "OK" or not messages[0]:
            print("No new messages found.", flush=True)
            mail.close()
            mail.logout()
            return

        email_ids = messages[0].split()
        print(f"Found {len(email_ids)} new email(s).", flush=True)
        for email_id in email_ids:
            _, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    for part in msg.walk():
                        if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                            continue
                        filename = part.get_filename()
                        if filename:
                            print(f"  Found attachment: {filename}", flush=True)
                            files = {'file': (filename, part.get_payload(decode=True), part.get_content_type())}
                            data = {'source': 'Email'}
                            try:
                                print(f"  Uploading {filename}...", flush=True)
                                response = requests.post(UPLOAD_ENDPOINT, files=files, data=data)
                                response.raise_for_status()
                                print(f"  Upload successful!", flush=True)
                                mail.store(email_id, '+FLAGS', '\\Seen')
                            except requests.exceptions.RequestException as e:
                                print(f"  ERROR: Failed to upload file. {e}", flush=True)
        mail.close()
        mail.logout()
    except Exception as e:
        print(f"An error occurred: {e}", flush=True)

if __name__ == "__main__":
    print("Starting email watcher service...", flush=True)
    if GMAIL_APP_PASSWORD == "PASTE_YOUR_16_DIGIT_APP_PASSWORD_HERE":
        print("ERROR: Please update the GMAIL_APP_PASSWORD in the script.", flush=True)
        exit(1)
    while True:
        check_for_new_mail()
        print("Waiting for 60 seconds...", flush=True)
        time.sleep(60)

