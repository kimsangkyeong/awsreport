####################################################################################################
#
# Purpose   : declarative service registry - 확장 지점 (서비스 추가 = 항목 1개 + 모듈 함수)
# Source    : registry.py
# Usage     : from kskpkg.registry import SERVICE_REGISTRY
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create
#
# ServiceSpec 필드
#   key          : 내부 식별자 (enrich 의 dep_key / deps 키로 사용)
#   sheet        : Excel sheet 이름 (<=31자)
#   scope        : 'REGIONAL' | 'GLOBAL'
#   collector    : 'kskpkg.<module>.<function>' (importlib 로 동적 로드, ctx 1개 인자)
#   order        : 수집/출력 순서 (연관 리소스 우선 배치)
#   depends_on   : 선행 수집 key 목록 (enrich 참조 보장)
#   enrich       : [(target_col, dep_key, func_name, source_col), ...]
#   enabled      : False 면 수집 제외
#   arn_services : Discovery(Tagging API) 의 ARN service 토큰 목록.
#                  예: elb 계열 -> ['elasticloadbalancing'], ec2 계열 -> ['ec2'].
#                  Discovery 결과(존재 서비스 집합)와 교집합이 있으면 수집, 없으면 생략.
#   always_collect : True 면 Discovery 결과와 무관하게 항상 수집.
#                  (Tagging API 가 추적 못하는 타입 / 선행 의존 리소스 / 안전상 필수)
#   key_columns  : 리포트 비교(diff)시 리소스 행을 매칭할 안정적 식별 컬럼 목록.
#                  비우면 diff 는 전체 행 해시로 추가/삭제만 비교(수정 추적 제한).
####################################################################################################
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ServiceSpec:
    key: str
    sheet: str
    scope: str
    collector: str
    order: int = 100
    depends_on: list = field(default_factory=list)
    enrich: list = field(default_factory=list)
    enabled: bool = True
    arn_services: list = field(default_factory=list)
    always_collect: bool = False
    key_columns: list = field(default_factory=list)


