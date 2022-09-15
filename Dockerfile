FROM golang:alpine AS rmapi-builder
RUN apk add --no-cache git
RUN git clone https://github.com/juruen/rmapi && \
    cd rmapi && \
    go install

FROM python:alpine
RUN pip install imbox
COPY . .
COPY --from=rmapi-builder /go/bin/rmapi /usr/local/bin/rmapi
RUN mkdir files
ENTRYPOINT ["entry.sh"]