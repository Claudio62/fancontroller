# fancontroller
Small python script to manage fan controller on Raspberry cpu

fancontrol.py have to be inserted in /usr/local/bin/
fancontrol.sh have to be inserted in /etc/init.d/

set execution proprerties +x for both files

to insert in the process launched at startup:
  sudo update-rc.d /etc/init.d/fancontrol.sh default

to launch manually : 
  sudo /etc/init.d/fancontrol.sh start | stop
or:
  python3 fancontrol.py -v 

