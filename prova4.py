import boto3

bucket = 'textract-console-eu-west-2-65379a31-a1cc-472f-b793-51c84519ab41'
document = 'phoenix_snowball_stock_ftiss_vf4_5_6.pdf'
s3_connection = boto3.resource('s3')           


textract = boto3.client('textract')
sns = boto3.client('sns')

response = textract.start_document_analysis(DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': document}},
        FeatureTypes=["TABLES",])
job_id=response['JobId']

analysis = textract.get_document_analysis(JobId=job_id)
print(type(analysis))
print(analysis)