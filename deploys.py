from aws_cdk import (
    aws_cloudfront as cf,
    Duration,
    Environment,
    RemovalPolicy,
    Stack,
    Stage,
)
from constructs import Construct
from infrastructure import github, hosted_zone, translation, web
from typing import Optional


DEV_ENV = Environment(account="779846793683", region="us-east-1")
PRD_ENV = Environment(account="473626866269", region="us-east-1")
PRODUCTION_DOMAIN_NAME = "nathanmenge.com"


class Production(Stage):
    def __init__(self, scope: Construct, id_: str, **kwargs):
        super().__init__(scope, id_, **kwargs)
        removal_policy = RemovalPolicy.RETAIN
        cache_policy_props = cf.CachePolicyProps(
            cookie_behavior=cf.CacheCookieBehavior.all(),
            default_ttl=Duration.seconds(1),
            max_ttl=Duration.seconds(1),
        )
        origin_request_policy_props = cf.OriginRequestPolicyProps(
            cookie_behavior=cf.OriginRequestCookieBehavior.all(),
            header_behavior=cf.OriginRequestHeaderBehavior.none(),
            query_string_behavior=cf.OriginRequestQueryStringBehavior.allow_list("action"),
        )
        resume = Resume(
            self,
            "webapp",
            removal_policy=removal_policy,
            logging_level="INFO",
            tracing=True,
            cache_policy_props=cache_policy_props,
            origin_request_policy_props=origin_request_policy_props,
            domain_name=PRODUCTION_DOMAIN_NAME,
        )
        GitHubIamConnection(
            self,
            "github-connection",
            pass_role_arn="arn:aws:iam::473626866269:role/cdk-hnb659fds-cfn-exec-role-473626866269-us-east-1",
            staging_bucket_arn="arn:aws:s3:::cdk-hnb659fds-assets-473626866269-us-east-1",
            cdk_bootstrap_version_param_arn=(
                "arn:aws:ssm:us-east-1:473626866269:parameter/cdk-bootstrap/hnb659fds/version"
            ),
            github_open_id_provider_arn="arn:aws:iam::473626866269:oidc-provider/token.actions.githubusercontent.com",
        )
        hosted_zone.HostedZone(
            self,
            "prd-hosted-zone",
            domain_name=PRODUCTION_DOMAIN_NAME,
            cf_distribution=resume.web.distribution,
        )


class Development(Stage):
    def __init__(self, scope: Construct, id_: str, **kwargs):
        super().__init__(scope, id_, **kwargs)
        removal_policy = RemovalPolicy.DESTROY
        cache_policy_props = cf.CachePolicyProps(
            cookie_behavior=cf.CacheCookieBehavior.all(),
            default_ttl=Duration.seconds(1),
            max_ttl=Duration.seconds(1),
        )
        origin_policy_props = cf.OriginRequestPolicyProps(
            cookie_behavior=cf.OriginRequestCookieBehavior.all(),
            header_behavior=cf.OriginRequestHeaderBehavior.none(),
            query_string_behavior=cf.OriginRequestQueryStringBehavior.allow_list("action"),
        )
        resume = Resume(
            self,
            "webapp",
            removal_policy=removal_policy,
            logging_level="DEBUG",
            tracing=True,
            cache_policy_props=cache_policy_props,
            origin_request_policy_props=origin_policy_props,
            function_environment_variables={"environment_name": "dev"},
        )
        GitHubIamConnection(
            self,
            "github-connection",
            pass_role_arn="arn:aws:iam::779846793683:role/cdk-hnb659fds-cfn-exec-role-779846793683-us-east-1",
            staging_bucket_arn="arn:aws:s3:::cdk-hnb659fds-assets-779846793683-us-east-1",
            cdk_bootstrap_version_param_arn=(
                "arn:aws:ssm:us-east-1:779846793683:parameter/cdk-bootstrap/hnb659fds/version"
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
        github_open_id_provider_arn: str | None = None,
    ):
        super().__init__(scope, id_)
        github.GithubIdp(
            self,
            "github-idp",
            pass_role_arn=pass_role_arn,
            staging_bucket_arn=staging_bucket_arn,
            cdk_bootstrap_version_param_arn=cdk_bootstrap_version_param_arn,
            github_open_id_provider_arn=github_open_id_provider_arn,
        )


class Resume(Stack):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        removal_policy: RemovalPolicy,
        cache_policy_props: cf.CachePolicyProps,
        origin_request_policy_props: cf.OriginRequestPolicyProps,
        logging_level: str,
        tracing: bool,
        domain_name: str | None = None,
        function_environment_variables: Optional[dict[str, str]] = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, id_, **kwargs)
        cache_policy: cf.CachePolicy = cf.CachePolicy(self, "cache-policy", **cache_policy_props._values)
        origin_request_policy: cf.OriginRequestPolicy = cf.OriginRequestPolicy(
            self, "origin-request-policy", **origin_request_policy_props._values
        )
        self.web = web.Web(
            self,
            "web-application-construct",
            removal_policy=removal_policy,
            logging_level=logging_level,
            tracing=tracing,
            cache_policy=cache_policy,
            origin_policy=origin_request_policy,
            domain_name=domain_name,
            function_environment_variables=function_environment_variables,
        )
