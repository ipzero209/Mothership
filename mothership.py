#!/usr/bin/python


from threading import Thread
import time
import pexpect
import os
import logging


#####################################################
## FUNCTIONS FOLLOW

#####################################################
## CLEARS SCREEN
#####################################################

def clearScreen():
    """Used to clear the screen"""
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

def writeLog(level,logmsg):
    """Writes a message to the log file."""
    f_name.write("%s: \t%s" % (time.ctime(time.time()), logmsg))

    return

#####################################################
## REBOOTS THE DEVICES
#####################################################

def rebootFW(dev_IP):
    """Reboots the firewall."""
    logging.info('Initiating reboot of %s' % dev_IP)
    device = pexpect.spawn('ssh admin@%s' % dev_IP)
    device.expect('word:')
    device.sendline('admin')
    device.expect('>+')
    device.sendline('request restart system')
    device.expect('continue?')
    time.sleep(1)
    device.sendline('y')
    device.expect('down for reboot NOW')
    device.terminate(True)
    logging.info('Reboot of %s in progress.' % dev_IP)
    return

#####################################################
## SETS DEVICE MANAGEMENT AND PANORAMA IP ADDRESS
#####################################################

def setIP(kvm, index, dev_IP, Pano_IP):
    """Sets the device management and Panorama server IP addresses via console connection
    and commits the changes."""
    logging.info('Setting IP %s on device connected to port %s' % (dev_IP, index))
    device = pexpect.spawn('telnet %s %s' % (kvm, index))
    device.sendline('\n')
    device.expect('ogin:')
    device.sendline('admin')
    device.expect('word:')
    device.sendline('admin')
    device.expect('>+')
    device.sendline('configure')
    # device.expect('[edit]')
    time.sleep(3)
    command = "set deviceconfig system ip-address " + str(dev_IP) + " netmask 255.255.255.0 default-gateway 192.168.1.254"
    device.sendline(command)
    # device.expect('#+')
    time.sleep(3)
    command = "set deviceconfig system panorama-server " + str(Pano_IP)
    device.sendline(command)
    # device.expect('#+')
    time.sleep(3)
    device.sendline('commit')
    time.sleep(5)
    device.sendline('\003')
    device.expect('#+')
    device.sendline('exit')
    device.expect('>+')
    device.sendline('exit')
    logging.info('Mgmt and Panorama IPs added to device %s on port %s. Commit in progress.' % (dev_IP, index))
    device.terminate(True)
    return




#####################################################
## CONTENT DOWNLOAD AND INSTALL
#####################################################

def getContent(dev_IP, content, user, passwd, path):
    """Downloads and installs content in preparation for PAN-OS upgrades."""
    logging.info('Initiating download and installation of content on %s.' % dev_IP)
    device = pexpect.spawn('ssh admin@%s' % str(dev_IP))
    resp = device.expect([pexpect.TIMEOUT, 'yes/no', 'Password:'])
    if resp == 1:
        logging.warning('Adding device %s to script host known_hosts file.' $ dev_IP)
        time.sleep(1)
        device.sendline('yes')
        device.expect('Password:')
        device.sendline('admin')
    if resp == 2:
        device.sendline('admin')
    device.expect('>+')
    device.sendline('scp import content from %s@192.168.1.254:%s/%s' % (user, path, content))
    resp = device.expect([pexpect.TIMEOUT, 'yes/no', 'Password:'])
    if resp == 1:
        logging.warning('Adding script host to known_hosts on %s' % dev_IP)
        time.sleep(1)
        device.sendline('yes')
        device.expect('Password:')
        device.sendline(passwd)
    if resp == 2:
        device.sendline(passwd)
    device.expect('>+')
    device.sendline('request content upgrade install file %s' % content)
    device.expect('>+', timeout=None)
    device.sendline('exit')
    logging.info('Content download complete on %s, install initiated.' % dev_IP)
    device.terminate(True)


#####################################################
## PAN-OS DOWNLOAD
#####################################################

