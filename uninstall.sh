#!/bin/bash

INSTALLATION_PATH=$HOME
SYSTEMD_PATH="/etc/systemd/user"


systemctl --user disable citaGym.timer
systemctl --user disable citaGym.service
systemctl --user stop citaGym.service
systemctl --user stop citaGym.timer

if test -f $SYSTEMD_PATH/citaGym.service; then
        echo "citaGym.service found"
        sudo rm $SYSTEMD_PATH/citaGym.service
else
        echo "citaGym.service not found"
fi
if test -f $SYSTEMD_PATH/citaGym.timer; then
        echo "citaGym.timer found"
        sudo rm $SYSTEMD_PATH/citaGym.timer
else
        echo "citaGym.timer not found"
fi

systemctl --user daemon-reload

if [ -d $INSTALLATION_PATH"/CitaGym" ]; then
        echo "CitaGym directory found"
        rm -rf $INSTALLATION_PATH/CitaGym
else
        echo "CitaGym directory not found"
fi


