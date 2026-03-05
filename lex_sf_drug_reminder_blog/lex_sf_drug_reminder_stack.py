#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CustomResource,
    aws_secretsmanager as secretsmanager,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda_event_sources as lambda_event_sources,
    aws_cloudwatch as cloudwatch
)
from constructs import Construct

from iot_resources import IoTStack

SFDC_DYNAMO_DB_TABLE_NAME = "SFDCPatientTable"


class LexSFDCDrugReminderStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        params = kwargs.pop('params')
        super().__init__(scope, construct_id, **kwargs)

        sfdc_consumer_key_secretsmanager = secretsmanager.CfnSecret(self, 'sfdcconsumerkey{}'.format(construct_id),
                                                                        name='sfdcconsumerkey{}'.format(construct_id),
                                                                        secret_string=params.get("sfdc_consumer_key"))
        sfdc_consumer_key_secretsmanager.apply_removal_policy(RemovalPolicy.DESTROY)

        sfdc_consumer_secret_secretsmanager = secretsmanager.CfnSecret(self,
                                                                           'sfdcconsumersecret{}'.format(construct_id),
                                                                           name='sfdcconsumersecret{}'.format(
                                                                               construct_id),
                                                                           secret_string=params.get(
                                                                               "sfdc_consumer_secret"))
        sfdc_consumer_secret_secretsmanager.apply_removal_policy(RemovalPolicy.DESTROY)

        sfdc_user_name_secretsmanager = secretsmanager.CfnSecret(self, 'sfdcusername{}'.format(construct_id),
                                                                     name='sfdcusername{}'.format(construct_id),
                                                                     secret_string=params.get("sfdc_user_name"))
        sfdc_user_name_secretsmanager.apply_removal_policy(RemovalPolicy.DESTROY)

        sfdc_user_password_secretsmanager = secretsmanager.CfnSecret(self,
                                                                         'sfdcuserpassword{}'.format(construct_id),
                                                                         name='sfdcuserpassword{}'.format(construct_id),
                                                                         secret_string=params.get("sfdc_user_password"))
        sfdc_user_password_secretsmanager.apply_removal_policy(RemovalPolicy.DESTROY)

        sfdc_user_security_token_secretsmanager = secretsmanager.CfnSecret(self, 'sfdcusersecuritytoken{}'.format(
            construct_id),
                                                                               name='sfdcusersecuritytoken{}'.format(
                                                                                   construct_id),
                                                                               secret_string=params.get(
                                                                                   "sfdc_user_security_token"))
        sfdc_user_security_token_secretsmanager.apply_removal_policy(RemovalPolicy.DESTROY)

        sfdc_endpoint_secretsmanager = secretsmanager.CfnSecret(self, 'sfdcendpoint{}'.format(construct_id),
                                                                    name='sfdcendpoint{}'.format(construct_id),
                                                                    secret_string=params.get("sfdc_endpoint"))
        sfdc_endpoint_secretsmanager.apply_removal_policy(RemovalPolicy.DESTROY)

        secrets_manager_iam_policy_statement = iam.PolicyStatement(actions=['secretsmanager:GetSecretValue',
                                                                                'secretsmanager:DescribeSecret'
                                                                                ],
                                                                       effect=iam.Effect.ALLOW,
                                                                       resources=[
                                                                           sfdc_consumer_secret_secretsmanager.ref,
                                                                           sfdc_endpoint_secretsmanager.ref,
                                                                           sfdc_user_password_secretsmanager.ref,
                                                                           sfdc_user_name_secretsmanager.ref,
                                                                           sfdc_consumer_key_secretsmanager.ref,
                                                                           sfdc_user_security_token_secretsmanager.ref
                                                                       ])

        fetch_lambda = lambda_python.PythonFunction(self, 'SFDCFetchLambda',
                                                    entry='./lex_sf_drug_reminder_blog/_lambda/functions/sfdc_fetch',
                                                    index='lambda_function.py',
                                                    handler='lambda_handler',
                                                    runtime=_lambda.Runtime.PYTHON_3_8,
                                                    timeout=Duration.minutes(2),
                                                    environment={"LOG_LEVEL": "DEBUG",
                                                                 "CONSUMER_KEY": "sfdcconsumerkey{}".format(
                                                                     construct_id),
                                                                 "CONSUMER_SECRET": "sfdcconsumersecret{}".format(
                                                                     construct_id),
                                                                 "USER_NAME": "sfdcusername{}".format(construct_id),
                                                                 "USER_PASSWORD": "sfdcuserpassword{}".format(
                                                                     construct_id),
                                                                 "USER_SECURITY_TOKEN": "sfdcusersecuritytoken{}".format(
                                                                     construct_id),
                                                                 "SALESFORCE_ENDPOINT": "sfdcendpoint{}".format(
                                                                     construct_id),
                                                                 "DYNAMO_DB_TABLE": SFDC_DYNAMO_DB_TABLE_NAME
                                                                 }
                                                    )

        fetch_lambda.add_to_role_policy(secrets_manager_iam_policy_statement)

        # fetch patients once every 6 hours
        sfdc_patient_fetch_scheduler = events.Rule(self, 'SFDCPatientFetchRule',
                                                       schedule=events.Schedule.expression('cron(0 */6 * * ? *)'))

        sfdc_patient_fetch_scheduler.add_target(target=targets.LambdaFunction(fetch_lambda))

        patient_table = dynamodb.Table(self, 'SFDCDynamoDBTable',
                                           partition_key=dynamodb.Attribute(name='Customer_Phone_Number',
                                                                                type=dynamodb.AttributeType.STRING),
                                           table_name=SFDC_DYNAMO_DB_TABLE_NAME,
                                           stream=dynamodb.StreamViewType.NEW_IMAGE,
                                           removal_policy=RemovalPolicy.DESTROY,
                                           )

        patient_table.grant_write_data(fetch_lambda)

        lex_fulfilment_lambda = lambda_python.PythonFunction(self, 'SFDCUpdateLambda',
                                                             entry='./lex_sf_drug_reminder_blog/_lambda/functions/lex_fulfillment',
                                                             index='lambda_function.py',
                                                             handler='lambda_handler',
                                                             runtime=_lambda.Runtime.PYTHON_3_8,
                                                             timeout=Duration.minutes(2),
                                                             environment={"LOG_LEVEL": "DEBUG",
                                                                          "CONSUMER_KEY": "sfdcconsumerkey{}".format(
                                                                              construct_id),
                                                                          "CONSUMER_SECRET": "sfdcconsumersecret{}".format(
                                                                              construct_id),
                                                                          "USER_NAME": "sfdcusername{}".format(
                                                                              construct_id),
                                                                          "USER_PASSWORD": "sfdcuserpassword{}".format(
                                                                              construct_id),
                                                                          "USER_SECURITY_TOKEN": "sfdcusersecuritytoken{}".format(
                                                                              construct_id),
                                                                          "SALESFORCE_ENDPOINT": "sfdcendpoint{}".format(
                                                                              construct_id),
                                                                          "DYNAMO_DB_TABLE": SFDC_DYNAMO_DB_TABLE_NAME
                                                                          })
        lex_fulfilment_lambda.add_to_role_policy(secrets_manager_iam_policy_statement)

        lex_operator_iam_policy_statement_lambda = iam.PolicyStatement(actions=['lambda:AddPermission'],
                                                                           effect=iam.Effect.ALLOW,
                                                                           resources=[
                                                                               lex_fulfilment_lambda.function_arn])

        lex_operator_iam_policy_statement_lambda_lex_import = iam.PolicyStatement(actions=['lex:StartImport',
                                                                                               'lex:GetImport'],
                                                                                      effect=iam.Effect.ALLOW,
                                                                                      resources=[
                                                                                          'arn:aws:lex:{}:{}:bot:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Drug_Reminder_Bot'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Dose_Confirm'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Dose_Quantity'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Auth'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'MRI_Scan'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Dose_Appearance'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Close_Intent')
                                                                                      ])

        lex_operator_iam_policy_statement_lambda_lex_update = iam.PolicyStatement(actions=["lex:PutSlotType",
                                                                                               "lex:GetBot",
                                                                                               "lex:PutBot",
                                                                                               "lex:GetIntent",
                                                                                               "lex:PutIntent",
                                                                                               "lex:GetSlotType",
                                                                                                                                                                                                                                                                                                                                                                                            "lex:StartImport",
                                                                                               "lex:GetImport",  
                                                                                               "lex:CreateBot",
                                                                                               "lex:CreateIntent",
                                                                                               "lex:UpdateSlot",
                                                                                               "lex:DescribeBotLocale",
                                                                                               "lex:UpdateBotAlias",
                                                                                               "lex:CreateSlotType",
                                                                                                                                                                                              "lex:DescribeBot",
                                                                                               "lex:UpdateBotLocale",
                                                                                               "lex:CreateSlot",
                                                                                                                                                                                              "lex:UpdateBot",
                                                                                                                                                                                              "lex:DescribeBotAlias",
                                                                                               "lex:CreateBotLocale",
                                                                                                                                                                                              "lex:StartImport",
                                                                                               "lex:UpdateSlotType",
                                                                                               "lex:UpdateIntent",
                                                                                               "lex:DescribeImport"
                                                                                               ],
                                                                                      effect=iam.Effect.ALLOW,
                                                                                      resources=[
                                                                                          'arn:aws:lex:{}:{}:bot:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Drug_Reminder_Bot'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Dose_Confirm'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Dose_Quantity'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Auth'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'MRI_Scan'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Dose_Appearance'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Close_Intent')
                                                                                      ]
                                                                                      )

        lex_operator_lambda = lambda_python.PythonFunction(self, 'LexOperatorLambda',
                                                           entry='./lex_sf_drug_reminder_blog/_lambda/functions/lex_operator',
                                                           index='lambda_function.py',
                                                           handler='lambda_handler',
                                                           runtime=_lambda.Runtime.PYTHON_3_8,
                                                           timeout=Duration.minutes(5),
                                                           environment={"LOG_LEVEL": "DEBUG",
                                                                        "LEX_LAMBDA_ARN": lex_fulfilment_lambda.function_arn})

        lex_operator_lambda.add_to_role_policy(lex_operator_iam_policy_statement_lambda)
        lex_operator_lambda.add_to_role_policy(lex_operator_iam_policy_statement_lambda_lex_import)
        lex_operator_lambda.add_to_role_policy(lex_operator_iam_policy_statement_lambda_lex_update)

        CustomResource(self, 'LexDeploymentTrigger',
                            service_token=lex_operator_lambda.function_arn
                            )

        connect_operator_lambda_v2 = lambda_python.PythonFunction(self, 'ConnectOperatorLambdav2',
                                                                  entry='./lex_sf_drug_reminder_blog/_lambda/functions/connect_import_flow',
                                                                  index='lambda_function.py',
                                                                  handler='lambda_handler',
                                                                  runtime=_lambda.Runtime.PYTHON_3_8,
                                                                  timeout=Duration.minutes(5),
                                                                  environment={"LOG_LEVEL": "DEBUG",
                                                                               "CONNECT_LAMBDA_ARN": lex_fulfilment_lambda.function_arn,
                                                                               "ACCOUNT_ID": self.account,
                                                                               "CONNECT_INSTANCE_ID": str(params.get(
                                                                                   "connectInstanceID"))
                                                                               })

        connect_operator_lambda_connect_import_connect = iam.PolicyStatement(actions=[                                                                                  "connect:DescribeInstance",
                                                                                  "connect:ListInstances",
                                                                                  "connect:AssociateInstanceStorageConfig",
                                                                                  "connect:UpdateInstanceAttribute",
                                                                                  "connect:ListSecurityKeys",
                                                                                  "connect:ListLexBots",
                                                                                  "connect:ListBots",
                                                                                  "connect:AssociateBot",
                                                                                  "connect:DisassociateBot",
                                                                                  "connect:ListBots",
                                                                                  "connect:AssociateLexBot",
                                                                                  "connect:DisassociateLexBot",
                                                                                  "connect:ListLexBots",
                                                                                  "connect:ListLambdaFunctions",
                                                                                  "connect:AssociateLambdaFunction",
                                                                                  "connect:DisassociateLambdaFunction"],
                                                                         effect=iam.Effect.ALLOW,
                                                                         resources=[f"arn:aws:connect:{self.region}:{self.account}:instance/{params.get('connectInstanceID')}",
                                                                                   f"arn:aws:connect:{self.region}:{self.account}:instance/{params.get('connectInstanceID')}/*"])
        connect_operator_lambda_connect_import_lex = iam.PolicyStatement(actions=["lex:GetBots",
                                                                                          "lex:GetBot",
                                                                                          "lex:CreateResourcePolicy",
                                                                                                                                                                                    "lex:UpdateResourcePolicy",
                                                                                          "lex:DescribeBotAlias",
                                                                                          "lex:ListBotAliases",
                                                                                          "lex:ListBots"],
                                                                         effect=iam.Effect.ALLOW,
                                                                         resources=[
                                                                                          'arn:aws:lex:{}:{}:bot:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Drug_Reminder_Bot'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Dose_Confirm'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Dose_Quantity'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Auth'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'MRI_Scan'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Dose_Appearance'),
                                                                                          'arn:aws:lex:{}:{}:intent:{}:*'.format(
                                                                                              self.region, self.account,
                                                                                              'Close_Intent')
                                                                                      ])

        connect_operator_lambda_v2.add_permission(id='lex', principal=iam.ServicePrincipal("lex.amazonaws.com"))
        connect_operator_lambda_v2.add_permission(id='connect',
                                                  principal=iam.ServicePrincipal("connect.amazonaws.com"))
        connect_operator_lambda_v2.add_to_role_policy(connect_operator_lambda_connect_import_connect)
        connect_operator_lambda_v2.add_to_role_policy(connect_operator_lambda_connect_import_lex)

        connect_deployment = CustomResource(self, 'ConnectDeploymentTriggerNew',
                                                 service_token=connect_operator_lambda_v2.function_arn
                                                 )
        # lex_sf_drug_reminder_blog/_lambda/functions/customer_calling
        customer_calling_lambda = lambda_python.PythonFunction(self, 'CustomerCallingLambda',
                                                               entry='./lex_sf_drug_reminder_blog/_lambda/functions/customer_calling',
                                                               index='lambda_function.py',
                                                               handler='lambda_handler',
                                                               runtime=_lambda.Runtime.PYTHON_3_8,
                                                               timeout=Duration.minutes(2),
                                                               environment={"LOG_LEVEL": "DEBUG",
                                                                            "PATIENT_RECORDS": patient_table.table_name,
                                                                            "CONNECT_INSTANCE_ID": str(params.get(
                                                                                "connectInstanceID")),
                                                                            "FLOW_ID": "Upload Flow ID here",
                                                                            "QueueId": "Upload Queue ID here"
                                                                            })

        customer_calling_lambda.add_event_source(lambda_event_sources.DynamoEventSource(
            table=patient_table,
            starting_position=_lambda.StartingPosition.TRIM_HORIZON
        ))
        customer_calling_lambda.add_permission(id='lex', principal=iam.ServicePrincipal("lex.amazonaws.com"))
        customer_calling_lambda.add_permission(id='connect',
                                               principal=iam.ServicePrincipal("connect.amazonaws.com"))
        customer_calling_lambda.add_to_role_policy(connect_operator_lambda_connect_import_connect)
        customer_calling_lambda.add_to_role_policy(connect_operator_lambda_connect_import_lex)
        patient_table.grant_read_write_data(customer_calling_lambda)

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
        
        # Call the IoT Stack
        IoTStack(self, "iot-resources", project_prefix_obj=params.get("project_prefix"),
                 time_zone_obj=params.get("time_zone"),
                 dynamoTable_obj=patient_table)
