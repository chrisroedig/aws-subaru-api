from datetime import datetime
import subarulink.const as sc
import logging 



class SubaruLinkGateway():
    def __init__(self, car_data=None):
        self._car_data = car_data

    @property
    def summary(self):
        s = {}
        
        status_time = datetime.fromtimestamp(self._car_data["status"][sc.TIMESTAMP])
        s['status_time'] = status_time.isoformat()

        timediff = (datetime.now() - status_time)

        s['status_timediff_str'] = "%d days, %d hours, %d minutes ago \n" % (
            timediff.days, 
            timediff.seconds // 3600, 
            (timediff.seconds) // 60 % 60,)
        
        s['odometer'] =  _km_to_miles(self._car_data["status"][sc.ODOMETER])
        s['avg_mpg'] = _L100km_to_mpg(self._car_data["status"][sc.AVG_FUEL_CONSUMPTION])
        
        if self._car_data["status"].get(sc.LATITUDE) and self._car_data["status"].get(sc.LONGITUDE):
            s['pos_lat'] = self._car_data["status"].get(sc.LATITUDE)
            s['pos_lng'] = (self._car_data["status"].get(sc.LONGITUDE) or 0) * -1
            s['pos_head'] = (self._car_data["status"].get(sc.HEADING) or 0)
        
        s['state'] = self._car_data["status"][sc.VEHICLE_STATE]

        s['tire_press_fl'] = _kpa_to_psi(self._car_data["status"][sc.TIRE_PRESSURE_FL])
        s['tire_press_fr'] = _kpa_to_psi(self._car_data["status"][sc.TIRE_PRESSURE_FR])
        s['tire_press_rl'] = _kpa_to_psi(self._car_data["status"][sc.TIRE_PRESSURE_RL])
        s['tire_press_rr'] = _kpa_to_psi(self._car_data["status"][sc.TIRE_PRESSURE_RR])

        s['ext_temp'] = _c_to_f(self._car_data["status"].get(sc.EXTERNAL_TEMP,0))
        s['doors'] =  self._car_data.get('doors')
        return s

def _km_to_miles(meters):
    return float(meters) * 0.62137119


def _c_to_f(temp_c):
    return float(temp_c) * 1.8 + 32.0


def _L100km_to_mpg(L100km):
    return round(235.215 / L100km, 1)


def _kpa_to_psi(kpa):
    return kpa / 68.95