from subarulink import Controller
from subarulink import SubaruException
from aiohttp import ClientSession
import settings
import os
import asyncio
import logging 

LOGGER = logging.getLogger("subarulink")
STREAMHANDLER = logging.StreamHandler()
STREAMHANDLER.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
LOGGER.addHandler(STREAMHANDLER)
LOOP = asyncio.get_event_loop()

class SubaruLinkService():
    def __init__(self):
        self._current_vin = os.getenv("SUBARU_VIN")
        self.__ctrl = None
        self.attributes = None
        self._pin = None
    
    @property
    def _ctrl(self):
        if self.__ctrl is None:
            self._session = ClientSession()
            self._cars = []
            self.__ctrl = Controller(
                self._session, # aiohttp
                os.getenv("SUBARU_USERNAME"),
                os.getenv("SUBARU_PASSWORD"),
                os.getenv("SUBARU_DEVICE_ID"),
                self._pin,
                os.getenv("SUBARU_DEVICE_NAME"),
            )
        return self.__ctrl
    
    async def connect(self, pin):
        LOGGER.info("Connecting to Subaru Remote Services API")
        self._pin = pin 
        try:
            if await self._ctrl.connect():
                self._current_hasEV = self._ctrl.get_ev_status(self._current_vin)
                self._current_hasRES = self._ctrl.get_res_status(self._current_vin)
                self._current_hasRemote = self._ctrl.get_remote_status(self._current_vin)
                self._current_api_gen = self._ctrl.get_api_gen(self._current_vin)
                LOGGER.info("Successfully connected")
            if self._current_api_gen == "g2":
                await self._fetch()
            else:
                LOGGER.error("Unsupprted telematics version: %s" % self._current_api_gen)
                return False
        except SubaruException:
            LOGGER.error("Unable to connect.  Check Username/Password.")
            await self._session.close()
            return False
        return True

    async def disconnect(self):
        await self._session.close()

    async def _fetch(self):
        LOGGER.info("Fetching data for %s..." % self._ctrl.vin_to_name(self._current_vin))
        self._car_data = await self._ctrl.get_data(self._current_vin)
        return True

    async def update(self):
        LOGGER.info("Requesting update for %s..." % self._ctrl.vin_to_name(self._current_vin))
        await self._ctrl.update(self._current_vin)
        await self._fetch()
        return True

    @property
    def car_data(self):
        return self._car_data
    
async def test():
    sls = SubaruLinkService()
    if await sls.connect(os.getenv("SUBARU_PIN")):
        print(sls._car_data)
    await sls.disconnect()

if __name__ == '__main__':
    LOOP.run_until_complete(test())