import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { AiDomainTraderStack } from '../lib/ai-domain-trader-stack';
const app = new cdk.App();
new AiDomainTraderStack(app, 'AiDomainTraderStack', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION }
});
