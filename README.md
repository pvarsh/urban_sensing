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

### Ethernet and Wireless setup
To SSH into Raspberry Pi you need to know its IP address. By default your router probably assigns IP addresses of its choice to Ethernet and WiFi devices. This [instructable step](http://www.instructables.com/id/Ultimate-Raspberry-Pi-Configuration-Guide/step11/Assigning-a-static-IP/) shows how to set up static IP to connect to your router with Ethernet.

These two docs helped me set up static IP WiFi. Very useful to SSH into Raspberry Pi from a machine on the same network:

- https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md
- http://weworkweplay.com/play/automatically-connect-a-raspberry-pi-to-a-wifi-network/

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

### Color git output
`git config --global color.ui auto`

### Vim

##### Install vim (so much better than vi)
From this text editors [doc](https://www.raspberrypi.org/documentation/linux/usage/text-editors.md):
`sudo apt-get install vim`

##### Vim configuration
This [gist](https://gist.github.com/pvarsh/4e8a9c2bb1ef8d361894) has my `.vimrc` file. Place it in your `home` folder to automatically set vim to highlight syntax, set tab to 4 spaces and convert tabs to spaces. It also highlights lines longer than 79 characters to keep you PEP8 compliant.

##### Make vim your default text editor
Run `sudo update-alternatives --config editor` and follow the prompts.
