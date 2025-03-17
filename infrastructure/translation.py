from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_lambda as lam,
    aws_s3 as s3,
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
)
from constructs import Construct
from typing import cast, Optional


class Translation(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        removal_policy: RemovalPolicy,
        ddb_table: dynamodb.Table,
        source_keys_uri: str,
        event_bus: Optional[events.IEventBus] = None,
        logging_level: Optional[str] = None,
        tracing: Optional[bool] = False,
    ):
        super().__init__(scope, id_)
        logging_level = logging_level or "DEBUG"
        source = s3.Bucket(
            self,
            "source",
            removal_policy=removal_policy,
            auto_delete_objects=(removal_policy == removal_policy.DESTROY),
        )
        destination = s3.Bucket(
            self,
            "destination",
            removal_policy=removal_policy,
            auto_delete_objects=(removal_policy == removal_policy.DESTROY),
        )
        role = iam.Role(
            self,
            "translation",
            assumed_by=iam.ServicePrincipal("translate.amazonaws.com"),
        )
        source.grant_read_write(role)
        destination.grant_read_write(role)
        CfnOutput(self, "source_bucket", value=source.bucket_name)
        CfnOutput(self, "destination_bucket", value=destination.bucket_name)
        CfnOutput(self, "role_arn", value=role.role_arn)
        lambda_policy = iam.ManagedPolicy(
            self,
            "lambda_policy",
            statements=[
                iam.PolicyStatement(
                    actions=["logs:*"],
                    effect=iam.Effect.ALLOW,
                    resources=["arn:aws:logs:*"],
                )
            ],
        )
        lambda_role = iam.Role(
            self,
            "lambda_role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[lambda_policy],
        )
        source.grant_read(lambda_role)
        destination.grant_read(lambda_role)
        ddb_table.grant_read_write_data(lambda_role)
        function = lam.Function(
            self,
            "resume_fn",
            code=lam.Code.from_asset("./build/language.zip"),
            handler="lib.language.handler",
            runtime=cast(lam.Runtime, lam.Runtime.PYTHON_3_13),
            role=lambda_role,
            tracing=lam.Tracing.ACTIVE if tracing else lam.Tracing.DISABLED,
            environment={
                "logging_level": logging_level,
                "ddb_table_name": ddb_table.table_name,
                "language_bucket_name": destination.bucket_name,
                "source_keys_uri": source_keys_uri,
            },
            memory_size=512,
            timeout=Duration.seconds(300),
        )
        rule = events.Rule(
            self,
            "translation-success",
            event_bus=event_bus,
            event_pattern=events.EventPattern(source=["aws.translate"], detail={"jobStatus": ["COMPLETED"]}),
        )
        rule.add_target(targets.LambdaFunction(cast(lam.IFunction, function)))


class TranslationStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        removal_policy: RemovalPolicy,
        ddb_table: dynamodb.Table,
        source_keys_uri: str,
        logging_level: Optional[str] = None,
        event_bus: Optional[events.IEventBus] = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, id_, **kwargs)
        Translation(
            self,
            "translation",
            removal_policy=removal_policy,
            logging_level=logging_level,
            event_bus=event_bus,
            ddb_table=ddb_table,
            source_keys_uri=source_keys_uri,
        )
