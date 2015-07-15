# urban_sensing
Urban sensing class team project

### Team
- Emil Christensen
- Eduardo Franco
- Juan Medina
- Peter Varshavsky

# Notes on RPi setup

### SSH Agent forwarding
Add this to your `~/.ssh/config` to forward your SSH Agent to your RPi. This allows you to ssh into GitHub and other servers using your laptop's private keys without storing them on RPi.

```bash
# Raspberry Pi ssh Agent forwarding
Host <raspberry_pi_IP_address>
   ForwardAgent yes
```
More info in this [GitHub guide](https://developer.github.com/guides/using-ssh-agent-forwarding/)

### Running a Python script on startup
This [instructable](http://www.instructables.com/id/Raspberry-Pi-Launch-Python-script-on-startup/?ALLSTEPS) goes over setting up a startup shell script to launch a python script and setting up a cron job to launch the shell script.

In my case the launcher script for `capture.py` is

```bash
#!/bin/sh
# rat_launch.sh
cd /home/pi/projects/rats/code
sudo python capture.py
cd /home/pi/logs
```

it drops me off in the `~/logs` directory.
