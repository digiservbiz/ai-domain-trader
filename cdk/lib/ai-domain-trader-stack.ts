import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as elasticache from 'aws-cdk-lib/aws-elasticache';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as acm from 'aws-cdk-lib/aws-certificatemanager';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';

export class AiDomainTraderStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, 'Vpc', {
      maxAzs: 2,
      natGateways: 1,
      subnetConfiguration: [
        { name: 'Public', subnetType: ec2.SubnetType.PUBLIC, cidrMask: 24 },
        { name: 'Private', subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS, cidrMask: 24 },
      ],
    });

    const albSg = new ec2.SecurityGroup(this, 'AlbSg', { vpc, allowAllOutbound: true });
    albSg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(80));
    albSg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(443));

    const backendSg = new ec2.SecurityGroup(this, 'BackendSg', { vpc, allowAllOutbound: true });
    backendSg.addIngressRule(albSg, ec2.Port.tcp(8000));

    const frontendSg = new ec2.SecurityGroup(this, 'FrontendSg', { vpc, allowAllOutbound: true });
    frontendSg.addIngressRule(albSg, ec2.Port.tcp(3000));

    const rdsSg = new ec2.SecurityGroup(this, 'RdsSg', { vpc, allowAllOutbound: false });
    rdsSg.addIngressRule(backendSg, ec2.Port.tcp(5432));

    const redisSg = new ec2.SecurityGroup(this, 'RedisSg', { vpc, allowAllOutbound: false });
    redisSg.addIngressRule(backendSg, ec2.Port.tcp(6379));

    const backendRepo = new ecr.Repository(this, 'BackendRepo', {
      repositoryName: 'ai-domain-trader/backend',
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    const frontendRepo = new ecr.Repository(this, 'FrontendRepo', {
      repositoryName: 'ai-domain-trader/frontend',
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    const appSecret = new secretsmanager.Secret(this, 'AppSecret', {
      secretName: 'ai-domain-trader/env',
      generateSecretString: {
        secretStringTemplate: JSON.stringify({
          DATABASE_URL: '',
          REDIS_URL: '',
          SECRET_KEY: '',
          GODADDY_KEY: '',
          GODADDY_SECRET: '',
          OPENROUTER_API_KEY: '',
          MOZ_ACCESS_ID: '',
          MOZ_SECRET_KEY: '',
        }),
        generateStringKey: '_placeholder',
      },
    });

    const dbSubnetGroup = new rds.SubnetGroup(this, 'DbSubnetGroup', {
      vpc,
      description: 'RDS subnet group',
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
    });

    const db = new rds.DatabaseInstance(this, 'Db', {
      engine: rds.DatabaseInstanceEngine.postgres({ version: rds.PostgresEngineVersion.VER_15 }),
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
      vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
      subnetGroup: dbSubnetGroup,
      securityGroups: [rdsSg],
      storageEncrypted: true,
      deletionProtection: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      databaseName: 'aidomaintrader',
    });

    const cacheSubnetGroup = new elasticache.CfnSubnetGroup(this, 'CacheSubnetGroup', {
      description: 'ElastiCache subnet group',
      subnetIds: vpc.selectSubnets({ subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS }).subnetIds,
      cacheSubnetGroupName: 'ai-domain-trader-cache',
    });

    const redis = new elasticache.CfnReplicationGroup(this, 'Redis', {
      replicationGroupDescription: 'ai-domain-trader Redis',
      cacheNodeType: 'cache.t3.micro',
      engine: 'redis',
      numCacheClusters: 1,
      cacheSubnetGroupName: cacheSubnetGroup.ref,
      securityGroupIds: [redisSg.securityGroupId],
      atRestEncryptionEnabled: true,
      transitEncryptionEnabled: false,
    });
    redis.addDependency(cacheSubnetGroup);

    const cluster = new ecs.Cluster(this, 'Cluster', { vpc });

    const taskRole = new iam.Role(this, 'TaskRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
    });
    appSecret.grantRead(taskRole);

    const executionRole = new iam.Role(this, 'ExecutionRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonECSTaskExecutionRolePolicy'),
      ],
    });
    appSecret.grantRead(executionRole);

    const containerSecrets: Record<string, ecs.Secret> = {
      DATABASE_URL: ecs.Secret.fromSecretsManager(appSecret, 'DATABASE_URL'),
      REDIS_URL: ecs.Secret.fromSecretsManager(appSecret, 'REDIS_URL'),
      SECRET_KEY: ecs.Secret.fromSecretsManager(appSecret, 'SECRET_KEY'),
      GODADDY_KEY: ecs.Secret.fromSecretsManager(appSecret, 'GODADDY_KEY'),
      GODADDY_SECRET: ecs.Secret.fromSecretsManager(appSecret, 'GODADDY_SECRET'),
      OPENROUTER_API_KEY: ecs.Secret.fromSecretsManager(appSecret, 'OPENROUTER_API_KEY'),
      MOZ_ACCESS_ID: ecs.Secret.fromSecretsManager(appSecret, 'MOZ_ACCESS_ID'),
      MOZ_SECRET_KEY: ecs.Secret.fromSecretsManager(appSecret, 'MOZ_SECRET_KEY'),
    };

    const privateSubnets = { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS };

    const backendTaskDef = new ecs.FargateTaskDefinition(this, 'BackendTaskDef', {
      cpu: 512,
      memoryLimitMiB: 1024,
      taskRole,
      executionRole,
    });
    backendTaskDef.addContainer('backend', {
      image: ecs.ContainerImage.fromEcrRepository(backendRepo, 'latest'),
      portMappings: [{ containerPort: 8000 }],
      secrets: containerSecrets,
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'backend',
        logGroup: new logs.LogGroup(this, 'BackendLogs', { removalPolicy: cdk.RemovalPolicy.DESTROY }),
      }),
    });

    const frontendTaskDef = new ecs.FargateTaskDefinition(this, 'FrontendTaskDef', {
      cpu: 256,
      memoryLimitMiB: 512,
      taskRole,
      executionRole,
    });
    frontendTaskDef.addContainer('frontend', {
      image: ecs.ContainerImage.fromEcrRepository(frontendRepo, 'latest'),
      portMappings: [{ containerPort: 3000 }],
      secrets: containerSecrets,
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'frontend',
        logGroup: new logs.LogGroup(this, 'FrontendLogs', { removalPolicy: cdk.RemovalPolicy.DESTROY }),
      }),
    });

    const celeryWorkerTaskDef = new ecs.FargateTaskDefinition(this, 'CeleryWorkerTaskDef', {
      cpu: 512,
      memoryLimitMiB: 1024,
      taskRole,
      executionRole,
    });
    celeryWorkerTaskDef.addContainer('celery-worker', {
      image: ecs.ContainerImage.fromEcrRepository(backendRepo, 'latest'),
      command: ['celery', '-A', 'app.celery', 'worker', '--loglevel=info'],
      secrets: containerSecrets,
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'celery-worker',
        logGroup: new logs.LogGroup(this, 'CeleryWorkerLogs', { removalPolicy: cdk.RemovalPolicy.DESTROY }),
      }),
    });

    const celeryBeatTaskDef = new ecs.FargateTaskDefinition(this, 'CeleryBeatTaskDef', {
      cpu: 256,
      memoryLimitMiB: 512,
      taskRole,
      executionRole,
    });
    celeryBeatTaskDef.addContainer('celery-beat', {
      image: ecs.ContainerImage.fromEcrRepository(backendRepo, 'latest'),
      command: ['celery', '-A', 'app.celery', 'beat', '--loglevel=info'],
      secrets: containerSecrets,
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'celery-beat',
        logGroup: new logs.LogGroup(this, 'CeleryBeatLogs', { removalPolicy: cdk.RemovalPolicy.DESTROY }),
      }),
    });

    const alb = new elbv2.ApplicationLoadBalancer(this, 'Alb', {
      vpc,
      internetFacing: true,
      securityGroup: albSg,
    });

    const httpListener = alb.addListener('HttpListener', {
      port: 80,
      defaultAction: elbv2.ListenerAction.redirect({
        protocol: 'HTTPS',
        port: '443',
        permanent: true,
      }),
    });
    void httpListener;

    const certificateArn = this.node.tryGetContext('certificateArn') as string;
    const certificate = acm.Certificate.fromCertificateArn(this, 'Cert', certificateArn);

    const backendTg = new elbv2.ApplicationTargetGroup(this, 'BackendTg', {
      vpc,
      port: 8000,
      protocol: elbv2.ApplicationProtocol.HTTP,
      targetType: elbv2.TargetType.IP,
      healthCheck: { path: '/health', interval: cdk.Duration.seconds(30) },
    });

    const frontendTg = new elbv2.ApplicationTargetGroup(this, 'FrontendTg', {
      vpc,
      port: 3000,
      protocol: elbv2.ApplicationProtocol.HTTP,
      targetType: elbv2.TargetType.IP,
      healthCheck: { path: '/', interval: cdk.Duration.seconds(30) },
    });

    const httpsListener = alb.addListener('HttpsListener', {
      port: 443,
      certificates: [certificate],
      defaultTargetGroups: [frontendTg],
    });

    httpsListener.addTargetGroups('ApiRoute', {
      targetGroups: [backendTg],
      priority: 10,
      conditions: [
        elbv2.ListenerCondition.pathPatterns(['/api/*', '/ws/*']),
      ],
    });

    const backendService = new ecs.FargateService(this, 'BackendService', {
      cluster,
      taskDefinition: backendTaskDef,
      desiredCount: 1,
      assignPublicIp: false,
      vpcSubnets: privateSubnets,
      securityGroups: [backendSg],
    });
    backendService.attachToApplicationTargetGroup(backendTg);

    const frontendService = new ecs.FargateService(this, 'FrontendService', {
      cluster,
      taskDefinition: frontendTaskDef,
      desiredCount: 1,
      assignPublicIp: false,
      vpcSubnets: privateSubnets,
      securityGroups: [frontendSg],
    });
    frontendService.attachToApplicationTargetGroup(frontendTg);

    new ecs.FargateService(this, 'CeleryWorkerService', {
      cluster,
      taskDefinition: celeryWorkerTaskDef,
      desiredCount: 1,
      assignPublicIp: false,
      vpcSubnets: privateSubnets,
      securityGroups: [backendSg],
    });

    new ecs.FargateService(this, 'CeleryBeatService', {
      cluster,
      taskDefinition: celeryBeatTaskDef,
      desiredCount: 1,
      assignPublicIp: false,
      vpcSubnets: privateSubnets,
      securityGroups: [backendSg],
    });

    void db;
    void redis;

    new cdk.CfnOutput(this, 'AlbDnsName', { value: alb.loadBalancerDnsName });
  }
}
