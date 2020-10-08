from subaru_link_service import SubaruLinkService 
from subaru_link_gateway import SubaruLinkGateway
import asyncio
import os
import settings

LOOP = asyncio.get_event_loop()

class VehicleSystemController():
    def __init__(self):
        self._slink = SubaruLinkService()
        self.response_body = {}

    def invoke(self, method, params, query_params):
        if params.get('pin') is None:
            raise AuthorizationException('missing PIN')
        if method.lower() not in ['put']:
            raise BadMethodException(f'{method} is not supported')
        LOOP.run_until_complete(
            self.__getattribute__(method.lower())(params, query_params))
        return (200, self.response_body)

    async def put(self, params, query_params):
        if await self._slink.connect(params['pin']):
            if params.get('doors', None) is not None:
                result = await self._actuate_doors(params)
            self.response_body = SubaruLinkGateway(self._slink.car_data).summary
            await self._slink.disconnect()
        else:
            raise ControllerException('failed to connect')
        
    async def patch(self, *args):
        return self.put(*args)
    
    async def get(self, params, query_params):
        return (405, {'error': 'Bad Method'})
    
    async def post(self, params):
        return (405, {'error': 'Bad Method'})
    
    async def delete(self, params):
        return (405, {'error': 'Bad Method'})

    async def _actuate_doors(self, params):
        if params['doors'] == 'unlocked':
            if not await self._slink.unlock():
                raise ControllerException('failed to unlock vehicle')
        elif params['doors'] == 'locked':
            if not await self._slink.lock():
                raise ControllerException('failed to lock vehicle')
        else:
            raise InvalidParamException('invalid param value: doors')
    
    async def _actuate_engine(self, params):
        if self._car_data.get("climate") is None:
            await self._fetch_climate_settings()
        await self._ctrl.remote_start(self._current_vin, self._car_data["climate"])
    

class ControllerException(Exception):
    status_code = 500

class InvalidRequestException(Exception):
    status_code = 400

class InvalidParamException(ControllerException):
    status_code = 420

class AuthorizationException(ControllerException):
    status_code = 401

class BadMethodException(ControllerException):
    status_code = 405