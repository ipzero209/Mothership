#!/usr/bin/python


from threading import Thread
import time
import pexpect
import os


#####################################################
## FUNCTIONS FOLLOW

#####################################################
## CLEARS SCREEN
#####################################################

def clearScreen():
    "Used to clear the screen"
    os.system('cls' if os.name == 'nt' else 'clear')
    return


#####################################################
## DELAY FOR BETWEEN OPERATIONS
#####################################################

def delay():
    """Sets a standard delay time to allow devices to complete their previous task."""
    time.sleep(300)
    return


#####################################################
## WRITES TO THE LOG FILE
#####################################################

def writeLog(f_name,logmsg):
    """Writes a message to the log file."""
    f_name.write("%s: \t%s" % (time.ctime(time.time())), logmsg)
    return

#####################################################
## REBOOTS THE DEVICES
#####################################################

def rebootFW(fw_IP):
    """Reboots the firewall."""
    logstr = "Interfacing with " + str(fw_IP)
    writeLog(logfile, logstr)
    device = pexpect.spawn('ssh admin@%s' % fw_IP)
    device.expect('word:')
    device.sendline('admin')
    device.expect('>+')
    device.sendline('request restart system')
    device.expect('continue?')
    time.sleep(1)
    device.sendline('y')
    device.expect('>+')
    device.sendline('exit')
    logstr = "Reboot of " + str(fw_IP) + " completed."
    writeLog(logfile, logstr)
    return

#####################################################
## SETS DEVICE MANAGEMENT AND PANORAMA IP ADDRESS
#####################################################

def setIP(kvm, index, dev_IP, Pano_IP):
    """Sets the device management and Panorama server IP addresses via console connection
    and commits the changes."""
    logstr = "Setting IP " + str(dev_IP) + " on device connected to port " + str(index)
    writeLog(logfile, logstr)
    device = pexpect.spawn('telnet admin@%s:%s' % (kvm, index))
    device.expect('word:')
    device.sendline('admin')
    device.expect('>+')
    device.sendline('configure')
    device.expect('#+')
    command = "set deviceconfig system ip-address " + str(dev_IP) + " netmask 255.255.255.0 default-gateway 192.168.1.254"
    device.sendline(command)
    device.expect('#+')
    command = "set deviceconfig system panorama-server " + str(Pano_IP)
    device.sendline(command)
    device.expect('#+')
    device.sendline('commit')
    device.sendline('\003')
    logstr = "Mgmt and Panorama IPs added for device on port " + str(index) + ". Commit in progress."
    writeLog(logfile, logstr)
    time.sleep(60)
    device.terminate(True)
    return



#####################################################
## GET DEVICE CERTIFICATES
#####################################################

def get_certs(dev_IP, user, passwd):
    """Initial connection to get certs into known_hosts files so that we don't need to account for fingerprint
    warnings every time we connect."""
    logstr = "Connecting to " + str(dev_IP)
    writeLog(logfile, logstr)
    device = pexpect.spawn('ssh admin@%s' % dev_IP)
    device.expect('connecting')
    time.sleep(1)
    device.sendline('yes')
    device.expect('word:')
    device.sendline('admin')
    device.expect('>+')
    device.sendline('scp export configuration from running-config.xml to %s@192.168.1.254:/' % user)
    device.expect('connecting')
    time.sleep(1)
    device.sendline('yes')
    device.expect('word:')
    device.sendline(passwd)
    device.expect('>+')
    device.sendline('exit')
    logstr = "Certificate for " + str(dev_IP) + " added to ~/.ssh/known_hosts"
    writeLog(logfile, logstr)
    device.terminate(True)

#####################################################
## CONTENT DOWNLOAD AND INSTALL
#####################################################

def getContent(dev_IP, content, user, passwd, path):
    """Downloads and installs content in preparation for PAN-OS upgrades."""
    writeLog(logfile, "Initiating download an install of content on %s" % dev_IP)
    device = pexpect.spawn('ssh admin@%s' % str(dev_IP))
    device.expect('word:')
    device.sendline('admin')
    device.expect('>+')
    device.sendline('scp import content from %s@192.168.1.254:%s%s' % (user, path, content))
    device.expect('word:')
    device.sendline(passwd)
    device.expect('>+')
    device.sendline('request content upgrade install file %s' % content)
    device.expect('>+')
    device.sendline('exit')
    writeLog(logfile, "Content download and install complete for %s" % )
    device.terminate(True)



