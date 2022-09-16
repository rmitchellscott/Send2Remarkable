# Send2Remarkable
Send2Remarkable scans an email inbox for unread emails containing PDFs and ePubs and sends them to ReMarkable Cloud or [rmfakecloud](https://github.com/ddvk/rmfakecloud). Can be paired nicely with [Calibre-Web](https://github.com/janeczku/calibre-web) for sending eBooks from your Calibre library directly to your ReMarkable tablet. Send2Remarkable uses [rmapi](https://github.com/juruen/rmapi) under the hood to send the files.

## Instructions
1. Configure your email account to allow for basic authentication for IMAP. This may require an App Password if you have MFA enabled. Tested successfully with Gmail.
1. Get your device and user token file (rmapi.conf) from the Remarkable cloud by running the following command and entering the one-time code: `docker run -it ghcr.io/rmitchellscott/send2remarkable init`
1. Save the output as rmapi.conf, and this will get mounted into the container.
1. By default, cron runs every minute to check for new emails. Adjust this to your liking in `crontab.txt`.

# Examples
The following examples are provided as a way to get started. Some adjustments may be required before production use, particularly regarding secret management.
## Docker
```shell
docker run -d \
-v ~/rmapi.conf:/root/.config/rmapi/rmapi.conf \
-e IMAP_HOST=imap.gmail.com \
-e IMAP_USER=AzureDiamond@example.com \
-e IMAP_PASSWORD=hunter2 \
-e SUBJECT="Sent to E-Reader" \
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
      IMAP_HOST: imap.gmail.com
      IMAP_USER: AzureDiamond@example.com
      IMAP_PASSWORD: hunter2
      SUBJECT: Sent to E-Reader
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
        - name: IMAP_HOST
          value: imap.gmail.com
        - name: IMAP_USER
          valueFrom:
            secretKeyRef:
              name: imap
              key: user
        - name: IMAP_PASSWORD
          valueFrom:
            secretKeyRef:
              name: imap
              key: password
        - name: SENT_TO
          valueFrom:
            secretKeyRef:
              name: imap
              key: sent_to
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
| IMAP_HOST                | yes       | IMAP hostname | imap.gmail.com    |
| IMAP_USER                | yes       | IMAP username | AzureDiamond@example.com |
| IMAP_PASSWORD            | yes       | IMAP password | hunter2 |
| SUBJECT                  | no*       | Email subject to search for | "Send to E-Reader"
| SENT_TO                  | no*       | Email To: address to search for | "remarkable@example.com"
| RMAPI_HOST               | no       | Override Remarkable cloud URL | https://remarkable.example.com |

*one of SUBJECT or SENT_TO __is required__. Both can be used if desired.
