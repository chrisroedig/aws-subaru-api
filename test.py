from subaru_link_service import SubaruLinkService 
from subaru_link_gateway import SubaruLinkGateway
import asyncio
import os
import settings
from pprint import pprint

LOOP = asyncio.get_event_loop()

async def test():
    sls = SubaruLinkService()
    if await sls.connect(os.getenv("SUBARU_PIN")):
        slg = SubaruLinkGateway(car_data=sls.car_data)
        success = await sls.lock()
        print(slg.summary)
    await sls.disconnect()

if __name__ == "__main__":
    LOOP.run_until_complete(test())