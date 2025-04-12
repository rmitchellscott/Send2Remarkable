FROM --platform=$BUILDPLATFORM golang:alpine AS rmapi-builder
WORKDIR /app
RUN apk add --no-cache git
ARG TARGETPLATFORM
RUN case "$TARGETPLATFORM" in \
        'linux/arm/v6') export GOARCH=arm GOARM=6 ;; \
        'linux/arm/v7') export GOARCH=arm GOARM=7 ;; \
        'linux/arm64') export GOARCH=arm64 ;; \
        *) export GOARCH=amd64 ;; \
    esac && \
    git clone https://github.com/ddvk/rmapi && \
    cd rmapi && \
    go build -ldflags='-w -s' .

FROM python:alpine
# Install boto3 for AWS services instead of imbox
RUN pip install boto3
COPY --from=rmapi-builder /app/rmapi/rmapi /usr/local/bin/rmapi
COPY . .
RUN chmod +x entry.sh && chmod +x init.sh && mv init.sh /usr/local/bin/init
RUN mkdir -p files
CMD ["/entry.sh"]
