#!/usr/bin/env python3
"""Apply security fixes to the CDK stack"""

import re

# Read the file
with open('lex_sf_drug_reminder_blog/lex_sf_drug_reminder_stack.py', 'r') as f:
    content = f.read()

# Fix #1: Add CloudWatch imports
content = content.replace(
    'aws_lambda_event_sources as lambda_event_sources\n)',
    'aws_lambda_event_sources as lambda_event_sources,\n    aws_cloudwatch as cloudwatch\n)'
)

# Fix #2: Remove Delete permissions from Lex policies
delete_permissions = [
    "'lex:DeleteBot',\n",
    '"lex:DeleteBot",\n',
    "'lex:DeleteIntent',\n",
    '"lex:DeleteIntent",\n',
    "'lex:DeleteSlotType',\n",
    '"lex:DeleteSlotType",\n',
    "'lex:DeleteBotLocale',\n",
    '"lex:DeleteBotLocale",\n',
    "'lex:DeleteSlot',\n",
    '"lex:DeleteSlot",\n',
    '"lex:DeleteResourcePolicy",\n'
]

for perm in delete_permissions:
    content = content.replace(perm, '')

# Fix #3: Remove CreateInstance from Connect
content = content.replace('"connect:CreateInstance",\n', '')

# Fix #4: Restrict Connect instance to specific ID
content = content.replace(
    'resources=["arn:aws:connect:{}:{}:instance/*".format(\n                                                                                              self.region, self.account)])',
    'resources=[f"arn:aws:connect:{self.region}:{self.account}:instance/{params.get(\'connectInstanceID\')}",\n                                                                                   f"arn:aws:connect:{self.region}:{self.account}:instance/{params.get(\'connectInstanceID\')}/*"])'
)

# Fix #5: Add DynamoDB encryption
content = content.replace(
    'removal_policy=RemovalPolicy.DESTROY,\n                                           )',
    'encryption=dynamodb.TableEncryption.AWS_MANAGED,\n                                           point_in_time_recovery=True,\n                                           removal_policy=RemovalPolicy.DESTROY,\n                                           )'
)

# Fix #6: Add CloudWatch alarms before IoTStack call
alarm_code = '''
        # SECURITY FIX: Add CloudWatch Alarms for security monitoring
        lambda_error_alarm = cloudwatch.Alarm(
            self, "LambdaErrorAlarm",
            metric=lex_fulfilment_lambda.metric_errors(statistic="Sum", period=Duration.minutes(5)),
            threshold=5,
            evaluation_periods=1,
            alarm_description="Alert on multiple Lambda function errors"
        )
        
        dynamodb_throttle_alarm = cloudwatch.Alarm(
            self, "DynamoDBThrottleAlarm",
            metric=patient_table.metric_user_errors(statistic="Sum", period=Duration.minutes(5)),
            threshold=10,
            evaluation_periods=1,
            alarm_description="Alert on DynamoDB throttling events"
        )
        
'''

content = content.replace(
    '        # Call the IoT Stack\n        IoTStack(',
    alarm_code + '        # Call the IoT Stack\n        IoTStack('
)

# Write the file
with open('lex_sf_drug_reminder_blog/lex_sf_drug_reminder_stack.py', 'w') as f:
    f.write(content)

print("✅ Security fixes applied to CDK stack")
