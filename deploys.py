from aws_cdk import aws_cloudfront as cf, Duration, RemovalPolicy, Stack, Stage
from constructs import Construct
from infrastructure import github, web


class Development(Stage):
    def __init__(self, scope: Construct, id_: str, **kwargs):
        super().__init__(scope, id_, **kwargs)
        Resume(
            self,
            "webapp",
            removal_policy=RemovalPolicy.DESTROY,
            logging_level="DEBUG",
            tracing=True,
        )
        GitHubIamConnection(
            self,
            "github-connection",
            pass_role_arn="arn:aws:iam::779846793683:role/cdk-hnb659fds-cfn-exec-role-779846793683-us-east-1",
            staging_bucket_arn="arn:aws:s3:::cdk-hnb659fds-assets-779846793683-us-east-1",
            cdk_bootstrap_version_param_arn=(
                "arn:aws:ssm:us-east-1:779846793683:parameter"
                "/cdk-bootstrap/hnb659fds/version"
            ),
        )


class GitHubIamConnection(Stack):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        pass_role_arn: str,
        staging_bucket_arn: str,
        cdk_bootstrap_version_param_arn: str,
    ):
        super().__init__(scope, id_)
        github.GithubIdp(
            self,
            "github-idp",
            pass_role_arn=pass_role_arn,
            staging_bucket_arn=staging_bucket_arn,
            cdk_bootstrap_version_param_arn=cdk_bootstrap_version_param_arn,
        )


class Resume(Stack):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        removal_policy: RemovalPolicy,
        logging_level: str,
        tracing: bool,
        **kwargs,
    ) -> None:
        super().__init__(scope, id_, **kwargs)
        cache_policy = cf.CachePolicy(
            self,
            "dev-cache-policy",
            cookie_behavior=cf.CacheCookieBehavior.all(),
            default_ttl=Duration.seconds(1),
            max_ttl=Duration.seconds(1),
        )
        web.Web(
            self,
            "web-application-construct",
            removal_policy=removal_policy,
            logging_level=logging_level,
            tracing=tracing,
            cache_policy=cache_policy,
        )
