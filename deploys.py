from aws_cdk import aws_cloudfront as cf, RemovalPolicy, Stack, Stage
from constructs import Construct
from infrastructure.web import Web
from typing import cast


class Development(Stage):
    def __init__(self, scope: Construct, id_: str, **kwargs):
        super().__init__(scope, id_, **kwargs)
        Resume(
            self,
            "webapp",
            removal_policy=RemovalPolicy.DESTROY,
            logging_level="DEBUG",
            tracing=True,
            cache_policy=cast(cf.CachePolicy, cf.CachePolicy.CACHING_DISABLED),
        )


class Resume(Stack):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        removal_policy: RemovalPolicy,
        logging_level: str,
        tracing: bool,
        cache_policy: cf.CachePolicy,
        **kwargs,
    ) -> None:
        super().__init__(scope, id_, **kwargs)
        Web(
            self,
            "web-application-construct",
            removal_policy=removal_policy,
            logging_level=logging_level,
            tracing=tracing,
            cache_policy=cache_policy,
        )
