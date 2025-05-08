import time
import threading
from collections import deque
from bme280 import BME280
from ltr559 import LTR559


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