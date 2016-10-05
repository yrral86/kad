# Knowledge Advantage Desktop

Find stuff -> mark it up -> link it together -> look at it

## Installation

It should be possible to run KAD on any recent Linux system, but the easiest way to get started is with an Ubunutu 16.04 VM.

1. Install VirtualBox (https://www.virtualbox.org/wiki/Downloads)
2. Create a new Linux VM and mount the Ubuntu 16.04 ISO (http://releases.ubuntu.com/16.04/ubuntu-16.04.1-desktop-amd64.iso)
3. Boot up the VM and install Ubuntu
4. Add the Gnome-3 staging PPA and upgrade your system (https://launchpad.net/~gnome3-team/+archive/ubuntu/gnome3-staging)

   ```
sudo add-apt-repository ppa:gnome3-team/gnome3-staging
sudo apt-get update
sudo apt-get upgrade
   ```

5. Install a few additional dependencies

   ```
sudo apt-get install libevince lynx python-gi python-networkx
   ```

Now, you should be ready to run KAD.  Execute kad.py to get started.

## Keyboard Shortcuts

KAD has a few built-in keyboard shortcuts that will help you use it.

* Control-Q: Quit KAD
* Control-L: Focus the location bar
* Control-S: Save the file currently being edited
* Control-R: Reload KAD (useful if you have edited the KAD source code)
