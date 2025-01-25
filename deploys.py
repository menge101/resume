from aws_cdk import (
    aws_cloudfront as cf,
    Duration,
    RemovalPolicy,
    Stack,
    Stage,
)
from constructs import Construct
from infrastructure import github, translation, web


class Development(Stage):
    def __init__(self, scope: Construct, id_: str, **kwargs):
        super().__init__(scope, id_, **kwargs)
        removal_policy = RemovalPolicy.DESTROY
        resume = Resume(
            self,
            "webapp",
            removal_policy=removal_policy,
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
        translation.TranslationStack(
            self,
            "translation",
            removal_policy=removal_policy,
            logging_level="DEBUG",
            ddb_table=resume.web.table,
            source_keys_uri="s3://development-translation-translationsource303b34d4-rwgn7buxzupq/keys/en.txt",
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
        origin_policy = cf.OriginRequestPolicy(
            self,
            "dev-origin-policy",
            query_string_behavior=cf.OriginRequestQueryStringBehavior.allow_list(
                "action"
            ),
            header_behavior=cf.OriginRequestHeaderBehavior.none(),
            cookie_behavior=cf.OriginRequestCookieBehavior.all(),
        )
        self.web = web.Web(
            self,
            "web-application-construct",
            removal_policy=removal_policy,
            logging_level=logging_level,
            tracing=tracing,
            cache_policy=cache_policy,
            origin_policy=origin_policy,
        )
