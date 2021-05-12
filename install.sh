#!/bin/bash

chmod +x ./uninstall.sh
INSTALLATION_PATH=$HOME
SYSTEMD_PATH="/etc/systemd/user"

if command -v pip >/dev/null 2>&1 ; then
        echo "Pip found"
        echo "version: $(pip -v)"
else
        sudo apt-get install python3-pip
fi

if python -c "import pipreqs" &> /dev/null; then
    echo "Pipreqs found"
else
    pip install pipreqs
fi
if dpkg-query -W -f'${db:Status-Abbrev}\n' 'firefox' 2>/dev/null \
 | grep -q '^.i $'; then
    echo "Firefox found"
else
    sudo apt-get install firefox
fi

if dpkg-query -W -f'${db:Status-Abbrev}\n' 'firefox-geckodriver' 2>/dev/null \
 | grep -q '^.i $'; then
    echo "Firefox geckodriver found"
else
    sudo apt-get install firefox-geckodriver
fi

pipreqs --force ./src
mv ./src/requirements.txt ./requirements.txt
pip install -r ./requirements.txt

if [ ! -d $INSTALLATION_PATH"/CitaGym" ]; then
        echo $INSTALLATION_PATH"/CitaGym directory doesn't exists, so we're gonna create it"
        mkdir $INSTALLATION_PATH/CitaGym
fi
cp -r ./src $INSTALLATION_PATH/CitaGym/src/
cp ./service/citaGym.sh $INSTALLATION_PATH/CitaGym/citaGym.sh
chmod +x $INSTALLATION_PATH/CitaGym/citaGym.sh

if test -f $SYSTEMD_PATH/citaGym.service; then
        echo "citaGym.service found"
else
        sudo cp ./service/citaGym.service $SYSTEMD_PATH/citaGym.service
fi
if test -f /etc/systemd/system/citaGym.timer; then
        echo "citaGym.timer found"
else
        sudo cp ./service/citaGym.timer $SYSTEMD_PATH/citaGym.timer
fi
systemctl --user daemon-reload
systemctl --user start citaGym.service
systemctl --user enable citaGym.timer
systemctl --user start citaGym.timer