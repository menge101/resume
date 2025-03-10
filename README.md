# Resume
This project is home to my digital resume and its related components

## Purpose
The primary purpose of this project is to explore [HTMX](https://htmx.org/) and use it to build a 
functional web site of some form. A digital resume was chosen to drive requirements and design goals.

## Technology
- [HTMX](https://htmx.org/) is used to enable interactivity in the UI.
- [Python](https://www.python.org/) the backend is written in Python.  
- [AWS](https://aws.amazon.com/) The infrastructure behind this project is part of Amazon Web Services.
  - IAM  
  - Route 53
  - Lambda
  - DynamoDB
  - S3
  - Amazon Translate
  - Event Bridge
  - Cloud Front
  - AWS Certificate Manager
  - AWS CDK

### [IAM](https://aws.amazon.com/iam/) (Identity and Access Management)
This project uses IAM for authorization Roles and Policies; which is essential and required within AWS.

### [Route 53](https://aws.amazon.com/route53/)
The domain name's nameservers are on Route 53, as well as the Hosted Zone that connects the domain name to Cloudfront.

### [Lambda](https://aws.amazon.com/pm/lambda/)
The backend is implemented as a single lambda which parses the request and dispatches to the specific code unit based on the request URL.  

Dispatchable components are implemented as a protocol that requires an act function to parse the request and handle any state changes, and a build function that builds the component by applying the state to the component template, returning valid HTML.

### [DynamoDB](https://aws.amazon.com/pm/dynamodb/)
DynamoDB holds all the queryable data in the system.  That is strongs for the translations, session information, and system information.

### [S3](https://aws.amazon.com/s3/) (Simple Storage Solution)
S3 is home to the static web content, the raw input and output files from translation, and CDK deploy artifacts.

### [Amazon Translate](https://aws.amazon.com/translate/)
Translations have been created by submitting the English language strings into Amazon Translate, then the resulting translated strings are written to a different S3 bucket when processing is complete.

### [Event Bridge](https://aws.amazon.com/eventbridge/)
Event Bridge rules are used to identify when an Amazon Translate job completes successfully.  Which is used to trigger a lambda function that reads the translations S3 bucket, identifies what translations are available and updates the system information in DynamoDB so that the web app has the new language available with no change in configuration needed.

### [Cloud Front](https://aws.amazon.com/cloudfront/)
Cloud Front is used as the "front door" for the application.  Static content from S3 is accesible through the S3 origin, and the dynamic data from Lambda is accessible through the lambda origin.  All of which map to the same DNS name, preventing any need for CORS.

### [AWS Certificate Manager](https://aws.amazon.com/certificate-manager/)
ACM is used with Route 53 to provide HTTPS through the hosted domain name.

### [Cloud Development Kit](https://aws.amazon.com/cdk/)
CDK is used to provision and configure the infrastructure used by this project.  CDK is an "infrastructure-as-code" tool, that generates Cloud Formation templates from python code.
  
## Components/Stacks  
There are five stacks in the [infrastructure directory](./infrastructure) that comprise the complete system.
- Web  
- Translation
- Github integration
- Hosted Zone
- Logging

### Web
This stack builds the following things:  
- the lambda function that powers the backend  
- the S3 bucket to hold the static web files  
- the DynamoDB table to hold the dynamic content, session data, and system data    
- the Cloud Front distribution  
- the Cloud Front origins that associate the S3 bucket and lambda function to the distribution  
- a "Bucket Deployment" which is a deployment convenience to sync a folder in the code repo ("src") with the S3 bucket  
- if a "domain_name" was specified in the constructor, then a Certificate is created for that domain and is associated with the Cloud Front distribution (this is only intended to be used for production deploys)
- and finally all the roles, policies, and principals to authorize these components to work together

### Translation
This stack builds the following things:
- S3 bucket for translation source data
- S3 bucket for translation destination data (e.g. the resulting translated strings)
- the lambda function to parse the translation files, connect them to the appropriate keys and store then in the DynamoDB table
- the Event Bus rule to respond to aws.translate success events, which triggers the above lambda function

### Github Integration
This stack builds the following things:
- An Open ID Connect Provider - which provides identity federation from github, allowing the Github Actions CI/CD pipelines to access AWS resources and deploy the application stacks
- The github policy that authorizes a federated github user to do deployments

### Logging
This stack builds a relatively simple lambda function that logs the event and context it is called with an exits.  This is used for debugging and development purposes.

## Component Dispatch
One of the key features of this implementation is the ability to pass in an argument with type `dict[str, Dispatchable]` to the [Dispatcher class](./lib/dispatch.py). 
The Dispatcher does not know or care about the internal workings of any given element, it only needs to know that implements an `act()` function and a `build()` function. 
This moves the definition and management of these mappings out to the top-level Resume constructor. 
It does however make the Dispatcher a little bit hard to understand, but fundamentally, it can be ignored unless something needs to be changed or fixed with Dispatch itself.
