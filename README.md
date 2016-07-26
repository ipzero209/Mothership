# Mothership

Purpose: Provision mulitiple Palo Alto Networks firewalls via serial console server and SSH. This version can be considered a development version, initial testing has been completed. This works as-is. Future features have not been tested.


Requirements: 

	1. Network switch with all ports on the same VLAN. Needs to have the same number of ports as the serial console server (at minimum).
	2. Serial console server.
	3. Linux host with content and all required PAN-OS images. Host needs to have Python 2.7 (included in most modern distros) with the pexpect module.



Script Setup:

	1. Configure ethernet on Linux host with IP address 192.168.1.254.
	2. Configure serial console server with IP address 192.168.1.253.
	3. Ensure all ports on networks switch are on the same VLAN, there is no need for a management IP address on the switch.
	4. Connect both the Linux host and the serial console server to the network switch and ensure that the two can communicate on the 192.168.1.0/24 subnet.
	5. Download the latest content update. Content should be apps only (panupv2-all-apps-xxx-xxxx). Save this in the directory you will be running the script from using only the version number for the name (e.g. 581-3295).
	6. Download all required PAN-OS versions (for upgrade path see https://live.paloaltonetworks.com/t5/Management-Articles/How-to-Upgrade-PAN-OS-and-Panorama/ta-p/58700)
	7. Save PAN-OS images using the version as the filename (e.g. 6.0.0) in the directory from which the scritp will be run.
	8. By default, the script will prompt you for several pieces of information. You can edit the script to assign values to these variables directly.

Physical Setup:

	1. Connect the console port of each firewall to a port on the console server. IP addresses will be assigned by the script to each firewall in the following manner:
			console server port		IP Address
			1		192.168.1.1
			2		192.168.1.2
			3		192.168.1.3
			4		192.168.1.4
			etc		
	2. Connect the management port of each firewall to a port on the network switch.


Coming Soon:

	1. Read and configure final IP address / partial configuration after completion of upgrade.
	2. Threading improvements.
