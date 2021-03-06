import json
from vehicle_command_controller import VehicleCommandController
from vehicle_command_controller import ControllerException
from vehicle_command_controller import BadMethodException
import threading
import os
import settings

def lambda_handler(event, context):
    # NOTE: event contains the entire API gateway context
    # event => json decoded params from aws api gateway
    try:
        request_body_json = event
        method = 'POST' # assimng we set up the API gateway like this
        path = '/'
        query_params = {}
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
    return json.dumps(response_body)

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
    event = {
            'pin': os.getenv("SUBARU_PIN"),
            'command': 'unlock'
        }
    context = None
    print(lambda_handler(event, context))