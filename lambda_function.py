import boto3
import pandas as pd
from options_price.cli.py import OptionsPricing

S3_RESOURCE = boto3.resource('s3')
S3_BUCKET = S3_RESOURCE.Bucket('shell-test-lambda')

def lambda_handler(event, context):   
    try:
        s3_object = S3_BUCKET.Object('excelfile').get()
        data = s3_object['Body'].read()
        workbook = pd.read_excel(data, sheet_name=['Volatility', 'Summary'])
        print(workbook)
        return
    except Exception as e:
        print(e)
        return 
    