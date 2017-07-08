import boto3
import logging

##user variables
#CloudFront Distribution ID eg. E1423SDSDSJBB343T

cloudFrontID = "XXXXXXXXXXXXXX"

#Failover Origin ID eg. S3-bucketname.failover.bucket

failoverS3BucketDomain = "s3-BUCKET_NAME.s3.amazonaws.com"
cf = boto3.client("cloudfront")

#logger variables
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    #logger.info("Event {0}".format(event))
    current_cf_config = get_cf_config(cloudFrontID)
    newConfig,Id,Etag = set_cf_config_values(current_cf_config)
    response = update_cf_config(newConfig,Id,Etag)
    logger.info("Ran Lambda Function with response {0}".format(response))
    return 0

def set_cf_config_values(current_cf_config):
    try:
        logger.info("Setting new CF distribution configs")
        my_DistributionConfig = current_cf_config['Distribution']['DistributionConfig']
        #logger.info("Current TargetOriginId {0}".format(my_DistributionConfig['Origins']["DomainName"]))
        # Add in our failover origin for default behaviour
        my_DistributionConfig['Origins']['Items'][0]["DomainName"] = failoverS3BucketDomain
        my_Id = current_cf_config['Distribution']['Id']
        my_Etag = current_cf_config["ETag"]
        return (my_DistributionConfig,my_Id,my_Etag)
    except Exception as e:
        logger.debug("Caught Exception whilst updating current CF Config values: {0}".format(e))
        return "Caught Exception whilst updating current CF Config values: {0}".format(e)
 
def get_cf_config(distroID):
    try:
        logger.info("Getting current CF distribution configs")
        response = cf.get_distribution(
            Id = distroID
        )
        return response
    except Exception as e:
        logger.debug("Caught Exception whilst getting CF Distribution: {0}".format(e))
        return "Caught Exception whilst getting CF Distribution: {0}".format(e)

def update_cf_config(my_DistributionConfig,my_Id,my_Etag):
    try:
        logger.info("Updating CF distribution with new configs")            
        response = cf.update_distribution(
            DistributionConfig = my_DistributionConfig,
            Id = my_Id,
            IfMatch = my_Etag
        )
        #logger.info("DistributionConfig {0}".format(my_DistributionConfig))
        return response
    except Exception as e:
        logger.debug("Caught Exception whilst updating CF Distribution: {0}".format(e))
        return "Caught Exception whilst updating CF Distribution: {0}".format(e)