SERVICE_REGISTRY: list[ServiceSpec] = [
    # ===== GLOBAL (us-east-1, 1회 수집 후 모든 리전 파일에 공통 포함) =====
    ServiceSpec("route53",         "route53",          "GLOBAL", "kskpkg.route53.list_hosted_zones", order=1,
                arn_services=["route53"]),
    ServiceSpec("route53_record",  "route53_record",   "GLOBAL", "kskpkg.route53.list_resource_record_sets", order=2,
                depends_on=["route53"], always_collect=True),
    ServiceSpec("cloudfront_dist", "cloudfront_dist",  "GLOBAL", "kskpkg.cloudfront.list_distributions", order=3,
                arn_services=["cloudfront"]),
    ServiceSpec("cloudfront_oid",  "cloudfront_oid",   "GLOBAL", "kskpkg.cloudfront.list_cloud_front_origin_access_identities", order=4,
                arn_services=["cloudfront"]),
    ServiceSpec("acm_global",      "acm_global",       "GLOBAL", "kskpkg.acm.list_certificates", order=5,
                arn_services=["acm"]),
    ServiceSpec("waf_cloudfront",  "waf_cloudfront",   "GLOBAL", "kskpkg.waf.list_web_acls_cloudfront", order=6,
                arn_services=["wafv2", "waf"]),

    # ===== REGIONAL - 네트워크 기반 (선행 수집, order 낮게) =====
    # vpc/subnet/sg/eni 등은 다른 서비스의 enrich 선행 의존이라 항상 수집.
    ServiceSpec("vpc",      "vpc",      "REGIONAL", "kskpkg.ec2.describe_vpcs", order=10,
                arn_services=["ec2"], always_collect=True),
    ServiceSpec("igw",      "igw",      "REGIONAL", "kskpkg.ec2.describe_internet_gateways", order=11,
                depends_on=["vpc"], enrich=[("VpcTName", "vpc", "get_vpcname", "AttachedVpcId")],
                arn_services=["ec2"]),
    ServiceSpec("subnet",   "subnet",   "REGIONAL", "kskpkg.ec2.describe_subnets", order=12,
                depends_on=["vpc"], enrich=[("VpcTName", "vpc", "get_vpcname", "VpcId")],
                arn_services=["ec2"], always_collect=True),
    ServiceSpec("kms",      "kms",      "REGIONAL", "kskpkg.kms.list_keys", order=13,
                arn_services=["kms"], always_collect=True),
    ServiceSpec("securitygroup", "securegroup", "REGIONAL", "kskpkg.ec2.describe_security_groups", order=14,
                depends_on=["vpc"], enrich=[("VpcTName", "vpc", "get_vpcname", "VpcId")],
                arn_services=["ec2"], always_collect=True),
    ServiceSpec("eni",      "eni",      "REGIONAL", "kskpkg.ec2.describe_network_interfaces", order=15,
                depends_on=["vpc", "subnet"],
                enrich=[("VpcTName", "vpc", "get_vpcname", "VpcId"),
                        ("SubnetTName", "subnet", "get_subnetname", "SubnetId")],
                arn_services=["ec2"], always_collect=True),
    ServiceSpec("instance", "instance", "REGIONAL", "kskpkg.ec2.describe_instances", order=16,
                depends_on=["vpc", "subnet", "eni"],
                enrich=[("VpcTName", "vpc", "get_vpcname", "VpcId"),
                        ("SubnetTName", "subnet", "get_subnetname", "SubnetId"),
                        ("ENITName", "eni", "get_eniname", "NetworkInterfaceId")],
                arn_services=["ec2"], always_collect=True),
    ServiceSpec("eip",      "eip",      "REGIONAL", "kskpkg.ec2.describe_addresses", order=17,
                depends_on=["eni", "instance"],
                enrich=[("ENITName", "eni", "get_eniname", "NetworkInterfaceId"),
                        ("InstanceTName", "instance", "get_insname", "InstanceId")],
                arn_services=["ec2"]),
    ServiceSpec("nat",      "nat",      "REGIONAL", "kskpkg.ec2.describe_nat_gateways", order=18,
                depends_on=["vpc", "subnet", "eip", "eni"],
                enrich=[("VpcTName", "vpc", "get_vpcname", "VpcId"),
                        ("SubnetTName", "subnet", "get_subnetname", "SubnetId"),
                        ("EIPTName", "eip", "get_eipname", "AllocationId"),
                        ("ENITName", "eni", "get_eniname", "NetworkInterfaceId")],
                arn_services=["ec2"], always_collect=True),
    ServiceSpec("managed_prefixlist", "managed_prefixlist", "REGIONAL", "kskpkg.ec2.describe_managed_prefix_lists", order=19,
                arn_services=["ec2"]),
    # 라우트 테이블: association(router) 관점 + route(routeinfo) 관점 2개 sheet
    ServiceSpec("router", "router", "REGIONAL", "kskpkg.ec2.describe_route_tables_assoc", order=20,
                depends_on=["vpc", "subnet"],
                enrich=[("VpcTName", "vpc", "get_vpcname", "VpcId"),
                        ("SubnetTName", "subnet", "get_subnetname", "SubnetId")],
                arn_services=["ec2"]),
    ServiceSpec("routeinfo", "routeinfo", "REGIONAL", "kskpkg.ec2.describe_route_tables_routes", order=21,
                depends_on=["vpc", "nat", "instance", "eni"],
                enrich=[("VpcTName", "vpc", "get_vpcname", "VpcId"),
                        ("NatGatewayTName", "nat", "get_natname", "NatGatewayId"),
                        ("InstanceTName", "instance", "get_insname", "InstanceId"),
                        ("ENITName", "eni", "get_eniname", "NetworkInterfaceId")],
                arn_services=["ec2"]),
    # VPC Endpoint
    ServiceSpec("vpcendpoint", "vpcendpoint", "REGIONAL", "kskpkg.ec2.describe_vpc_endpoints", order=22,
                depends_on=["vpc", "subnet", "securitygroup"],
                enrich=[("VpcTName", "vpc", "get_vpcname", "VpcId"),
                        ("SubnetTName", "subnet", "get_subnetname", "SubnetIds"),
                        ("SecurityGroupTName", "securitygroup", "get_sgname", "SecurityGroups")],
                arn_services=["ec2"]),

    # ===== REGIONAL - 컴퓨트/컨테이너 =====
    ServiceSpec("elb",      "elb",      "REGIONAL", "kskpkg.elb.describe_load_balancers", order=30,
                depends_on=["vpc", "subnet", "securitygroup"],
                enrich=[("VpcTName", "vpc", "get_vpcname", "VpcId"),
                        ("SubnetTName", "subnet", "get_subnetname", "SubnetId"),
                        ("SecurityGroupTName", "securitygroup", "get_sgname", "SecurityGroups")],
                arn_services=["elasticloadbalancing"]),
    ServiceSpec("elb_listener", "elb_listener", "REGIONAL", "kskpkg.elb.describe_listeners", order=31,
                depends_on=["elb"], arn_services=["elasticloadbalancing"]),
    ServiceSpec("elb_listener_rule", "elb_listener_rule", "REGIONAL", "kskpkg.elb.describe_rules", order=32,
                depends_on=["elb"], arn_services=["elasticloadbalancing"]),
    ServiceSpec("eks",      "eks",      "REGIONAL", "kskpkg.eks.list_clusters", order=33,
                depends_on=["vpc", "subnet", "securitygroup", "kms"],
                enrich=[("VpcTName", "vpc", "get_vpcname", "VpcId"),
                        ("SubnetTName", "subnet", "get_subnetname", "Subnets"),
                        ("ClusterSecurityGroupTName", "securitygroup", "get_sgname", "ClusterSecurityGroupId"),
                        ("EncryptKeyAlias", "kms", "get_keyalias", "EncryptKeyArn")],
                arn_services=["eks"]),
    # EKS 하위 리소스: addon / nodegroup / fargate profile (클러스터 존재 시 수집)
    ServiceSpec("eks_addon", "eks_addon", "REGIONAL", "kskpkg.eks.list_addons", order=33.1,
                depends_on=["eks"], arn_services=["eks"]),
    ServiceSpec("eks_nodegroup", "eks_nodegroup", "REGIONAL", "kskpkg.eks.list_nodegroups", order=33.2,
                depends_on=["eks", "subnet", "securitygroup"],
                enrich=[("SubnetTName", "subnet", "get_subnetname", "Subnets"),
                        ("RemoteAccessSecurityGroupTName", "securitygroup", "get_sgname", "RemoteAccessSecurityGroupId")],
                arn_services=["eks"]),
    ServiceSpec("eks_fargate", "eks_fargate_profile", "REGIONAL", "kskpkg.eks.list_fargate_profiles", order=33.3,
                depends_on=["eks", "subnet"],
                enrich=[("SubnetTName", "subnet", "get_subnetname", "Subnets")],
                arn_services=["eks"]),
    ServiceSpec("ecs",      "ecs",      "REGIONAL", "kskpkg.ecs.list_clusters", order=34,
                arn_services=["ecs"]),
    ServiceSpec("ecs_service", "ecs-service", "REGIONAL", "kskpkg.ecs.list_services", order=35,
                depends_on=["ecs", "subnet", "securitygroup"],
                enrich=[("ECSClusterName", "ecs", "get_ecsclustername", "ClusterArn"),
                        ("SubnetTName", "subnet", "get_subnetname", "SubnetId"),
                        ("SecurityGroupTName", "securitygroup", "get_sgname", "SecurityGroups")],
                arn_services=["ecs"]),
    # ELB 타깃 그룹 + 타깃 그룹 바인딩(등록 타깃/헬스)
    ServiceSpec("elb_targetgroup", "elb_targetgroup", "REGIONAL", "kskpkg.elb.describe_target_groups", order=36,
                depends_on=["vpc", "elb"],
                enrich=[("VpcTName", "vpc", "get_vpcname", "VpcId")],
                arn_services=["elasticloadbalancing"]),
    ServiceSpec("elb_targetbinding", "elb_targetbinding", "REGIONAL", "kskpkg.elb.describe_target_health", order=37,
                depends_on=["instance"],
                enrich=[("TargetTName", "instance", "get_insname", "TargetId")],
                arn_services=["elasticloadbalancing"]),
    # AWS Batch: 컴퓨트 환경 / 작업 큐 / 작업 정의
    ServiceSpec("batch_compute_env", "batch_compute_env", "REGIONAL", "kskpkg.batch.describe_compute_environments", order=38,
                depends_on=["subnet", "securitygroup"],
                enrich=[("SubnetTName", "subnet", "get_subnetname", "Subnets"),
                        ("SecurityGroupTName", "securitygroup", "get_sgname", "SecurityGroupIds")],
                arn_services=["batch"]),
    ServiceSpec("batch_job_queue", "batch_job_queue", "REGIONAL", "kskpkg.batch.describe_job_queues", order=39,
                arn_services=["batch"]),
    ServiceSpec("batch_job_def", "batch_job_definition", "REGIONAL", "kskpkg.batch.describe_job_definitions", order=39.5,
                arn_services=["batch"]),

    # ===== REGIONAL - 스토리지/데이터 =====
    ServiceSpec("efs",      "efs",      "REGIONAL", "kskpkg.efs.describe_file_systems", order=40,
                depends_on=["kms"], enrich=[("KmsKeyAlias", "kms", "get_keyalias", "KmsKeyId")],
                arn_services=["elasticfilesystem"]),
    ServiceSpec("s3",       "s3",       "REGIONAL", "kskpkg.s3.list_buckets", order=41,
                depends_on=["kms"], enrich=[("KMSMasterKeyAlias", "kms", "get_keyalias", "KMSMasterKeyID")],
                arn_services=["s3"]),
    ServiceSpec("ecr",      "ecr",      "REGIONAL", "kskpkg.ecr.describe_repositories", order=42,
                depends_on=["kms"], enrich=[("KmsKeyAlias", "kms", "get_keyalias", "KmsKeyId")],
                arn_services=["ecr"]),
    ServiceSpec("rds",      "rds",      "REGIONAL", "kskpkg.rds.describe_db_clusters", order=43,
                depends_on=["securitygroup", "kms"],
                enrich=[("KmsKeyAlias", "kms", "get_keyalias", "KmsKeyId"),
                        ("VpcSecurityGroupTName", "securitygroup", "get_sgname", "VpcSecurityGroups")],
                arn_services=["rds"]),
    ServiceSpec("redshift", "redshift", "REGIONAL", "kskpkg.redshift.describe_clusters", order=44,
                depends_on=["vpc", "securitygroup", "kms"],
                enrich=[("VpcTName", "vpc", "get_vpcname", "VpcId"),
                        ("KmsKeyAlias", "kms", "get_keyalias", "KmsKeyId"),
                        ("VpcSecurityGroupTName", "securitygroup", "get_sgname", "VpcSecurityGroups")],
                arn_services=["redshift"]),
    ServiceSpec("elasticache", "elasticache", "REGIONAL", "kskpkg.elasticache.describe_cache_clusters", order=45,
                depends_on=["securitygroup"],
                enrich=[("SecurityGroupTName", "securitygroup", "get_sgname", "SecurityGroups")],
                arn_services=["elasticache"]),
    ServiceSpec("dynamodb_tables", "dynamodb_tables", "REGIONAL", "kskpkg.dynamodb.list_tables", order=46,
                arn_services=["dynamodb"]),
    ServiceSpec("dynamodb_gtables", "dynamodb_global_tables", "REGIONAL", "kskpkg.dynamodb.list_global_tables", order=47,
                arn_services=["dynamodb"]),

    # ===== REGIONAL - 메시징/통합 =====
    ServiceSpec("kafka",    "kafka_msk", "REGIONAL", "kskpkg.kafka.list_clusters", order=50,
                depends_on=["subnet", "securitygroup", "kms"],
                enrich=[("ClientSubnetTName", "subnet", "get_subnetname", "ClientSubnets"),
                        ("SecurityGroupTName", "securitygroup", "get_sgname", "SecurityGroupId"),
                        ("DataVolumeKMSTName", "kms", "get_keyalias", "DataVolumeKMSKeyId")],
                arn_services=["kafka"]),
    ServiceSpec("sqs",      "sqs",      "REGIONAL", "kskpkg.sqs.list_queues", order=51,
                arn_services=["sqs"]),
    ServiceSpec("sns",      "sns",      "REGIONAL", "kskpkg.sns.list_topics_with_subscriptions", order=52,
                arn_services=["sns"]),
    ServiceSpec("ses",      "ses",      "REGIONAL", "kskpkg.ses.list_identities", order=53,
                arn_services=["ses"]),

    # ===== REGIONAL - 보안/관리 =====
    ServiceSpec("acm_regional", "acm_regional", "REGIONAL", "kskpkg.acm.list_certificates", order=60,
                arn_services=["acm"]),
    ServiceSpec("secretmanager", "secretmanager", "REGIONAL", "kskpkg.secretsmanager.list_secrets", order=61,
                depends_on=["kms"], enrich=[("KmsKeyAlias", "kms", "get_keyalias", "KmsKeyId")],
                arn_services=["secretsmanager"]),
    ServiceSpec("ssm_params", "ssm_parameterstore", "REGIONAL", "kskpkg.ssm.describe_parameters", order=62,
                arn_services=["ssm"]),
    ServiceSpec("backup",   "backup",   "REGIONAL", "kskpkg.backup.list_backup_plans", order=63,
                arn_services=["backup"]),
    ServiceSpec("backup_vault", "backup_vault", "REGIONAL", "kskpkg.backup.list_backup_vaults", order=64,
                depends_on=["kms"], enrich=[("KmsKeyAlias", "kms", "get_keyalias", "EncryptionKeyArn")],
                arn_services=["backup"]),
    ServiceSpec("waf_regional", "waf_regional", "REGIONAL", "kskpkg.waf.list_web_acls_regional", order=65,
                arn_services=["wafv2", "waf-regional"]),
    ServiceSpec("cloudmap", "cloudmap", "REGIONAL", "kskpkg.servicediscovery.list_namespaces", order=66,
                arn_services=["servicediscovery"]),

    # ===== REGIONAL - 서버리스/인증 =====
    ServiceSpec("lambda",   "lambda",   "REGIONAL", "kskpkg.lambda.list_functions", order=70,
                depends_on=["vpc", "subnet", "securitygroup", "kms"],
                enrich=[("VpcTName", "vpc", "get_vpcname", "VpcId"),
                        ("SubnetTName", "subnet", "get_subnetname", "Subnets"),
                        ("SecurityGroupTName", "securitygroup", "get_sgname", "SecurityGroup"),
                        ("KeyAlias", "kms", "get_keyalias", "KMSKeyArn")],
                arn_services=["lambda"]),
    ServiceSpec("cognito_id_pool", "cognito-federated-id-pool", "REGIONAL", "kskpkg.cognito.list_identity_pools", order=71,
                arn_services=["cognito-identity"]),
    ServiceSpec("cognito_idp", "cognito-user-pool", "REGIONAL", "kskpkg.cognito.list_user_pools", order=72,
                arn_services=["cognito-idp"]),

    # ===== REGIONAL - CICD =====
    ServiceSpec("codecommit", "codecommit", "REGIONAL", "kskpkg.codecommit.list_repositories", order=80,
                arn_services=["codecommit"]),
    ServiceSpec("codebuild", "codebuild", "REGIONAL", "kskpkg.codebuild.list_projects", order=81,
                depends_on=["vpc", "subnet", "securitygroup"],
                enrich=[("VpcTName", "vpc", "get_vpcname", "VpcId"),
                        ("SubnetTName", "subnet", "get_subnetname", "Subnets"),
                        ("SecurityGroupTName", "securitygroup", "get_sgname", "SecurityGroup")],
                arn_services=["codebuild"]),
    ServiceSpec("codedeploy_app", "codedeploy_application", "REGIONAL", "kskpkg.codedeploy.list_applications", order=82,
                arn_services=["codedeploy"]),
    ServiceSpec("codepipeline", "codepipeline", "REGIONAL", "kskpkg.codepipeline.list_pipelines", order=83,
                arn_services=["codepipeline"]),
    ServiceSpec("codedeployment", "codedeploy_deployment", "REGIONAL", "kskpkg.codedeploy.list_deployments", order=84,
                arn_services=["codedeploy"]),

    # ===== REGIONAL - 분석 =====
    ServiceSpec("athena",   "athena",   "REGIONAL", "kskpkg.athena.list_data_catalogs", order=90,
                arn_services=["athena"]),

    # ===== REGIONAL - AI / 신규 서비스 =====
    # Tagging API 커버리지가 불확실한 신규 AI 서비스는 always_collect.
    # 각 모듈이 미지원 리전을 INFO 로 조용히 생략하므로 빈 결과는 emit_empty_sheets 로 제어.
    ServiceSpec("bedrock",  "bedrock",  "REGIONAL", "kskpkg.bedrock.list_custom_models", order=200,
                arn_services=["bedrock"], always_collect=True),
    ServiceSpec("bedrock_guardrail", "bedrock_guardrail", "REGIONAL", "kskpkg.bedrock.list_guardrails", order=201,
                arn_services=["bedrock"], always_collect=True),
    ServiceSpec("bedrock_agentcore_gw", "bedrock_agentcore_gw", "REGIONAL", "kskpkg.bedrock_agentcore.list_gateways", order=205,
                arn_services=["bedrock-agentcore"], always_collect=True),
    ServiceSpec("sagemaker_domain", "sagemaker_domain", "REGIONAL", "kskpkg.sagemaker.list_domains", order=210,
                arn_services=["sagemaker"], always_collect=True),
    ServiceSpec("sagemaker_endpoint", "sagemaker_endpoint", "REGIONAL", "kskpkg.sagemaker.list_endpoints", order=211,
                arn_services=["sagemaker"], always_collect=True),
    ServiceSpec("apigateway_rest", "apigateway_rest", "REGIONAL", "kskpkg.apigateway.get_rest_apis", order=220,
                arn_services=["apigateway"], always_collect=True),
    ServiceSpec("apigateway_v2", "apigateway_v2", "REGIONAL", "kskpkg.apigateway.get_apis_v2", order=221,
                arn_services=["apigateway"], always_collect=True),
]


