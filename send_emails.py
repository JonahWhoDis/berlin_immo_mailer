import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import shutil
import logging

# Configuration
sender_email = "jonahgrosshanten@gmail.com" #without @gmail.com 
password = "ampi oewl bepk znuz" # See Readme how to get it
email_subject = "Wohnungsbewerbung – 1300 € Warmmiete, zuverlässiger Mieter (Jonah Großhanten)"
directory_path = "output"
sent_directory_path = os.path.join(directory_path, "sent")
amount_to_send = 25
wait_min = 60
wait_max = 180

# Ensure the "sent" directory exists
if not os.path.exists(sent_directory_path):
    os.makedirs(sent_directory_path)

# Setup logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("email_sender.log"),
                              logging.StreamHandler()])

def waiting():
    wait_time = random.randint(wait_min, wait_max)
    logging.info(f"Waiting for {wait_time / 60:.2f} minutes before processing the next email.")
    time.sleep(wait_time)
    return wait_time

def send_email(subject, body, sender, recipient, password):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    # Attach the HTML content
    html_part = MIMEText(body, 'html')
    msg.attach(html_part)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipient, msg.as_string())
            logging.info(f"Email sent to {recipient}")
    except smtplib.SMTPException as e:
        logging.error(f"Failed to send email to {recipient}: {e}")

def main():
    count = 0
    for filename in os.listdir(directory_path):
        if filename.endswith(".html"):
            recipient_email = filename.split('.html')[0]
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            send_email(email_subject, html_content, sender_email, recipient_email, password)
            
            count += 1
            logging.info(f"Email count: {count}")
            # Move the sent email file to the "sent" directory
            shutil.move(file_path, os.path.join(sent_directory_path, filename))
            logging.info(f"Moved {filename} to {sent_directory_path}")
            if count >= amount_to_send:
                logging.info(f"Reached the limit of {amount_to_send} emails. Stopping the application.")
                break


            # Wait for a random time before sending the next email
            wait_time = waiting()
            logging.info(f"Waited for {wait_time / 60:.2f} minutes.")

if __name__ == "__main__":
    main()
