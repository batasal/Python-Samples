from netmiko import ConnectHandler
from netmiko.cisco import CiscoNxosSSH
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException
from getpass import getpass
import paramiko
import time

hostname = input('\n Enter the hostname or ip address of vPC peer you want to configure: \n\n')
username = input('\n Enter the username to login to the device: \n\n')
password = getpass()


N9K = {
'ip':   hostname,
'username': username,
'password': password ,
'device_type': 'cisco_nxos',
}
print ('\n #### Connecting to the '  + hostname + ' ' + '#### \n' )

try:
    net_connect = ConnectHandler(**N9K)
except NetMikoTimeoutException:
    print ('\n #### Device not reachable #### \n')
    #continue
except AuthenticationException:
    print ('\n #### Authentication Failure #### \n')
    #continue
except SSHException:
    print ('\n #### Check to see if SSH is enabled on device #### \n')
    #continue

print ('\n #### Connection successfull, enabling vPC related related features... #### \n')

vpc_features = ['feature vpc',
                'feature lacp',
                'feature interface-vlan']
net_connect.send_config_set(vpc_features)
output = net_connect.send_command('show feature | i enable')
print(output)
time.sleep(2)

print('\n #### Features enabled successfully, creating vPC domain... #### \n')
time.sleep(2)

vpc_domain_id = input('\n #### Please enter vPC domain ID to be created: #### \n\n')
vpc_system_priority = input('\n #### Please enter a System Priority value to be assigned: ####\n\n')
vpc_role_priority = input('\n #### Please enter a Role Priority value to be assigned: #### \n\n')

vpc_domain_config = ['vpc domain' + ' ' + str(vpc_domain_id),
                        'system-priority' + ' ' + str(vpc_system_priority),
                        'role priority' + ' ' + str(vpc_role_priority),
                        ]
net_connect.send_config_set(vpc_domain_config)

peer_keepalive_ip = input("\n #### Please enter the peer's ip address to be used as 'peer-keepalive destination': #### \n\n")
peer_keepalive_config = ['vpc domain' + ' ' + str(vpc_domain_id),
                            'peer-keepalive destination' +' '+ str(peer_keepalive_ip) + ' ' + 'vrf management']
net_connect.send_config_set(peer_keepalive_config)
time.sleep(2)

peer_switch = input("\n #### Would you like to enable 'peer-switch'? (yes/no): #### \n\n" )
if peer_switch == 'yes':
    print('\n #### Enabling peer-switch... #### \n')
    time.sleep(2)
    peer_switch_config = ['vpc domain' + ' ' + str(vpc_domain_id),
                            'peer-switch']
    net_connect.send_config_set(peer_switch_config)

else:
    print('\n #### peer-switch is NOT enabled #### \n')
    time.sleep(2)

peer_gateway = input("\n #### Would you like to enable 'peer-gateway'? (yes/no): #### \n\n" )
if peer_gateway == 'yes':
    print('\n #### Enabling peer-gateway... #### \n')
    time.sleep(2)
    peer_gateway_config = ['vpc domain' + ' ' + str(vpc_domain_id),
                            'peer-gateway']
    net_connect.send_config_set(peer_gateway_config)

else:
    print('\n #### peer-gateway is NOT enabled #### \n')
    time.sleep(2)

auto_recovery = input("\n #### Would you like to enable 'auto-recovery'? (yes/no): #### \n\n")
if auto_recovery == 'yes':
    print('\n #### Enabling auto-recovery with default timer (240sec)... #### \n')
    time.sleep(2)
    auto_recover_config = ['vpc domain' + ' ' + str(vpc_domain_id),
                            'auto-recovery']
    net_connect.send_config_set(auto_recover_config)
else:
    print('\n #### auto-recovery is NOT enabled #### \n')
    time.sleep(2)

create_vlan = input("\n #### Would you like to create any VLANs now? (yes/no): #### \n\n")
if create_vlan == 'yes':
    vlan_list = input('\n #### Please enter the VLAN IDs you want to create (eg. 10-20 or 10,20): #### \n\n')
    vlan_config = ['vlan' +' '+ str(vlan_list)]
    net_connect.send_config_set(vlan_config)
    print('\n #### VLANs are created #### \n')
    time.sleep(3)
else:
    print('\n #### No VLANs are created #### \n')
    time.sleep(2)

peer_link = input ("\n #### Please enter the interfaces to be configured as 'peer-link' (eg. eth1/1, eth 1/2): #### \n\n" )
peer_link_config = ['interface ' + ' ' + str(peer_link),
                    'switchport',
                    'description vPC_Peer_Link_Members',
                    'switchport mode trunk',
                    'no shutdown',
                    'channel-group' +' '+ str(vpc_domain_id),
                    'interface port-channel' +' '+ str(vpc_domain_id),
                    'description vPC_Peer_Link',
                    'vpc peer-link']
net_connect.send_config_set(peer_link_config)
time.sleep(5)
print('\n #### vPC Peer-Link created #### \n')
time.sleep(5)
print('\n #### vPC Configuration on this peer is completed successfully... The configuration done so far: #### \n')
time.sleep(5)
config_done = ['show run vpc',
                'show run int port-channel ' + str(vpc_domain_id)]
for command in config_done:
    output = net_connect.send_command(command)
    print(output)
time.sleep(5)

print("\n #### Let's see the status of peer-keepalive link #### \n")
time.sleep(5)
output = net_connect.send_command('show vpc peer-keepalive')
print(output)
time.sleep(5)

print("\n #### Let's see the status of vPC domain #### \n")
time.sleep(5)
output = net_connect.send_command('show vpc')
print(output)
time.sleep(5)

print('\n #### Saving configuration... #### \n')
net_connect.save_config()
