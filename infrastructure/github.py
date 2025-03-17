from aws_cdk import Aws, aws_iam as iam, CfnOutput
from constructs import Construct


class GithubIdp(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        pass_role_arn: str,
        staging_bucket_arn: str,
        cdk_bootstrap_version_param_arn: str,
        github_open_id_provider_arn: str | None = None,
    ):
        super().__init__(scope, id_)
        if not github_open_id_provider_arn:
            open_id_provider_arn = self.create_github_open_connect_provider()
        else:
            open_id_provider_arn = github_open_id_provider_arn
        policy = iam.ManagedPolicy(
            self,
            "github-managed-policy",
            managed_policy_name="github-managed-policy",
            statements=[
                iam.PolicyStatement(
                    sid="BasicCFNPerms",
                    actions=[
                        "cloudformation:CreateChangeSet",
                        "cloudformation:DeleteChangeSet",
                        "cloudformation:DescribeChangeSet",
                        "cloudformation:DescribeStacks",
                        "cloudformation:ExecuteChangeSet",
                        "cloudformation:CreateStack",
                        "cloudformation:UpdateStack",
                        "cloudformation:RollbackStack",
                        "cloudformation:ContinueUpdateRollback",
                    ],
                    resources=["*"],
                    effect=iam.Effect.ALLOW,
                ),
                iam.PolicyStatement(
                    sid="PipelineCrossAccountBucketPerms",
                    actions=[
                        "s3:GetObject*",
                        "s3:GetBucket*",
                        "s3:List*",
                        "s3:Abort*",
                        "s3:DeleteObject*",
                        "s3:PutObject*",
                    ],
                    resources=["*"],
                    conditions={"StringNotEquals": {"s3:ResourceAccount": Aws.ACCOUNT_ID}},
                ),
                iam.PolicyStatement(
                    sid="PipelineCrossAccountKMSperms",
                    actions=[
                        "kms:Decrypt",
                        "kms:DescribeKey",
                        "kms:Encrypt",
                        "kms:ReEncrypt*",
                        "kms:GenerateDataKey*",
                    ],
                    resources=["*"],
                    conditions={"StringEquals": {"kms:ViaService": "s3.us-east-1.amazonaws.com"}},
                ),
                iam.PolicyStatement(
                    sid="AllowPassRole",
                    actions=["iam:PassRole"],
                    resources=[pass_role_arn],
                    effect=iam.Effect.ALLOW,
                ),
                iam.PolicyStatement(
                    sid="AllowCDKRoles",
                    actions=["sts:AssumeRole"],
                    resources=["arn:aws:iam::*:role/cdk-*"],
                    effect=iam.Effect.ALLOW,
                ),
                iam.PolicyStatement(
                    sid="CliPerms",
                    actions=[
                        "cloudformation:DescribeStackEvents",
                        "cloudformation:GetTemplate",
                        "cloudformation:DeleteStack",
                        "cloudformation:UpdateTerminationProtection",
                        "sts:GetCallerIdentity",
                        "cloudformation:GetTemplateSummary",
                    ],
                    resources=["*"],
                    effect=iam.Effect.ALLOW,
                ),
                iam.PolicyStatement(
                    sid="CliStagingBucketPerms",
                    actions=["s3:GetObject*", "s3:GetBucket*", "s3:List*"],
                    resources=[staging_bucket_arn, f"{staging_bucket_arn}/*"],
                    effect=iam.Effect.ALLOW,
                ),
                iam.PolicyStatement(
                    sid="ReadCdkBootstrapVersion",
                    actions=["ssm:GetParameter", "ssm:GetParameters"],
                    resources=[cdk_bootstrap_version_param_arn],
                    effect=iam.Effect.ALLOW,
                ),
                iam.PolicyStatement(
                    sid="AssumeCDKRoles",
                    actions=["iam:AssumeRole"],
                    resources=[cdk_bootstrap_version_param_arn],
                    effect=iam.Effect.ALLOW,
                ),
            ],
        )
        role = iam.Role(
            self,
            "ghidp_role",
            assumed_by=iam.WebIdentityPrincipal(open_id_provider_arn).with_conditions(
                {
                    "StringLike": {"token.actions.githubusercontent.com:sub": ["repo:menge101/*"]},
                    "StringEquals": {"token.actions.githubusercontent.com:aud": ["sts.amazonaws.com"]},
                }
            ),
            managed_policies=[policy],
        )
        CfnOutput(self, "role-arn", value=role.role_arn)

    def create_github_open_connect_provider(self) -> str:
        ghidp = iam.OpenIdConnectProvider(
            self,
            "ghidp",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"],
        )
        return ghidp.open_id_connect_provider_arn
