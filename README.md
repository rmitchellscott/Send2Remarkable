# Send2Remarkable
Send2Remarkable monitors an AWS SQS queue for emails placed in an S3 bucket containing PDFs and ePubs and sends them to ReMarkable Cloud or [rmfakecloud](https://github.com/ddvk/rmfakecloud). Can be paired nicely with [Calibre-Web](https://github.com/janeczku/calibre-web) for sending eBooks from your Calibre library directly to your ReMarkable tablet. Send2Remarkable uses [rmapi](https://github.com/ddvk/rmapi) under the hood to send the files.

For the IMAP version that is no longer maintained, see the imap branch.

## Instructions
1. Configure AWS S3, SES, and SQS to recieve emails, place them in a bucket, and queue.
1. Get your device and user token file (rmapi.conf) from the Remarkable cloud by running the following command and entering the one-time code: `docker run -it ghcr.io/rmitchellscott/send2remarkable init`
1. Save the output as rmapi.conf, and this will get mounted into the container.
1. By default, SQS is polled every minute. This can be adjusted via environment variable.

# Examples
The following examples are provided as a way to get started. Some adjustments may be required before production use, particularly regarding secret management.
## Docker
```shell
docker run -d \
-v ~/rmapi.conf:/root/.config/rmapi/rmapi.conf \
-e AWS_REGION=us-east-2 \
-e AWS_ACCESS_KEY_ID=your_access_key\
-e AWS_SECRET_ACCESS_KEY=your_secret_key \
-e SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/YourQueueName \
-e S3_BUCKET_NAME=your-s3-bucket-name\
ghcr.io/rmitchellscott/send2remarkable
```

## Docker Compse

```yaml
verion: 2.4

services:
  send2remarkable:
    image: ghcr.io/rmitchellscott/send2remarkable
    volumes:
      - type: bind
        source: ~/rmapi.conf
        target: /root/.config/rmapi/rmapi.conf
    environment:
      AWS_REGION: us-east-2
      AWS_ACCESS_KEY_ID: your_access_key
      AWS_SECRET_ACCESS_KEY: your_secret_key
      SQS_QUEUE_URL: https://sqs.us-east-1.amazonaws.com/123456789012/YourQueueName
      S3_BUCKET_NAME: your-s3-bucket-name
    restart: unless-stopped
```

## Kubernetes deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: send2remarkable
spec:
  replicas: 1
  revisionHistoryLimit: 1
  selector:
    matchLabels:
      app: send2remarkable
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: send2remarkable
    spec:
      containers:
      - image: ghcr.io/rmitchellscott/send2remarkable:latest
        name: send2remarkable
        env:
        - name: AWS_REGION
          value: us-east-2
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: aws
              key: key-id
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: aws
              key: secret
        - name: SQS_QUEUE_URL
          value: https://sqs.us-east-1.amazonaws.com/123456789012/YourQueueName
        - name: S3_BUCKET_NAME
          value: your-s3-bucket-name
        volumeMounts:
        - name: rmapi-config
          mountPath: /root/.config/rmapi
          readOnly: true
      volumes:
      - name: rmapi-config
        secret:
          secretName: rmapi-secret
```

# Environment Variables

| Variable                 | Required? | Details | Example |
|--------------------------|-----------|---------|---------|
| AWS_REGION               | yes | AWS Region | us-east-2 |
| AWS_ACCESS_KEY_ID | yes | AWS IAM key ID | AKIAYOURKEY |
| AWS_SECRET_ACCESS_KEY | yes | AWS IAM secret | your_secret_key |
| SQS_QUEUE_URL | yes | AWS SQS URL | https://sqs.us-east-1.amazonaws.com/123456789012/YourQueueName |
| S3_BUCKET_NAME | yes | AWS S3 bucket name | your-s3-bucket-name |
| POLL_INTERVAL_SECONDS | no | Interval in seconds to poll SQS | 60 |
| RMAPI_HOST               | no       | Override Remarkable cloud URL | https://remarkable.example.com |
