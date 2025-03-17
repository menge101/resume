from aws_cdk import aws_iam as iam, aws_lambda as lam, CfnOutput, Stack
from constructs import Construct
from typing import cast


class Logging(Stack):
    def __init__(self, scope: Construct, id_: str) -> None:
        super().__init__(scope, id_)
        self.policy = iam.ManagedPolicy(
            self,
            "policy",
            statements=[
                iam.PolicyStatement(
                    actions=["logs:*"],
                    effect=iam.Effect.ALLOW,
                    resources=["arn:aws:logs:*"],
                )
            ],
        )
        self.role = iam.Role(
            self,
            "role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[self.policy],
        )
        self.function = lam.Function(
            self,
            "logging",
            code=lam.Code.from_asset("./build/logging.zip"),
            handler="lib.log.handler",
            runtime=cast(lam.Runtime, lam.Runtime.PYTHON_3_13),
            role=self.role,
        )
        function_url = self.function.add_function_url(auth_type=lam.FunctionUrlAuthType.NONE)
        CfnOutput(self, "url", value=function_url.url)
