from aws_cdk import (
    aws_ec2 as ec2,
    Stack
)
from constructs import Construct

class EC2AppStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the VPC with public subnets and unique CIDR blocks
        vpc = ec2.Vpc(
            self, "MyVpc",
            max_azs=2,
            cidr="10.1.0.0/16",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                )
            ]
        )

        # Define the Amazon Linux AMI
        ami = ec2.MachineImage.latest_amazon_linux()

        # Create a Security Group
        security_group = ec2.SecurityGroup(
            self, 'SecurityGroup',
            vpc=vpc,
            description='Allow SSH and HTTP traffic',
            allow_all_outbound=True
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(22),
            'Allow SSH access from anywhere'
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            'Allow HTTP traffic from anywhere'
        )

        # Create the EC2 instance
        instance = ec2.Instance(
            self, 'Instance',
            instance_type=ec2.InstanceType('t2.micro'),
            machine_image=ami,
            vpc=vpc,
            security_group=security_group,
            key_name='TestCapstone-key',  # Replace with your key pair name
            vpc_subnets={"subnet_type": ec2.SubnetType.PUBLIC},  # Ensure it's in a public subnet
            user_data=ec2.UserData.custom(
                """
                #!/bin/bash
                yum update -y
                yum install -y python3 python3-pip
                pip3 install flask
                echo "from flask import Flask" > /home/ec2-user/app.py
                echo "app = Flask(__name__)" >> /home/ec2-user/app.py
                echo "@app.route('/')" >> /home/ec2-user/app.py
                echo "def home():" >> /home/ec2-user/app.py
                echo "    return 'Hello, World!'" >> /home/ec2-user/app.py
                echo "if __name__ == '__main__':" >> /home/ec2-user/app.py
                echo "    app.run(host='0.0.0.0', port=5000)" >> /home/ec2-user/app.py
                python3 /home/ec2-user/app.py
                """
            )
        )