# ##################################################################################################
# 리포트 비교(diff) 용 key_columns 매핑 (service key -> 식별 컬럼 목록)
#   diff 는 이 컬럼들로 '이전 리포트'와 '현재 리포트'의 행을 매칭하여
#   Added(신규)/Removed(삭제)/Modified(값 변경)를 판정한다.
#   매핑이 없는 서비스는 전체 행 비교(추가/삭제 위주)로 폴백한다.
# ##################################################################################################
_KEY_COLUMNS: dict[str, list[str]] = {
    # 글로벌
    "route53": ["Id"],
    "route53_record": ["HostedZoneId", "Name", "Type"],
    "cloudfront_dist": ["Id"],
    "cloudfront_oid": ["Id"],
    "acm_global": ["CertificateArn"],
    "waf_cloudfront": ["ARN"],
    # 네트워크
    "vpc": ["VpcId"],
    "igw": ["InternetGatewayId"],
    "subnet": ["SubnetId"],
    "kms": ["KeyArn"],
    "securitygroup": ["SGroupId"],
    "eni": ["NetworkInterfaceId"],
    "instance": ["InstanceId"],
    "eip": ["AllocationId"],
    "nat": ["NatGatewayId"],
    "managed_prefixlist": ["PrefixListId"],
    "router": ["RouteTableId"],
    "routeinfo": ["RouteTableId", "DestinationCidrBlock"],
    "vpcendpoint": ["VpcEndpointId"],
    # 컴퓨트/컨테이너
    "elb": ["LoadBalancerArn"],
    "elb_listener": ["ListenerArn"],
    "elb_listener_rule": ["RuleArn"],
    "eks": ["ClusterName"],
    "eks_addon": ["ClusterName", "AddonName"],
    "eks_nodegroup": ["ClusterName", "NodegroupName"],
    "eks_fargate": ["ClusterName", "FargateProfileName"],
    "ecs": ["ClusterArn"],
    "ecs_service": ["ClusterArn", "ServiceName"],
    "elb_targetgroup": ["TargetGroupArn"],
    "elb_targetbinding": ["TargetGroupArn", "TargetId", "Port"],
    "batch_compute_env": ["ComputeEnvironmentArn"],
    "batch_job_queue": ["JobQueueArn"],
    "batch_job_def": ["JobDefinitionArn"],
    # 스토리지/데이터
    "efs": ["FileSystemId"],
    "s3": ["BucketName"],
    "ecr": ["RepositoryName"],
    "rds": ["DBClusterIdentifier"],
    "redshift": ["ClusterIdentifier"],
    "elasticache": ["CacheClusterId"],
    "dynamodb_tables": ["TableName"],
    "dynamodb_gtables": ["GlobalTableName"],
    # 메시징/통합
    "kafka": ["ClusterName"],
    "sqs": ["QueueUrl"],
    "sns": ["TopicArn", "SubscriptionArn"],
    "ses": ["Identity"],
    # 보안/관리
    "acm_regional": ["CertificateArn"],
    "secretmanager": ["ARN"],
    "ssm_params": ["Name"],
    "backup": ["BackupPlanId"],
    "backup_vault": ["BackupVaultName"],
    "waf_regional": ["ARN"],
    "cloudmap": ["Id"],
    # 서버리스/인증
    "lambda": ["FunctionName"],
    "cognito_id_pool": ["IdentityPoolId"],
    "cognito_idp": ["Id"],
    # CICD
    "codecommit": ["RepositoryId"],
    "codebuild": ["ProjectName"],
    "codedeploy_app": ["ApplicationName"],
    "codepipeline": ["Name"],
    "codedeployment": ["DeploymentId"],
    # 분석
    "athena": ["CatalogName"],
    # AI
    "bedrock": ["ModelArn"],
    "bedrock_guardrail": ["Id"],
    "bedrock_agentcore_gw": ["GatewayId", "TargetId"],
    "sagemaker_domain": ["DomainId"],
    "sagemaker_endpoint": ["EndpointArn"],
    "apigateway_rest": ["Id"],
    "apigateway_v2": ["ApiId"],
}

# sheet 이름 -> key_columns (diff 는 sheet 기준으로 매칭)
SHEET_KEY_COLUMNS: dict[str, list[str]] = {}
for _spec in SERVICE_REGISTRY:
    _spec.key_columns = _KEY_COLUMNS.get(_spec.key, [])
    SHEET_KEY_COLUMNS[_spec.sheet] = _spec.key_columns
