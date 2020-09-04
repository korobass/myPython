# Automating AWS with Python

Repository for the A Cloud Guru course *Automating AWS with Python*

## 01-webotron

Webotron is a script that will sync a local directory to an s3 bucket, and optionally configure Route 53 and cloudfront as well.

## Features

Webotron currently has the following features:

- List buckets
- List contents of a bucket
- Create and Setup bucket
- sync directory to bucket:
    - including multipart upload,
    - skipping files that are already in the bucket
    - -d or --delete flag to optionally delete files from bucket, that are no longer available in local
- delete bucket
- set aws profile with -p <"profileName"> or --profile=<"profileName">
- set aws region with -r <"regionName"> or --region=<"regionName">
- handling exception for non existing bucket
- bucket name validation