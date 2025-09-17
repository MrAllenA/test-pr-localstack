from fastapi import FastAPI, UploadFile
import boto3
import os

app = FastAPI()

# Config
SSM_ENDPOINT = os.getenv("SSM_ENDPOINT", "http://localhost:4566")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:4566")

# Create boto3 clients (point to Localstack by default)
ssm = boto3.client(
    "ssm",
    region_name=AWS_REGION,
    endpoint_url=SSM_ENDPOINT,
    aws_access_key_id="fake",
    aws_secret_access_key="fake",
)

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id="fake",
    aws_secret_access_key="fake",
)


@app.get("/")
def root():
    return {"message": "Hello Suckkers"}


@app.get("/config")
def get_config():
    """Fetch DB connection string from SSM"""
    param = ssm.get_parameter(Name="/test/DB_CONN_URL")
    return {"DB_CONN_URL": param["Parameter"]["Value"]}


@app.get("/secrets")
def get_secrets():
    """Fetch multiple SSM parameters"""
    keys = ["/test/JWT_SECRET", "/test/S3_BUCKET_NAME"]
    result = {}
    for key in keys:
        param = ssm.get_parameter(Name=key)
        result[key] = param["Parameter"]["Value"]
    return result


@app.get("/buckets")
def list_buckets():
    """List all buckets in Localstack S3"""
    buckets = s3.list_buckets()
    return {"buckets": [b["Name"] for b in buckets.get("Buckets", [])]}


@app.post("/upload")
def upload_file(file: UploadFile):
    """Upload a file to the mock S3 bucket"""
    bucket = ssm.get_parameter(Name="/test/S3_BUCKET_NAME")["Parameter"]["Value"]
    s3.upload_fileobj(file.file, bucket, file.filename)
    return {"message": f"Uploaded {file.filename} to {bucket}"}


@app.get("/download/{filename}")
def download_file(filename: str):
    """Download a file from the mock S3 bucket"""
    bucket = ssm.get_parameter(Name="/test/S3_BUCKET_NAME")["Parameter"]["Value"]
    response = s3.get_object(Bucket=bucket, Key=filename)
    content = response["Body"].read().decode("utf-8")
    return {"filename": filename, "content": content}
