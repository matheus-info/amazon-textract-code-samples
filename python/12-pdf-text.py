import boto3
import time


def start_job(s3_bucket_name, object_name, region):
    response = None
    client = boto3.client('textract', region)
    response = client.start_document_text_detection(
        DocumentLocation={
            'S3Object': {
                'Bucket': s3_bucket_name,
                'Name': object_name
            }})

    return response["JobId"]


def is_job_complete(job_id):
    time.sleep(5)
    client = boto3.client('textract')
    response = client.get_document_text_detection(JobId=job_id)
    status = response["JobStatus"]
    print("Job status: {}".format(status))

    while(status == "IN_PROGRESS"):
        time.sleep(5)
        response = client.get_document_text_detection(JobId=job_id)
        status = response["JobStatus"]
        print("Job status: {}".format(status))

    return status


def get_job_results(job_id):
    pages = []
    time.sleep(5)
    client = boto3.client('textract')
    response = client.get_document_text_detection(JobId=job_id)
    pages.append(response)
    print("Resultset page received: {}".format(len(pages)))
    next_token = None
    if 'NextToken' in response:
        next_token = response['NextToken']

    while next_token:
        time.sleep(5)
        response = client.\
            get_document_text_detection(JobId=job_id, NextToken=next_token)
        pages.append(response)
        print("Resultset page received: {}".format(len(pages)))
        next_token = None
        if('NextToken' in response):
            next_token = response['NextToken']

    return pages


if __name__ == "__main__":
    # Document
    s3_bucket_name = "ki-textract-demo-docs"
    document_name = "Amazon-Textract-Pdf.pdf"
    region = "us-east-1"

    job_id = start_job(s3_bucket_name, document_name, region)
    print("Started job with id: {}".format(job_id))
    if(is_job_complete(job_id)):
        response = get_job_results(job_id)

    # print(response)

    # Print detected text
    for result_page in response:
        for item in result_page["Blocks"]:
            if item["BlockType"] == "LINE":
                print('\033[94m' + item["Text"] + '\033[0m')