#####################################################
## PAN-OS DOWNLOAD
#####################################################

def getpanos(dev_IP, panver, user, passwd):
    """Downloads a specified version of PAN-OS and loads it into the
    software repository."""
    logstr = "Initiating download of PAN-OS version " + str(panver)
    writeLog(logfile, logstr)
    command = "scp import software from %s@192.168.1.1:/%s" % (user, panver)
    device = pexpect.spawn('ssh admin@%s' % str(dev_IP))
    device.expect('word:')
    device.sendline('admin')
    device.expect('>+')
    device.sendline(command)
    device.expect('word:')
    device.sendline(passwd)
    device.expect('>+', timeout=None)
    command = "debug swm load image %s" % panver
    device.sendline(command)
    device.expect('>+', timeout=None)
    logstr = "PAN-OS version " + str(panver) + " has been downloaded and loaded into the repository on " + str(dev_IP)
    writeLog(logfile, logstr)
    device.sendline('exit')
    device.terminate(True)


#####################################################
## PAN-OS INSTALL
#####################################################


def instpanos(dev_IP, panver):
    """Installs the specified version of PAN-OS."""
    logstr = "Initiating installation of PAN-OS version " + str(panver) + " on " + str(dev_IP)
    writeLog(logfile, logstr)
    device = pexpect.spawn('ssh admin@%s' % dev_IP)
    device.expect('word:')
    device.sendline('admin')
    device.expect('>+')
    device.sendline('request system software install version %s' % panver)
    device.expect('continue')
    time.sleep(1)
    device.sendline('y')
    device.expect('>+')
    device.sendline('exit')
    writeLog('Installation of PAN-OS version %s started for %s' % (panver, dev_IP))
    device.terminate(True)




## END FUNCTIONS SECTION
#####################################################


logfile = open('hivelog.txt', 'w+')


kvm_IP = raw_input('IP address of the Serial KVM: ')
kvm_Prefix = raw_input('Enter prefix used by KVM (e.g. 70) ')
num_of_devices = raw_input('How many firewalls do you need to provision? ')
cur_version = raw_input('What version did your firewalls ship with (e.g. 5.0.6 or 6.1.4)')
target_version = raw_input('What version of PAN-OS do you want to move to (ex. 7.1.1)? ')
Pano_IP = raw_input('What is your Panorama IP address? ')

scp_user = raw_input('SCP user name: ')
scp_pass = raw_input('SCP user password: ')
scp_path = "/home/cstancill/"
content_ver = raw_input('What is the content file name? ')
dev_count = num_of_devices
versions = {'5.0.6':'6.0.0','6.0.0':'6.1.0','6.1.4':'7.0.1''6.1.0':'7.0.1','7.0.1':'7.1.0'}



dev_list = []


# Build list of device IP addresses
i = 1
while i <= dev_count:
    ip_str = '192.168.1.' + str(list_count)
    dev_list.append(ip_str)
    i += 1


# Connect to each device and set mgmt & Panorama IP
p = 1
while p <= dev_count:
    if ( p % 5 ) = 0:
        time.sleep(120)
    i_string = str(p)
    k_index = str(kvm_IP) + i_string.zfill(2)
    init_thread = Thread(target=setIP, args=(kvm_IP, k_index, dev_list[p-1], Pano_IP))
    p += 1

delay()

# Add devices to script host known_hosts file, add script host cert to device known_hosts file

f = 1
for fw in dev_list:
    if ( f % 5 ) = 0:
        time.sleep(10)
    cert_thread = Thread(target=get_certs, args=(dev_list(fw), scp_user, scp_pass))
    f += 1

# Download and install content in preparation for PAN-OS upgrades

c = 1
for fw in dev_list:
    if ( c % 5 ) = 0:
        time.sleep(60)
    content_thread = Thread(target=getContent, args=(dev_list(fw), content_ver, scp_user, scp_pass, scp_path))
    c +=1

delay()

# Upgrade through required versions to get to target version

while cur_version != target_version:
    if cur_version[0:2] == target_version[0:2]:
        next_ver = target_version
    else:
        next_ver = versions(cur_version)
    for fw in dev_list:
        upgrade_thread = Thread(target=instpanos, args=(dev_list(fw), next_ver))
    time.sleep(600)
    for fw in dev_list:
        reboot_thread = Thread(target=rebootFW, args=dev_list(fw))
    time.sleep(1200)
    cur_version = next_ver
