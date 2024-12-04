from infrastructure import logging
import aws_cdk as cdk

app = cdk.App()
logging.Logging(app, "logging")
app.synth()
