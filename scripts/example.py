import json
import yaml
import paramiko
import time
from netmiko import ConnectHandler

json_path = '/Users/fernando/Desktop/Alvaro/Personal/Study-Guides-Cert/Cisco/Python-Labs/CiscoTest/resources' \
            '/questions.json'

with open(json_path, 'r') as f:
    questions = json.load(f)  # convert a JSON file to Python Object ( List of Dictionnaries)


for item in questions:
    print('************ DICTIONNARY to JSON **************')
    print(json.dumps(item, indent=4)) # convert a Python Dictionnary to JSON string and print in json format
    a = json.dumps(item, indent=4)
    print('************     DICTIONNARY to YAML    **************')
    print(yaml.dump(item, indent=4, sort_keys=False)) # convert Python Dictionnary to YAML string and print YAML format
    break

# Path to save output files
path = '/Users/fernando/Desktop/Alvaro/Personal/Study-Guides-Cert/Network Automation/LABS/Network_Inventory/outputs/'

with open (f'{path}data.yaml', 'w') as file:
    yaml.dump(questions, file, sort_keys=False)

a = {"name": "Diana", "age": 37, "country": "Ecuador"}
# a_json_str = json.dumps(a, indent=4)
# print(a_json_str)

b_yaml = yaml.dump(a, indent=4, sort_keys=False)
print(b_yaml)


# -----------Using PARAMIKO ----------------------- #
# Create SSH Client
client = paramiko.SSHClient()

# Set Policy to automatically add host to known host file
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect to the remote host
client.connect(
    hostname="10.10.20.31",
    username="alvaro",
    password="2LNN%6^l2*bpa",
    look_for_keys=False,
    allow_agent=False,
)

# Open an interactive SSH session
ssh_client = client.invoke_shell()

# Send command
ssh_client.send("sh ip int brief\n")

# Wait for the command to be finished
time.sleep(3)

# Receive and process command output
output = ssh_client.recv(65000)
print(output.decode("ascii"))

# Create Loopback interface
print(" ########## Create Loopback Interface ###########")
ssh_client.send("ena\n")
ssh_client.send("C1sco12345\n")
ssh_client.send("conf ter\n")

for item in range(0, 1):
    ssh_client.send(f"int lo {item}\n")
    ssh_client.send(f"ip add 1.1.1.{item} 255.255.255.255\n")

time.sleep(1)

ssh_client.send("end\n")
ssh_client.send("sh ip int brief\n")

time.sleep(3)
output = ssh_client.recv(65000)
print(output.decode("ascii"))


# Close the SSH session
ssh_client.close()

# Close the connection
client.close()


# -------------------Using NETMIKO ----------------------- #

# Create device inventory in a dictionary
SW_01 = {
    "device_type": "cisco_ios",
    "host": "10.10.20.31",
    "username": "alvaro",
    "password": "2LNN%6^l2*bpa",
    "secret": "C1sco12345"
}

# Unpacking the dictionnary to connect device
connection = ConnectHandler(**SW_01)
connection.enable() #Enable method
connection.config_mode() #Global config mode

config_commands = ['ip access-list extended TEST', 'permit tcp any any eq www', 'permit tcp host 10.1.1.5 any eq ssh', 'exit', 'int lo 0', 'ip access-group TEST in', 'exit']
connection.send_config_set(config_commands)

connection.exit_config_mode()
connection.send_command('wr')
show_output = connection.send_command('sh run int l0')
print(show_output)

# close connection
connection.disconnect()
