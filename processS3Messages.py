import os
import boto3
import json
import time
import traceback
import subprocess
import logging
from botocore.exceptions import ClientError
from email import message_from_bytes, policy
from email.parser import BytesParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
POLL_INTERVAL_SECONDS = int(os.environ.get('POLL_INTERVAL_SECONDS', '60'))
DOWNLOAD_FOLDER = "/files"

# Ensure download folder exists
if not os.path.isdir(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Initialize AWS clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
sqs_client = boto3.client('sqs', region_name=AWS_REGION)

def process_email_from_s3(s3_bucket, s3_key):
    """
    Process an email stored in S3 by SES
    """
    try:
        # Get the email object from S3
        logger.info(f"Retrieving email from S3: {s3_bucket}/{s3_key}")
        response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
        email_content = response['Body'].read()
        
        # Parse the email
        parser = BytesParser(policy=policy.default)
        message = parser.parsebytes(email_content)
        
        # Process attachments
        attachments_found = False
        for part in message.iter_attachments():
            filename = part.get_filename()
            
            if filename:
                # Check if file is PDF or EPUB
                if filename.lower().endswith(('.pdf', '.epub')):
                    attachments_found = True
                    # Save attachment to file
                    download_path = f"{DOWNLOAD_FOLDER}/{filename}"
                    logger.info(f"Saving attachment: {download_path}")
                    
                    with open(download_path, "wb") as fp:
                        fp.write(part.get_payload(decode=True))
        
        if attachments_found:
            # Call the script to process and upload files
            logger.info("Running putFiles.sh to upload documents")
            subprocess.call(['sh', '/putFiles.sh'])
        else:
            logger.info("No PDF or EPUB attachments found in email")
            
        return True
    except Exception as e:
        logger.error(f"Error processing email: {str(e)}")
        traceback.print_exc()
        return False

def poll_sqs_queue():
    """
    Poll SQS queue for S3 event notifications
    """
    try:
        # Receive message from SQS queue
        response = sqs_client.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20  # Long polling
        )
        
        # Check if there are messages
        if 'Messages' in response:
            for message in response['Messages']:
                receipt_handle = message['ReceiptHandle']
                
                try:
                    # Parse the message body
                    body = json.loads(message['Body'])
                    
                    # The message might be wrapped in an SNS notification
                    if 'Message' in body:
                        body = json.loads(body['Message'])
                    
                    # Process S3 event
                    if 'Records' in body:
                        for record in body['Records']:
                            if record.get('eventSource') == 'aws:s3' and record.get('eventName').startswith('ObjectCreated'):
                                s3_bucket = record['s3']['bucket']['name']
                                s3_key = record['s3']['object']['key']
                                
                                logger.info(f"Processing new S3 object: {s3_bucket}/{s3_key}")
                                process_success = process_email_from_s3(s3_bucket, s3_key)
                                
                                if process_success:
                                    # Delete message from queue after successful processing
                                    sqs_client.delete_message(
                                        QueueUrl=SQS_QUEUE_URL,
                                        ReceiptHandle=receipt_handle
                                    )
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    traceback.print_exc()
            
            return len(response.get('Messages', []))
        return 0
    except Exception as e:
        logger.error(f"Error polling SQS: {str(e)}")
        traceback.print_exc()
        return 0

def main():
    """
    Main function to continuously poll SQS for new messages
    """
    logger.info("Starting SES + S3 + SQS processor for send2remarkable")
    logger.info(f"Using SQS Queue: {SQS_QUEUE_URL}")
    logger.info(f"Using S3 Bucket: {S3_BUCKET_NAME}")
    
    while True:
        try:
            messages_processed = poll_sqs_queue()
            logger.info(f"Processed {messages_processed} messages")
            
            # Sleep if no messages were processed
            if messages_processed == 0:
                time.sleep(POLL_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logger.info("Shutting down")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            traceback.print_exc()
            time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
