from subarulink import Controller
from subarulink import SubaruException
from aiohttp import ClientSession
from functools import cached_property
import os
import asyncio
import logging 

LOGGER = logging.getLogger("subarulink")
STREAMHANDLER = logging.StreamHandler()
STREAMHANDLER.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(STREAMHANDLER)
LOOP = asyncio.get_event_loop()

class SubaruVehicle():
    def __init__(self, vin, username, password, device_id, device_name):
        self.__vin = vin
        self.__username = username
        self.__password = password
        self.__device_id = device_id
        self.__device_name = device_name
        self.__pin = None
        self.__car_data = None
        self.__connected = False
    
    @cached_property
    def session(self):
        return ClientSession()

    @cached_property
    def ctrl(self):
        self._cars = []
        return Controller(
                self.session, # aiohttp
                self.__username,
                self.__password,
                self.__device_id,
                self.__pin,
                self.__device_name
            )

    @property
    def name(self):
        if not self.__connected:
            return None
        return self.ctrl.vin_to_name(self.__vin)

    async def connect(self, pin):
        if self.__connected:
            LOGGER.info("Already connected to Subaru Remote Services API")
            return True
        LOGGER.info("Connecting to Subaru Remote Services API")
        self.__pin = pin 
        api_version = None
        try:
            if await self.ctrl.connect():
                api_version = self.ctrl.get_api_gen(self.__vin)
                LOGGER.info("Successfully connected")
                self.__connected = True
            if api_version == "g2":
                await self.fetch()
            else:
                LOGGER.error("Unsupprted telematics version: %s" % api_version)
                return False
        except SubaruException:
            LOGGER.error("Unable to connect.  Check Username/Password.")
            await self.session.close()
            return False
        return True


    async def disconnect(self):
        await self.session.close()

    async def fetch(self, pin=None):
        await self.connect(pin)
        LOGGER.info("Fetching data for %s..." % self.name)
        self.__car_data = await self.ctrl.get_data(self.__vin)
        return True

    async def update(self, pin=None):
        await self.connect(pin)
        LOGGER.info("Requesting update for %s..." % self.name)
        await self.ctrl.update(self.__vin)
        await self.fetch()
        return True

    async def unlock(self, pin=None):
        await self.connect(pin)
        LOGGER.info("Requesting door unlock for %s..." % self.name)
        if await self.ctrl.unlock(self.__vin):
            self.__car_data['doors'] = 'unlocked'
            return True
        else:
            return False
    
    async def lock(self, pin=None):
        await self.connect(pin)
        LOGGER.info("Requesting door lock for %s..." % self.name)
        if await self.ctrl.lock(self.__vin):
            self.__car_data['doors'] = 'locked'
            return True
        else:
            return False
    async def list_climate_presets(self, pin=None):
        await self.connect(pin)
        LOGGER.info("Requesting climate presets for %s..." % self.name)
        preset_names = await self.ctrl.list_climate_preset_names(self.__vin)
        return preset_names

    async def start_engine(self, pin=None):
        await self.connect(pin)
        preset_names = await self.ctrl.list_climate_preset_names(self.__vin)
        LOGGER.info(f"Requesting engine START for ${self.name} with climate preset ${preset_names[0]}")
        await self.ctrl.remote_start(self.__vin, preset_names[0])
    
    async def stop_engine(self, pin=None):
        await self.connect(pin)
        LOGGER.info("Requesting engine STOP for %s..." % self.name)
        await self.ctrl.remote_stop(self._current_vin)

    @property
    def car_data(self):
        return self.__car_data

def make_vehicle():
    return SubaruVehicle(
        os.getenv("SUBARU_VIN"),
        os.getenv("SUBARU_USERNAME"),
        os.getenv("SUBARU_PASSWORD"),
        os.getenv("SUBARU_DEVICE_ID"),
        os.getenv("SUBARU_DEVICE_NAME"))

def unlock(pin):
    vehicle = make_vehicle()
    asyncio.run(vehicle.unlock(pin))

def start_engine(pin):
    vehicle = make_vehicle()
    asyncio.run(vehicle.start_engine(pin))
    vehicle.disconnect()

if __name__ == "__main__":
    pin_code = input('Enter your pin: ')
    start_engine(pin_code)