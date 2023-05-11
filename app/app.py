import boto3
import pandas as pd
import json
from options import OptionsPricing
from file_reader import FileReader

S3_RESOURCE = boto3.resource('s3')
S3_BUCKET = S3_RESOURCE.Bucket('shell-test-lambda')

def handler(event, context): 
    headers = {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            }
    try:
        output = {}
        filename = event.get("filename")
        s3_object = S3_BUCKET.Object(filename).get()
        data = s3_object['Body'].read()
        options = OptionsPricing(data)
        if event.get('http_method') == 'POST':
            formula_values, market_data = options._set_formula_values()
            option_value = options.run()
            output = { "option value": option_value, "formula values": formula_values }
        elif event.get('http_method') == 'GET':
            formula_values, market_data = options._set_formula_values()
            output = { 
                "option": market_data['Option'][0],
                "future price": market_data['Future Price'][0],
                "strike": market_data['Strike'][0],
                "risk free rate": market_data['Risk Free Rate'][0],
                "type": market_data['Type'][0],
                "number of daily data": market_data['Number of Daily Data'][0]
             }
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(output)
        }

    except Exception as e:
        print("An exception occurred: ", e)
        raise
    