#!/bin/sh
echo "Starting S3 + SQS processor for send2remarkable"
python /processS3Messages.py
