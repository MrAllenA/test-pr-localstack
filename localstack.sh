#!/bin/bash
echo "🚀 Initializing Localstack with mock SSM parameters and S3 bucket..."

# Fake AWS credentials (Localstack ignores them but boto3 requires them)
export AWS_ACCESS_KEY_ID=fake
export AWS_SECRET_ACCESS_KEY=fake

# AWS CLI shorthand
AWS="aws --endpoint-url=http://localhost:4566 --region ap-south-1"

# ------------------------
# Seed SSM Parameters
# ------------------------
$AWS ssm put-parameter --name "/test/DB_CONN_URL" --value "postgresql://postgres:postgres@localhost/test" --type "String"
$AWS ssm put-parameter --name "/test/JWT_SECRET" --value "random_jwt_secret_12345" --type "String"
$AWS ssm put-parameter --name "/test/S3_BUCKET_NAME" --value "test-s3-bucket" --type "String"
$AWS ssm put-parameter --name "/test/PAYSHARP_API_TOKEN" --value "paysharp_api_token_xyz" --type "String"
$AWS ssm put-parameter --name "/test/PAYSHARP_BASE_URL" --value "https://api.paysharp.com" --type "String"

# ------------------------
# Create mock S3 bucket
# ------------------------
$AWS s3 mb s3://test-s3-bucket || true
echo "✅ Created mock S3 bucket: test-s3-bucket"

echo "✅ SSM parameters and mock S3 setup complete!"
