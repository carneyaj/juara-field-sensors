import numpy as np
import pandas as pd
import time
import os
import subprocess

from model import Model
from sound import Stream
from sensors import SingleReadSensors

def ensure_usb_mounted(mount_point="/mnt/usb", device="/dev/sda1"):
    if not os.path.ismount(mount_point):
        os.makedirs(mount_point, exist_ok=True)
        subprocess.run(["sudo", "mount", device, mount_point], check=True)

ensure_usb_mounted()

model = Model("model_int8")
stream = Stream(device="adau7002")
sensors = SingleReadSensors()

stream.start()

try:
    date_time = time.strftime("%Y-%m-%d_%H_%M_%S")
    file_start_time = time.time()
    df = pd.DataFrame()
    rows = 0
    while time.time() - file_start_time < 5 * 2 * 5:
        start_time = time.time()
        full_dict = sensors.get()
        full_dict["timestamp"] = time.strftime("%Y-%m-%d_%H_%M_%S")
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

    df.to_csv(f"~/mnt/usb/{date_time}.csv.gz", index=False, compression='gzip')
    print(f"Data saved and compressed to data/{date_time}.csv.gz")
    time.sleep(5)
    print("Shutting down...")
    try:
        os.system("sudo halt")
    except:
        print("Error shutting down")

except KeyboardInterrupt:
    display.turn_off()