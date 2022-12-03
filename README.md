Group Members: Adam Bullard, Don Strong

ALB Link: http://ec2co-ecsel-1r13h1vw1h9v0-533578369.us-west-2.elb.amazonaws.com:3000

Most challenging part of assignment: Getting the SQS working with the lambda function. I was trying to use boto3 to retrieve sqs messages for awhile, but it turns out the lambda receives the messages automatically in the event variable. Once I figured that out, it was pretty easy to figure out. 

Buggy features: None found so far, all should be solved. Occasionally the API ECS task would crash due to lack of memory but upping the task definition's memory allocation did the trick.

Client instructions: 
1. Ensure python3 is installed on your system.
2. Navigate into the ClientApp folder.
3. If you have pipenv installed, run the environment defined in the Pipfile which will automatically install modules with `pipenv run python3 client.py`.
4. Alternatively, if you have the modules listed in the Pipfile installed for your own python3 installation, simply run the client with `python3 client.py`.
