import boto3
import boto3
import json
import sys
import time

class ProcessType:
    DETECTION = 1
    ANALYSIS = 2
    
class TextractProcessor:
    jobId = ''
    textract = boto3.client('textract')
    sqs = boto3.client('sqs')
    sns = boto3.client('sns')

    roleArn = ''   
    bucket = ''
    document = ''
    
    sqsQueueUrl = ''
    snsTopicArn = ''
    processType = ''

    results = None

    def __init__(self, role, bucket, document):    
        self.roleArn = role
        self.bucket = bucket
        self.document = document    
    
    def ProcessDocument(self,type):
        jobFound = False
        
        self.processType=type
        validType=False

        #Determine which type of processing to perform
        if self.processType==ProcessType.DETECTION:
            response = self.textract.start_document_text_detection(DocumentLocation={'S3Object': {'Bucket': self.bucket, 'Name': self.document}},
                    NotificationChannel={'RoleArn': self.roleArn, 'SNSTopicArn': self.snsTopicArn})
            print('Processing type: Detection')
            validType=True        

        
        if self.processType==ProcessType.ANALYSIS:
            response = self.textract.start_document_analysis(DocumentLocation={'S3Object': {'Bucket': self.bucket, 'Name': self.document}},
                FeatureTypes=["TABLES", "FORMS"],
                NotificationChannel={'RoleArn': self.roleArn, 'SNSTopicArn': self.snsTopicArn})
            print('Processing type: Analysis')
            validType=True    

        if validType==False:
            print("Invalid processing type. Choose Detection or Analysis.")
            return

        print('Start Job Id: ' + response['JobId'])
        dotLine=0
        while jobFound == False:
            sqsResponse = self.sqs.receive_message(QueueUrl=self.sqsQueueUrl, MessageAttributeNames=['ALL'],
                                          MaxNumberOfMessages=10)
            if sqsResponse:
                if 'Messages' not in sqsResponse:
                    if dotLine<40:
                        print('.', end='')
                        dotLine=dotLine+1
                    else:
                        print()
                        dotLine=0    
                    sys.stdout.flush()
                    time.sleep(5)
                    continue

                for message in sqsResponse['Messages']:
                    notification = json.loads(message['Body'])
                    textMessage = json.loads(notification['Message'])
                    print(textMessage['JobId'])
                    print(textMessage['Status'])
                    if str(textMessage['JobId']) == response['JobId']:
                        print('Matching Job Found:' + textMessage['JobId'])
                        jobFound = True
                        self.results = self.GetResults(textMessage['JobId'])
                        self.sqs.delete_message(QueueUrl=self.sqsQueueUrl,
                                       ReceiptHandle=message['ReceiptHandle'])
                    else:
                        print("Job didn't match:" +
                              str(textMessage['JobId']) + ' : ' + str(response['JobId']))
                    # Delete the unknown message. Consider sending to dead letter queue
                    self.sqs.delete_message(QueueUrl=self.sqsQueueUrl,
                                   ReceiptHandle=message['ReceiptHandle'])

        print('Done!')
    
    def CreateTopicandQueue(self):
      
        millis = str(int(round(time.time() * 1000)))

        #Create SNS topic
        snsTopicName="AmazonTextractTopic" + millis

        topicResponse=self.sns.create_topic(Name=snsTopicName)
        self.snsTopicArn = topicResponse['TopicArn']

        #create SQS queue
        sqsQueueName="AmazonTextractQueue" + millis
        self.sqs.create_queue(QueueName=sqsQueueName)
        self.sqsQueueUrl = self.sqs.get_queue_url(QueueName=sqsQueueName)['QueueUrl']
 
        attribs = self.sqs.get_queue_attributes(QueueUrl=self.sqsQueueUrl,
                                                    AttributeNames=['QueueArn'])['Attributes']
                                        
        sqsQueueArn = attribs['QueueArn']

        # Subscribe SQS queue to SNS topic
        self.sns.subscribe(
            TopicArn=self.snsTopicArn,
            Protocol='sqs',
            Endpoint=sqsQueueArn)

        #Authorize SNS to write SQS queue 
        policy = """{{
        "Version":"2012-10-17",
        "Statement":[
            {{
            "Sid":"MyPolicy",
            "Effect":"Allow",
            "Principal" : {{"AWS" : "*"}},
            "Action":"SQS:SendMessage",
            "Resource": "{}",
            "Condition":{{
                "ArnEquals":{{
                "aws:SourceArn": "{}"
                }}
            }}
            }}
        ]
        }}""".format(sqsQueueArn, self.snsTopicArn)
        
        response = self.sqs.set_queue_attributes(
            QueueUrl = self.sqsQueueUrl,
            Attributes = {
                'Policy' : policy
            })

    def DeleteTopicandQueue(self):
        self.sqs.delete_queue(QueueUrl=self.sqsQueueUrl)
        self.sns.delete_topic(TopicArn=self.snsTopicArn)
    
    def GetResults(self, jobId):
        maxResults = 1000
        paginationToken = None
        finished = False

        while finished == False:

            response=None

            if self.processType==ProcessType.ANALYSIS:
                if paginationToken==None:
                    response = self.textract.get_document_analysis(JobId=jobId,
                        MaxResults=maxResults)
                else: 
                    response = self.textract.get_document_analysis(JobId=jobId,
                        MaxResults=maxResults,
                        NextToken=paginationToken)                           

            if self.processType==ProcessType.DETECTION:
                if paginationToken==None:
                    response = self.textract.get_document_text_detection(JobId=jobId,
                        MaxResults=maxResults)
                else: 
                    response = self.textract.get_document_text_detection(JobId=jobId,
                        MaxResults=maxResults,
                        NextToken=paginationToken)   

            blocks=response['Blocks'] 
            return blocks
            # print ('Detected Document Text')
            # print ('Pages: {}'.format(response['DocumentMetadata']['Pages']))
        
            # # Display block information
            # for block in blocks:
            #         self.DisplayBlockInfo(block)
            #         print()
            #         print()

            # if 'NextToken' in response:
            #     paginationToken = response['NextToken']
            # else:
            #     finished = True

def main(doc = ''):
    roleArn = 'arn:aws:iam::529573128668:role/TextractRole'   
    bucket = 'textract-console-eu-west-2-65379a31-a1cc-472f-b793-51c84519ab41'
    document = doc if doc else 'Phoenix Snowball Stock FTISS vf4-5-6.pdf'

    analyzer=TextractProcessor(roleArn, bucket,document)
    analyzer.CreateTopicandQueue()
    analyzer.ProcessDocument(ProcessType.ANALYSIS)
    analyzer.DeleteTopicandQueue()
    return analyzer.results


def analyze_document(document = 'Phoenix Snowball Stock FTISS vf4-5-6-1.png', bucket = 'textract-console-eu-west-2-65379a31-a1cc-472f-b793-51c84519ab41'):
        textract = boto3.client('textract')
        sns = boto3.client('sns')

        response = textract.analyze_document(Document={'S3Object': {'Bucket': bucket, 'Name': document}},
                FeatureTypes=["TABLES",])
        blocks = response['Blocks']
        print(type(blocks))
        print(blocks)
        return blocks

