import boto3
import pandas as pd
import json
from options import OptionsPricing

S3_RESOURCE = boto3.resource('s3')
S3_BUCKET = S3_RESOURCE.Bucket('shell-test-lambda')

def handler(event, context): 
    headers = {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            }
    try:
        filename = event["filename"]
        s3_object = S3_BUCKET.Object(filename).get()
        data = s3_object['Body'].read()
        options = OptionsPricing(data)
        formula_values = options._set_formula_values()
        option_value = options.run()
        output = { "option value": option_value, "formula values": formula_values }
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(output)
        }

    except Exception as e:
        print(e)
        return 
    