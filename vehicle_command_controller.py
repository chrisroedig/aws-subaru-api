from subaru_link_service import SubaruLinkService 
from subaru_link_gateway import SubaruLinkGateway
import asyncio
import os
import settings

LOOP = asyncio.get_event_loop()

class VehicleCommandController():
    COMMANDS = ['lock', 'unlock', 'start', 'stop', 'lights', 'horn']
    
    def __init__(self):
        self._slink = SubaruLinkService()
        self.command = None
        self.response = (500, {'message': 'no response' })

    def post_command(self, params):
        command = params.get('command')
        pin = params.get('pin')
        if pin is None:
            raise AuthorizationException('Missing PIN')
        if command.lower() not in self.COMMANDS:
            raise InvalidParamException('Invalid Command')
        self.validate_command(command, pin, params)
        return self.response

    def validate_command(self, command, pin, params):
        self.pin = pin
        self.params = params
        self.command = command.lower()
        self.response = (202, {'command': command })
        
    def execute_command(self):
        method_name = f'_execute_{self.command}'
        self.command_method = self.__getattribute__(method_name)
        LOOP.run_until_complete(self._execute_command())
        print('execute_command Finished!')
    
    async def _execute_command(self):
        if await self._slink.connect(self.pin):
            await self.command_method(self.params)
            await self._slink.disconnect()

    async def _execute_unlock(self, params):
        await self._slink.unlock()

    async def _execute_lock(self, params):
        await self._slink.lock()

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