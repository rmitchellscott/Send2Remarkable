#!/bin/sh
echo "Welcome to Send2Remarkable. Lets get you set up!"
rmapi cd
if [ $? -eq 0 ]
then
    echo "Printing your rmapi.conf file:"
    cat /root/.config/rmapi/rmapi.conf
fi