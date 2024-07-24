from aws_cdk import App
from ec2_app_stack import EC2AppStack

app = App()
EC2AppStack(app, "ec2-app-stack")
app.synth()