def getpanos(dev_IP, panver, user, passwd, path):
    """Downloads a specified version of PAN-OS and loads it into the
    software repository."""
    logging.info('Initiating download of PAN-OS version %s on %s.' % (panver, dev_IP)
    command = "scp import software from %s@192.168.1.254:%s/%s" % (user, path, panver)
    device = pexpect.spawn('ssh admin@%s' % str(dev_IP))
    resp = device.expect([pexpect.TIMEOUT, 'yes/no', 'word:'])
    if resp == 1:
        logging.warning('Re-adding %s to known_hosts file. This may be a different partition.' % dev_IP)
        time.sleep(1)
        device.sendline('yes')
        device.expect('word:')
        device.sendline('admin')
    elif resp == 2:
        device.sendline('admin')
    else:
        print "No prompt match"
        return
    device.expect('>+')
    device.sendline(command)
    resp = device.expect([pexpect.TIMEOUT, 'yes/no', 'word:'])
    if resp == 1:
        logging.warning('Re-adding script host to device known_hosts file.')
        time.sleep(1)
        device.sendline('yes')
        device.expect('Password:')
        device.sendline(passwd)
    elif resp == 2:
        device.sendline(passwd)
    else:
        print "No prompt match"
        logging.error('Unable to match prompt during download on %s' % dev_IP)
        logging.error('Before: %s' % device.before)
        logging.error(device.read)
        return
    device.expect('>+', timeout=None)
    command = "debug swm load image %s" % panver
    device.sendline(command)
    device.expect('>+', timeout=None)
    logging.info('PAN-OS version %s has been downloaded and added to the software repository on $s' % (panver, dev_IP))
    device.sendline('exit')
    device.terminate(True)


#####################################################
## PAN-OS INSTALL
#####################################################


def instpanos(dev_IP, panver):
    """Installs the specified version of PAN-OS."""
    logging.info('Initiating installaiton of PAN-OS version %s on %s' % (panver, dev_IP))
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
    logging.info('Installation of PAN-OS version %s has started on %s' % (panver, dev_IP))
    device.terminate(True)




## END FUNCTIONS SECTION
#####################################################



logging.basicConfig(filename="mothership.log", format=' %(asctime)s %(levelname)s:\t\t%(message)s', level=logging.DEBUG)

kvm_IP = "192.168.1.253" #raw_input('IP address of the Serial KVM: ')
kvm_Prefix = "60" #raw_input('Enter prefix used by KVM (e.g. 70) ')
num_of_devices = raw_input('How many firewalls do you need to provision? ')
cur_version = raw_input('What version did your firewalls ship with (e.g. 5.0.6 or 6.1.4)')
target_version = raw_input('What version of PAN-OS do you want to move to (ex. 7.1.1)? ')
Pano_IP = raw_input('What is your Panorama IP address? ')

scp_user = raw_input('SCP user name: ')
scp_pass = raw_input('SCP user password: ')
scp_path = "/"
content_ver = raw_input('What is the content file name? ')
dev_count = int(num_of_devices)
versions = {'5.0.6':'6.0.0','6.0.0':'6.1.0','6.1.4':'7.0.1','6.1.0':'7.0.1','7.0.1':'7.1.0'}



dev_list = []

# Build list of device IP addresses
logging.info('Building device IP list.')
i = 1
while i <= dev_count:
    ip_str = '192.168.1.' + str(i)
    dev_list.append(ip_str)
    i += 1

logging.info('Device IP list built.')

# Connect to each device and set mgmt & Panorama IP

p = 1
for fw in dev_list:
    if ( p % 5 ) == 0:
        time.sleep(120)
    i_string = str(p)
    k_index = kvm_Prefix + i_string.zfill(2)
    init_thread = Thread(target=setIP, args=(kvm_IP, k_index, fw, Pano_IP))
    init_thread.start()
    p += 1

logging.info('All init threads started. Allowing time for commit.')
print 'Init threads started. Allowing time for commit.'
time.sleep(300)



# Download and install content in preparation for PAN-OS upgrades

logging.info('Beginning content download and install.')
print 'Beginning content download and install.'

c = 1
for fw in dev_list:
    if ( c % 5 ) == 0:
        time.sleep(60)
    content_thread = Thread(target=getContent, args=(fw, content_ver, scp_user, scp_pass, scp_path))
    content_thread.start()
    c +=1
logging.info('All content threads started. Allowing time for install/commit')
print 'All content threads started. Allowing time for install/commit'

delay()

# Upgrade through required versions to get to target version

while cur_version != target_version:
    if cur_version[0:3] == target_version[0:3]:
        next_ver = target_version
    else:
        next_ver = versions[cur_version]
    d = 1
    for fw in dev_list:
        if ( d % 5 ) == 0:
            delay()
        download_thread = Thread(target=getpanos, args=(fw, next_ver, scp_user, scp_pass, scp_path))
        download_thread.start()
    logging.info('Pausing for 10 minutes to allow for downloads of %s to complete.' % next_ver)
    time.sleep(600)
    for fw in dev_list:
        upgrade_thread = Thread(target=instpanos, args=(fw, next_ver))
        upgrade_thread.start()
    logging.info('Pausing for 10 minutes to allow for installation of %s to complete.' % next_ver)
    time.sleep(600)
    for fw in dev_list:
        reboot_thread = Thread(target=rebootFW, args=(fw,))
        reboot_thread.start()
    logging.info('Pausing for 20 minutes to allow for reboot of all devices.')
    time.sleep(1200)
    cur_version = next_ver


print "DONE!!"
logging.info('UPGRADES COMPLETE')
