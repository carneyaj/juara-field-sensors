import numpy as np
import pandas as pd
import time

from model import Model
from sound import Stream
from sensors import SingleReadSensors

model = Model("model_int8")
stream = Stream(device="adau7002")
sensors = SingleReadSensors()

stream.start()
try:
    df = pd.DataFrame()
    rows = 0
    while True:
        start_time = time.time()
        full_dict = sensors.get()
        while time.time() - start_time < 5 * 2:
            data = stream.get_audio()
            labels = model.predict_threshold([data], min_p=0.5, timestamp=timestamp)
            for label, _ in labels:
                if label in full_dict:
                    full_dict[label] += 1
                else:
                    full_dict[label] = 1
        df = pd.concat([df, pd.DataFrame([full_dict])], ignore_index=True)
        rows += 1
        print(f"{rows} rows logged, {len(df.columns)} columns")
        

except KeyboardInterrupt:
    display.turn_off()