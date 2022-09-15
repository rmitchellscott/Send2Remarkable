import os
import sys
from imbox import Imbox
import traceback
import subprocess

host = os.environ.get('IMAP_HOST')
username = os.environ.get('IMAP_USER')
password = os.environ.get('IMAP_PASSWORD')
sent_to = os.environ.get('SENT_TO')
subject = os.environ.get('SUBJECT')
download_folder = "/files"

if not os.path.isdir(download_folder):
    os.makedirs(download_folder, exist_ok=True)
mail = Imbox(host, username=username, password=password, ssl=True, ssl_context=None, starttls=False)
if subject is None and sent_to is None:
    print("SUBJECT or SENT_TO envs required! Exiting.")
    exit()
elif subject is None:
    messages = mail.messages(sent_to=sent_to,unread=True)
elif sent_to is None:
    messages = mail.messages(subject=subject,unread=True)
else:
    messages = mail.messages(sent_to=sent_to,subject=subject,unread=True)

for (uid, message) in messages:
    for idx, attachment in enumerate(message.attachments):
        try:
            att_fn = attachment.get('filename')
            download_path = f"{download_folder}/{att_fn}"
            print(download_path)
            with open(download_path, "wb") as fp:
                fp.write(attachment.get('content').read())
        except:
            print(traceback.print_exc())
        subprocess.call(['sh','/putFiles.sh'])
        mail.mark_seen(uid)
mail.logout()