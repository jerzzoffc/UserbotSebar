git clone https://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@github.com/jerzzoffc/UserbotSebar && cd UserbotSebar

cmd run UBOT

apt update && apt upgrade -y

cd UserbotSebar

tmux new-session -s UserbotSebar

apt install python3.10-venv

python3 -m venv UserbotSebar && source UserbotSebar/bin/activate

pip3 install -U pip && bash installnode.sh && pip3 install -r requirements.txt && npm install -g uglify-js && pip install geopy && pip3 install geopy

sudo apt update && sudo apt install -y libjpeg-dev zlib1g-dev libpng-dev libtiff-dev && pip install --upgrade pip setuptools wheel && pip install speedtest-cli && pip install qrcode

bash start.sh
