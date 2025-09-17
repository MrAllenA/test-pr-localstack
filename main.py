from fastapi import FastAPI, UploadFile
import boto3
import os


app = FastAPI()

# Localstack endpoint
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

# Mocked boto3 clients pointing to Localstack
ssm = boto3.client(
    "ssm",
    endpoint_url=AWS_ENDPOINT_URL,
    region_name=AWS_REGION,
    aws_access_key_id="fake",
    aws_secret_access_key="fake",
)

s3 = boto3.client(
    "s3",
    endpoint_url=AWS_ENDPOINT_URL,
    region_name=AWS_REGION,
    aws_access_key_id="fake",
    aws_secret_access_key="fake",
)

# Ensure bucket exists
bucket_name = ssm.get_parameter(Name="/test/S3_BUCKET_NAME")["Parameter"]["Value"]
try:
    s3.head_bucket(Bucket=bucket_name)
except s3.exceptions.ClientError:
    s3.create_bucket(Bucket=bucket_name)

@app.get("/")
def root():
    return {"message": "Hello World22"}
@app.get("/config")
def get_config():
    """Fetch DB connection string from mocked SSM"""
    param = ssm.get_parameter(Name="/test/DB_CONN_URL")
    return {"DB_CONN_URL": param["Parameter"]["Value"]}


@app.get("/secrets")
def get_secrets():
    """Fetch multiple mocked SSM parameters"""
    keys = ["/test/JWT_SECRET", "/test/S3_BUCKET_NAME"]
    result = {}
    for key in keys:
        param = ssm.get_parameter(Name=key)
        result[key] = param["Parameter"]["Value"]
    return result


@app.get("/buckets")
def list_buckets():
    """List all buckets in mocked S3"""
    buckets = s3.list_buckets()
    return {"buckets": [b["Name"] for b in buckets.get("Buckets", [])]}


@app.post("/upload")
def upload_file(file: UploadFile):
    """Upload a file to the mocked S3 bucket"""
    bucket = ssm.get_parameter(Name="/test/S3_BUCKET_NAME")["Parameter"]["Value"]
    s3.upload_fileobj(file.file, bucket, file.filename)
    return {"message": f"Uploaded {file.filename} to {bucket}"}


@app.get("/download/{filename}")
def download_file(filename: str):
    """Download a file from the mocked S3 bucket"""
    bucket = ssm.get_parameter(Name="/test/S3_BUCKET_NAME")["Parameter"]["Value"]
    response = s3.get_object(Bucket=bucket, Key=filename)
    content = response["Body"].read().decode("utf-8")
    return {"filename": filename, "content": content}
