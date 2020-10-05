import database
from models import Climb
import controllers

def lambda_handler(event, context):
    # NOTE: requires mapping template on API gateway
    path = event['context']['resource-path'][1:].replace("/","_")
    method = event['context']['http-method'].lower()
    params = event['body-json']
    query_params = event['params']['querystring']

    return dispatch_method(method, path, params, query_params)

def dispatch_method(method, path, params, query_params):
    # NOTE: worst router ever
    resource_name = path.split("/")[-1].title()
    method_name = method.lower()
    controller = getattr(controllers, f'{resource_name}')
    return getattr(controller, method_name)(params, query_params)
    
if __name__ == '__main__':
    dispatch_method("PUT", "/doors", {'unlocked': True, 'pin':1234}, {'vin': ''})