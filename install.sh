#!/bin/bash

sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y git
sudo apt-get install -y libasound2-dev portaudio19-dev libatlas-base-dev

python3 -m venv myenv
source myenv/bin/activate
echo 'alias act="source myenv/bin/activate"' >> ~/.bashrc
source ~/.bashrc

pip3 install sounddevice

TFVER=2.16.1
WHL="tflite_runtime-${TFVER/-/}-cp311-none-linux_aarch64.whl"
BASE_URL="https://github.com/PINTO0309/TensorflowLite-bin/releases/download/v${TFVER}/"
curl -L -o $WHL $BASE_URL$WHL

pip3 install wheel
pip3 install -U $WHL

pip3 install numpy==1.26.4

# # Old paths, now included in repo
# GHURL="https://raw.githubusercontent.com/birdnet-team/BirdNET-Analyzer/master"
# MODEL="/birdnet_analyzer/checkpoints/V2.4/BirdNET_GLOBAL_6K_V2.4_Model_INT8.tflite"
# LABELS="/birdnet_analyzer/labels/V2.4/BirdNET_GLOBAL_6K_V2.4_Labels_en_uk.txt"
# curl -L -o model_int8.tflite $GHURL$MODEL
# curl -L -o labels.txt $GHURL$LABELS

CONFIG_TXT=(
    "dtoverlay=pi3-miniuart-bt"
    "dtoverlay=adau7002-simple"
	"test"
)

CONFIG_DIR="/boot/firmware"
CONFIG_FILE=config.txt

for CONFIG_LINE in "${CONFIG_TXT[@]}"; do
    if [[ -n "$CONFIG_LINE" ]]; then
        echo "Adding $CONFIG_LINE to $CONFIG_DIR/$CONFIG_FILE"
        sudo sed -i "s|^#${CONFIG_LINE}|${CONFIG_LINE}|" "$CONFIG_DIR/$CONFIG_FILE"
        if ! grep -q "^${CONFIG_LINE}" "$CONFIG_DIR/$CONFIG_FILE"; then
            printf "%s\n" "$CONFIG_LINE" | sudo tee -a "$CONFIG_DIR/$CONFIG_FILE" > /dev/null
        fi
    fi
done

pip3 install pimoroni-bme280 st7735 ltr559 pillow fonts font-roboto gpiod gpiodevice

# # Not needed for now
# git clone https://github.com/pimoroni/enviroplus-python
# cd enviroplus-python
# ./install.sh
# cd ..

git clone https://github.com/carneyaj/juara-field-sensors.git
cd juara-field-sensors

read -p "Do you want to reboot now? (y/n): " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
    echo "Rebooting..."
    sudo reboot
else
    echo "Reboot canceled."
fi
