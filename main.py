import numpy as np
import pandas as pd
import time
import os

from model import Model
from sound import Stream
from sensors import SingleReadSensors

model = Model("model_int8")
stream = Stream(device="adau7002")
sensors = SingleReadSensors()

stream.start()
date = time.strftime("%Y-%m-%d")

try:
    date_time = time.strftime("%Y-%m-%d %H:%M:%S")
    file_start_time = time.time()
    df = pd.DataFrame()
    rows = 0
    while time.time() - file_start_time > 5 * 2 * 5:
        start_time = time.time()
        full_dict = sensors.get()
        full_dict["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        full_dict["date"] = date
        while time.time() - start_time < 5 * 2:
            data = stream.get_audio()
            timestamp = time.time()
            labels = model.predict_threshold([data], min_p=0.5, timestamp=timestamp)
            for label, _ in labels:
                if label in full_dict:
                    full_dict[label] += 1
                else:
                    full_dict[label] = 1
        df = pd.concat([df, pd.DataFrame([full_dict])], ignore_index=True)
        rows += 1
        print(f"{rows} rows logged, {len(df.columns)} columns")
    df.to_csv(f"data/{date}.csv.gz", index=False, , compression='gzip')
    print(f"Data saved and compressed to data/{date}.csv.gz")
    time.sleep(5)
    print("Shutting down...")
    # os.system("sudo halt")

except KeyboardInterrupt:
    display.turn_off()