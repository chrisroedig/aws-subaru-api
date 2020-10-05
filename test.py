from subaru_link_service import SubaruLinkService 
from subaru_link_gateway import SubaruLinkGateway
import asyncio
import os
import settings

LOOP = asyncio.get_event_loop()

async def test():
    
    print(
        os.getenv("SUBARU_USERNAME"),
        os.getenv("SUBARU_PASSWORD"),
        os.getenv("SUBARU_DEVICE_ID"),
        os.getenv("SUBARU_PIN"),
        os.getenv("SUBARU_DEVICE_NAME"))
    sls = SubaruLinkService()
    if await sls.connect(os.getenv("SUBARU_PIN")):
        slg = SubaruLinkGateway(car_data=sls.car_data)
        print(slg.summary)
    await sls.disconnect()

if __name__ == "__main__":
    LOOP.run_until_complete(test())