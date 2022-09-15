# SendToRemarkable
SendToRemarkable scans an email inbox for unread emails containing PDFs and ePubs and sends them to ReMarkable Cloud or [rmfakecloud](https://github.com/ddvk/rmfakecloud). Can be paired nicely with [Calibre-Web](https://github.com/janeczku/calibre-web) for sending eBooks from your Calibre library directly to your ReMarkable tablet. SendToRemarkable uses [rmapi](https://github.com/juruen/rmapi) under the hood to send the files.

## Instructions
1. Configure your email account to allow for basic authentication for IMAP. This may require an App Password if you have MFA enabled. Tested successfully with Gmail.
2. Run the `rmapi` command from within this container, and enter the ReMarkable one-time code when prompted. Exit `rmapi`, then record the contents of `/root/.config/rmapi/rmapi.conf`. This will be mounted inside the container later. Alternatively, you could use a volume mount for this location if you don't mind the app becoming stateful.
3. By default, cron runs every minute to check for new emails. Adjust this to your liking.


## Example Kubernetes deployment
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
      - image: harbor.mitchellscott.us/library/send2remarkable:33a62f03
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

## Environment Variables

| Variable                 | Required? | Details | Example |
|--------------------------|-----------|---------|---------|
| IMAP_HOST                | yes       | IMAP hostname | imap.gmail.com    |
| IMAP_USER                | yes       | IMAP username | AzureDiamond@example.com |
| IMAP_PASSWORD            | yes       | IMAP password | hunter2 |
| SUBJECT                  | no*       | Email subject to search for | "Send to E-Reader"
| SENT_TO                  | no*       | Email To: address to search for | "remarkable@example.com"
| RMAPI_HOST               | no       | Override Remarkable cloud URL | https://remarkable.example.com |

*one of SUBJECT or SENT_TO __is required__. Both can be used if desired.