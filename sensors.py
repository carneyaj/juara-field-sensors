import time
import threading
from collections import deque

class SingleReadSensors():

    def __init__(self):
        self.LIVE = []
        try:
            from bme280 import BME280
            self.bme280 = BME280()
            self.LIVE.append("bme")
        except ImportError:
            pass
        try:
            from ltr559 import LTR559
            self.ltr559 = LTR559()
            self.LIVE.append("ltr")
        except ImportError:
            pass
        try:
            from enviroplus import gas
            self.gas = gas
            self.LIVE.append("gas")
        except ImportError:
            pass
        try:
            from pms5003 import PMS5003, ReadTimeoutError
            self.pms = PMS5003()
            self.ReadTimeoutError = ReadTimeoutError
            self.LIVE.append("aqi")
        except ImportError:
            pass

    def get(self) -> dict:
        sensor_dict = {}
        if "bme" in self.LIVE:
            sensor_dict.update({
                "temp": self.bme280.get_temperature(),
                "pressure": self.bme280.get_pressure(),
                "humidity": self.bme280.get_humidity(),
            })
        if "ltr" in self.LIVE:
            sensor_dict['lux'] = self.ltr559.get_lux()
        if "gas" in self.LIVE:
            sensor_dict.update({
                "gas-reducing": self.gas.read_reducing(),
                "gas-oxidising": self.gas.read_oxidising(),
                "nh3": self.gas.read_nh3(),
            })
        if "aqi" in self.LIVE:
            try:
                aqi_str = str(self.pms.read())
                aqi_cats = aqi_str.split("\n")
                for cat in aqi_cats:
                    print(cat)
                    k, v = cat.split(":")
                    v = int(v.replace(" ", ""))
                    sensor_dict[k] = v
            except self.ReadTimeoutError:
                self.pms = PMS5003()
        return sensor_dict
            

class Sensors():

    def __init__(self, max_samples=5):
        self.bme280 = BME280()
        self.ltr559 = LTR559()

        self.max_samples = max_samples
        self.samples = deque(maxlen=max_samples)
        self._stop_event = threading.Event()

        self.thread = threading.Thread(target=self._update_sensors)
        self.thread.daemon = True
        self.thread.start()
        self.button = 0
        self.mode = 0

    def _update_sensors(self):
        while not self._stop_event.is_set():
            sensor_data = self.get()
            self.samples.append(sensor_data)
            if self.ltr559.get_proximity() > 1500:
                button = 1
            else:
                button = 0
            if button > self.button:
                self.mode = (self.mode + 1) % 2
            self.button = button
            time.sleep(1)

    def get(self) -> dict:
        sensors_dict = {
            "temp": self.bme280.get_temperature(),
            "pres": self.bme280.get_pressure(),
            "hum": self.bme280.get_humidity(),
            "lux": self.ltr559.get_lux(),
        }
        return sensors_dict

    def get_average(self) -> dict:
        avg_data = {"temp": 0, "pres": 0, "hum": 0, "lux": 0}
        num_samples = len(self.samples)

        if num_samples == 0:
            return avg_data

        for sample in self.samples:
            for key in avg_data:
                avg_data[key] += sample[key]

        for key in avg_data:
            avg_data[key] /= num_samples

        return avg_data

    def stop(self):
        self._stop_event.set()
        self.thread.join()