# -*- coding: utf-8 -*-

import time 
from boto import ec2


KEY_PAIR_NAME = 'key_pair'
GROUP_NAME = 'csc326-group41'
DISCRIPTION = 'The host created by Zhaoqing Xu for my CSC326 Lab'

AMI_ID = 'ami-8caa1ce4'
INSTANCE_TYPE = 't1.micro'

print "begin launching an instance"

'''
Get the aws_access_key_id and aws_secret_access_key from .csv file
'''
try:
    with open("accessKeys.csv") as f:
        info = f.readlines()
        info = info[1].split(',')
except:
    print "I intentionally remove the accessKeys for safety"

aws_access_key_id = info[0].strip()
aws_secret_access_key = info[1].strip()

# Step 1: Establish connection to region “us-east-1” along with aws_access_key_id and aws_secret_access_key
conn = ec2.connect_to_region('us-east-1', aws_access_key_id=aws_access_key_id, 
		aws_secret_access_key=aws_secret_access_key)

'''
Step 2:
    Create Key-Pair with boto.ec2.connection.create_key_pair(), which returns a key-pair object, boto.ec2.keypair.KeyPair. 
    The key must be save as a .pem key file using boto.ec2.keypair.KeyPair.save(<directory>). The .pem key file is needed for SSH the new instances. 
'''

try:
    key_pair = conn.create_key_pair(KEY_PAIR_NAME)
except:
    conn.delete_key_pair(KEY_PAIR_NAME)
    key_pair = conn.create_key_pair(KEY_PAIR_NAME)
key_pair.save("")

'''
Step 3:
    Create a security group with boto.ec2.connection.create_security_group(), which returns an instance of boto.ec2.securitygroup.SecurityGroup. 
    Security group provides restricted access only from authorized IP address and ports. For more details, see See http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-network-security.html 
'''

group = conn.create_security_group(GROUP_NAME, DISCRIPTION)


'''
Step 4:
    Authorize following protocols and ports forthe security group created in step 3: 
        4.1.To ping the server, enable protocol: ICMP, from port: -1, to port: -1, CIDR  IP 0.0.0.0/0 
        4.2.To allow SSH, enableprotocol: TCP, from port: 22, to port: 22, CIDR  IP 0.0.0.0/0 
        4.3.To allow HTTP, enableprotocol: TCP, from port: 80, to port: 80, CIDR  IP 0.0.0.0/0
'''

group.authorize("icmp", -1, -1, "0.0.0.0/0")
group.authorize('tcp', 22, 22, "0.0.0.0/0")
group.authorize('tcp', 80, 80, "0.0.0.0/0")

'''
Step 5:
    Start a new instance with boto.ec2.connection.run_instance(). 
    To find Amazon Machine Image (AMI) IDs of Ubuntu server images in various regions, please see http://cloud-images.ubuntu.com/releases/14.04.1/release-20140927Make sure the property of the selected image matches the instance type and region of your selection. For the specification of different EC2 instance types, see http://aws.amazon.com/ec2/instance-types. 
    Note that for the purpose of this lab, it is sufficient that you use the Micro Instance with the free tier usage. 
'''

resp = conn.run_instances(AMI_ID, instance_type = INSTANCE_TYPE, key_name = KEY_PAIR_NAME, security_groups=[group])

'''
Step 6:
    Step 5 returns a reservation object, which contains a list of instances newly create. 
    States of the instance can be retrieved as variable of boto.ec2.instance.Instance. 
'''

inst = resp.instances[0]

'''
Step 7:
    Once the state of the instance is changedto "running", you can access your instance with the key-pair generated in step 1 with the following command:
    $   ssh -i key_pair.pem ubuntu@<PUBLIC-IP-ADDRESS>
    Note that the default user name for the Ubuntu AMIs is "ubuntu". 
    The public IP address of the instance can be found with boto.ec2.instance.Instance.ip_addre
'''
print "Please wait for the instance to run"
while(inst.update() != "running"):
    time.sleep(5)

print "Instance is now running"
print "Instance ID is: %s" % inst.id
print "Instance Public IP address is: %s" % inst.ip_address



