# Necesssary import
from time import sleep
from prefect_aws import S3Bucket, AwsCredentials

# Function for credentials
def create_aws_creds_block():
    # Define the credentials object
    my_aws_creds_obj = AwsCredentials(
        aws_access_key_id = "123abc", aws_secret_access_key = "abc123"
    )
    # Save credentials
    my_aws_creds_obj.save(name = "my-aws-creds", overwrite = True)

# Function for creating an s3 bucket
def create_s3_bucket_block():
    # Load credentials
    aws_creds = AwsCredentials.load("my-aws-creds")
    # Define s3 bucket object
    my_s3_bucket_obj = S3Bucket(
        bucket_name = "my-first-bucket-abc", credentials = aws_creds
    )
    # Save bucket
    my_s3_bucket_obj.save(name = "s3-bucket-example", overwrite = True)

# If the script is executed
if __name__ == "__main__":
    # create credentials block
    create_aws_creds_block()
    # pause for 5 seconds
    sleep(5)
    # create s3 bucket
    create_s3_bucket_block()
