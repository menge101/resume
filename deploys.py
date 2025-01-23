from aws_cdk import aws_cloudfront as cf, Duration, RemovalPolicy, Stack, Stage
from constructs import Construct
from infrastructure.web import Web


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
        Web(
            self,
            "web-application-construct",
            removal_policy=removal_policy,
            logging_level=logging_level,
            tracing=tracing,
            cache_policy=cache_policy,
        )
