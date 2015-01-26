#!/bin/bash
sudo pkill gunicorn
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start bizcuits
