# S3 Static Site Failover

## Goal: Create a failover scenario for s3 hosted site for Disaster Recovery.

### Steps:
1. Create 2 buckets with static website hosting enabled and ensure Cross-Region Replication is enabled and objects are being replicated to the destination bucket.
1. Create a CloudFront Distribution and use primary S3 bucket as the origin.
1. Create a new R53 health check targeting CNAME of CF distribution (d123456789.cloudfront.net works as well) including path of health check object (eg. d123456789.cloudfront.net/healthcheck.txt)
1. Expand Advanced Configuration under Health Check and set request interval of Standard (30 sec) and Failure Threshold of at least 3.
1. Create a new Alarm and select an existing or a new SNS Topic (must be in US-EAST-1 region)
1. Create a new Lambda Function in any region other than US-EAST-1 using the s3_site_failover.py.
1. Create a new SNS trigger for the Lambda Function using CLI commands below.

    1. Create a new SNS subscription for Lambda Function:

        aws sns subscribe --topic-arn "YourSNSTopicARN" --protocol lambda --notification-endpoint "YourLambdaARN" --region "us-east-1"

    1. Create Lambda invoke permissions for SNS to invoke function:

        aws lambda add-permission --function-name "YourLambdaARN" --statement-id "HealthCheck_SNS_Lambda" --action "lambda:InvokeFunction" --principal "sns.amazonaws.com" --source-arn "YourSNSTopicARN" 

1. Ensure both bucket policies allow for public read access on the bucket. 

1. Upload a new error.html page into source bucket to avoid seeing 403 response for URI queries for non-existent objects.

        S3 -> Bucket -> Properties -> Static website hosting -> Error document

1. Upload a health check object into Original S3 bucket with cache control header set to no-cache (this will help negate false positives with R53 healthcheck):

        aws s3 cp "local/path/healthcheck.txt" "s3://bucketName/healthcheck.txt" --cache-control no-cache

1.  Simulate a bucket failure by changing the permission or deleting the health check object. This will result in R53 health check failure and triggering SNS/Lambda for the failover procedure.

