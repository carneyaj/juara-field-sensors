import numpy as np
import time

from model import Model
from sound import Stream
from display import Display
from sensors import Sensors

model = Model("model_int8")
stream = Stream(device="adau7002")
display = Display()
sensors = Sensors()

stream.start()
last_update = time.time()
try:
    while True:
        if sensors.mode == 1:
            display.turn_on()
        else:
            display.turn_off()

        data = stream.get_audio()
        timestamp = time.time()
        labels = model.predict_threshold([data], min_p=0.5, timestamp=timestamp)
        # display.clear_left()
        for label, _ in labels:
            display.print_left(label)
        if time.time() > last_update + 5:
            w = sensors.get_average()
            display.clear_right()
            for name, value in w.items():
                display.print_right(f"{name}: {value:.1f}", stdout=False)
            last_update = time.time()

except KeyboardInterrupt:
    display.turn_off()