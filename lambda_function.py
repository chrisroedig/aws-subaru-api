import json
from vehicle_command_controller import VehicleCommandController
from vehicle_command_controller import ControllerException
from vehicle_command_controller import BadMethodException
import threading
import os
import settings

def lambda_handler(event, context):
    # NOTE: event contains the entire API gateway context
    # event => {
    #     "resource": "",
    #     "path": "", 
    #     "httpMethod": "", 
    #     "headers": {},
    #     "multiValueHeaders": {} 
    #     "queryStringParameters": null, 
    #     "multiValueQueryStringParameters": null, 
    #     "pathParameters": null, 
    #     "stageVariables": null, 
    #     "requestContext": {},
    #     "body": "", 
    #     "isBase64Encoded": false
    # }
    try:
        request_body_json = json.loads(event['body'])
        method = event['httpMethod']
        path = event['path']
        query_params = event['queryStringParameters']
        [ status_code, response_body ] = dispatch_method(
            method, path,
            request_body_json,
            query_params
        )
    except json.decoder.JSONDecodeError as err:
        status_code = 400
        response_body = {'error': 'Bad Request, invalid JSON'}
    # NOTE: return value must follow expected format for 
    # API gateway lambda proxy intgration
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response_body),
        "isBase64Encoded": False }

def dispatch_method(method, path, params, query_params):
    try:
        if not method == 'POST':
            raise BadMethodException(f'HTTP {method} not supported')
        ctrl = VehicleCommandController()
        ctrl.post_command(params)
        ctrl.execute_command()
        return ctrl.response
    except ControllerException as ex:
        return (ex.status_code, { "error": str(ex) })

if __name__ == "__main__":
    #print(dispatch_method('put', '/foo', {}, None))
    event = {
        'queryStringParameters': None,
        'httpMethod': 'POST',
        'path': '/foo',
        'body': json.dumps({
            'pin': os.getenv("SUBARU_PIN"),
            'command': 'unlock'
        })
    }
    context = None
    print(lambda_handler(event, context))