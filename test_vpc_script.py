import importlib
import sys
import types
from unittest import mock


def test_vpc_script_send_command_calls():
    mock_conn = mock.MagicMock()

    # Create fake modules for netmiko and paramiko so the script imports succeed
    fake_netmiko = types.ModuleType('netmiko')
    fake_netmiko.ConnectHandler = mock.MagicMock(return_value=mock_conn)
    fake_netmiko.cisco = types.ModuleType('netmiko.cisco')
    fake_netmiko.cisco.CiscoNxosSSH = object
    fake_netmiko.ssh_exception = types.ModuleType('netmiko.ssh_exception')
    fake_netmiko.ssh_exception.NetMikoTimeoutException = Exception
    fake_netmiko.ssh_exception.AuthenticationException = Exception

    fake_paramiko = types.ModuleType('paramiko')
    fake_paramiko.ssh_exception = types.ModuleType('paramiko.ssh_exception')
    fake_paramiko.ssh_exception.SSHException = Exception

    modules = {
        'netmiko': fake_netmiko,
        'netmiko.cisco': fake_netmiko.cisco,
        'netmiko.ssh_exception': fake_netmiko.ssh_exception,
        'paramiko': fake_paramiko,
        'paramiko.ssh_exception': fake_paramiko.ssh_exception,
    }

    with mock.patch.dict(sys.modules, modules), \
         mock.patch('builtins.input') as input_patch, \
         mock.patch('getpass.getpass', return_value='pass'), \
         mock.patch('time.sleep'):
        input_patch.side_effect = [
            '1.1.1.1',  # hostname
            'admin',    # username
            '10',       # vpc_domain_id
            '100',      # system priority
            '200',      # role priority
            '10.0.0.1', # peer keepalive IP
            'no',       # peer-switch
            'no',       # peer-gateway
            'no',       # auto-recovery
            'no',       # create-vlan
            'Ethernet1/1'  # peer-link
        ]
        # Import the script which will execute with patched inputs
        importlib.import_module('script_vpc_config_per_peer')

    # Verify the expected commands were sent
    mock_conn.send_command.assert_any_call('show run vpc')
    mock_conn.send_command.assert_any_call('show run int port-channel 10')

