# Issue: Upgrade AWS CDK from v1 to v2 and Update All Dependencies

## Summary

This project has been upgraded from AWS CDK v1.122.0 (deprecated) to CDK v2.241.0 with all dependencies updated to their latest versions as of March 2026. This migration was necessary because AWS CDK v1 reached end-of-support and is no longer maintained.

## Motivation

### Why This Upgrade Was Needed

1. **CDK v1 End of Support**: AWS CDK v1 is officially deprecated and no longer receives security updates or bug fixes
2. **Python 3.8 EOL**: Python 3.8 reached end-of-life in October 2024
3. **Security Vulnerabilities**: Unpinned dependencies posed security risks
4. **Missing Features**: CDK v2 includes new features and improvements not available in v1
5. **Community Support**: CDK v1 issues are no longer addressed by AWS

## Changes Made

### 1. AWS CDK Migration (v1.122.0 → v2.241.0)

**Why**: CDK v1 is deprecated and unsupported. CDK v2 consolidates all packages into a single library.

#### Modified Files:

**`setup.py`**
- **Before**: 13 separate CDK packages (`aws-cdk.core`, `aws-cdk.aws_lambda`, etc.)
- **After**: 2 packages (`aws-cdk-lib==2.241.0`, `constructs>=10.0.0`)
- **Why**: CDK v2 uses a monolithic package structure for simpler dependency management

**`requirements.txt`**
```diff
- -e .
+ aws-cdk-lib==2.241.0
+ constructs>=10.0.0,<11.0.0
+ aws-cdk.aws-lambda-python-alpha==2.241.0a0
```
- **Why**: Explicit version pinning prevents dependency conflicts and ensures reproducible builds

**`app.py`**
```diff
- from aws_cdk import core
+ from aws_cdk import App

- app = core.App()
+ app = App()
```
- **Why**: CDK v2 moved core classes to top-level imports

**`lex_sf_drug_reminder_blog/lex_sf_drug_reminder_stack.py`**
```diff
- from aws_cdk import (core,
-                      aws_secretsmanager,
-                      aws_iam,
-                      aws_lambda as _lambda,
-                      aws_lambda_python as lambda_python,
-                      aws_dynamodb,
-                      aws_events,
-                      aws_events_targets,
-                      aws_lambda_event_sources)
+ from aws_cdk import (
+     Stack,
+     RemovalPolicy,
+     Duration,
+     CustomResource,
+     aws_secretsmanager as secretsmanager,
+     aws_iam as iam,
+     aws_lambda as _lambda,
+     aws_dynamodb as dynamodb,
+     aws_events as events,
+     aws_events_targets as events_targets,
+     aws_lambda_event_sources as lambda_event_sources
+ )
+ from constructs import Construct
+ from aws_cdk.aws_lambda_python_alpha import PythonFunction

- class LexSFDCDrugReminderStack(core.Stack):
-     def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
+ class LexSFDCDrugReminderStack(Stack):
+     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
```
- **Why**: CDK v2 reorganized imports and moved `Construct` to separate `constructs` package

**All references updated throughout the file:**
```diff
- core.RemovalPolicy → RemovalPolicy
- core.Duration → Duration
- core.CustomResource → CustomResource
- aws_secretsmanager. → secretsmanager.
- aws_iam. → iam.
- aws_dynamodb. → dynamodb.
- aws_events. → events.
- aws_events_targets. → events_targets.
- aws_lambda_event_sources. → lambda_event_sources.
- lambda_python.PythonFunction → PythonFunction
```
- **Why**: Consistent with CDK v2 naming conventions

**`iot_resources/__init__.py`**
```diff
- from aws_cdk import (
-     core,
-     aws_lambda as _lambda,
-     aws_logs as logs,
-     aws_iam as iam,
-     aws_iot as iot
- )
+ from aws_cdk import (
+     Duration,
+     aws_lambda as _lambda,
+     aws_logs as logs,
+     aws_iam as iam,
+     aws_iot as iot
+ )
+ from constructs import Construct

- class IoTStack(core.Construct):
-     def __init__(self, scope: core.Construct, id: str, ...):
+ class IoTStack(Construct):
+     def __init__(self, scope: Construct, id: str, ...):

- code=_lambda.Code.asset('iot_resources/_lambda')
+ code=_lambda.Code.from_asset('iot_resources/_lambda')
```
- **Why**: CDK v2 API changes and improved naming

**`cdk.json`**
```diff
  {
    "app": "python3 app.py",
    "context": {
-     "@aws-cdk/core:enableStackNameDuplicates": "true",
      "aws-cdk:enableDiffNoFail": "true",
-     "@aws-cdk/core:stackRelativeExports": "true",
      "@aws-cdk/aws-ecr-assets:dockerIgnoreSupport": true,
      "@aws-cdk/aws-secretsmanager:parseOwnedSecretName": true,
      "@aws-cdk/aws-kms:defaultKeyPolicies": true,
      "@aws-cdk/aws-s3:grantWriteWithoutAcl": true
    }
  }
```
- **Why**: Removed deprecated CDK v1 feature flags that cause errors in CDK v2

### 2. Python Runtime Upgrade (3.8 → 3.13)

**Why**: Python 3.8 reached EOL in October 2024 and no longer receives security updates.

**All Lambda Functions Updated:**
```diff
- runtime=_lambda.Runtime.PYTHON_3_8
+ runtime=_lambda.Runtime.PYTHON_3_13
```

**Files Modified:**
- `lex_sf_drug_reminder_blog/lex_sf_drug_reminder_stack.py` (5 Lambda functions)
- `iot_resources/__init__.py` (1 Lambda function)

**Benefits:**
- Security patches and bug fixes
- Performance improvements
- Support until October 2028
- New Python language features

### 3. Lambda Dependencies Updated

**Why**: Unpinned dependencies can introduce breaking changes and security vulnerabilities.

**`lex_sf_drug_reminder_blog/_lambda/functions/connect_import_flow/requirements.txt`**
```diff
- requests
+ requests==2.32.5
```

**`lex_sf_drug_reminder_blog/_lambda/functions/lex_fulfillment/requirements.txt`**
```diff
- requests
- simple-salesforce
+ requests==2.32.5
+ simple-salesforce==1.12.9
```

**`lex_sf_drug_reminder_blog/_lambda/functions/lex_operator/requirements.txt`**
```diff
- requests
+ requests==2.32.5
```

**`lex_sf_drug_reminder_blog/_lambda/functions/sfdc_fetch/requirements.txt`**
```diff
- requests
- simple-salesforce
- dynamodb-json
+ requests==2.32.5
+ simple-salesforce==1.12.9
+ dynamodb-json==1.4.2
```

**Benefits:**
- Reproducible builds
- Security vulnerability tracking
- Prevents unexpected breaking changes

### 4. Python Version Requirements

**`setup.py`**
```diff
- python_requires=">=3.6"
+ python_requires=">=3.9"

  classifiers=[
      ...
-     "Programming Language :: Python :: 3.6",
-     "Programming Language :: Python :: 3.7",
-     "Programming Language :: Python :: 3.8",
+     "Programming Language :: Python :: 3.9",
+     "Programming Language :: Python :: 3.10",
+     "Programming Language :: Python :: 3.11",
+     "Programming Language :: Python :: 3.12",
+     "Programming Language :: Python :: 3.13",
  ]
```
- **Why**: CDK v2 requires Python 3.7+, but Python 3.9+ is recommended for modern features

## Dependency Version Summary

| Package | Old Version | New Version | Reason |
|---------|-------------|-------------|--------|
| aws-cdk-lib | 1.122.0 (as aws-cdk.*) | 2.241.0 | CDK v1 deprecated |
| constructs | 3.3.69 | 10.5.1 | Required by CDK v2 |
| requests | unpinned | 2.32.5 | Security & stability |
| simple-salesforce | unpinned | 1.12.9 | Security & stability |
| dynamodb-json | unpinned | 1.4.2 | Security & stability |
| Python Runtime | 3.8 | 3.13 | Python 3.8 EOL |

## Breaking Changes

### For Developers

1. **Virtual Environment Must Be Recreated**
   ```bash
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Docker Required for Deployment**
   - `PythonFunction` uses Docker to bundle Lambda dependencies
   - Ensures Linux compatibility for Lambda runtime
   - Docker Desktop must be running for `cdk synth` and `cdk deploy`

3. **Import Statements Changed**
   - If you have custom constructs, update imports to CDK v2 style
   - `from aws_cdk import core` → `from aws_cdk import Stack, Duration, etc.`
   - `from constructs import Construct` is now required

### For Deployment

1. **Bootstrap May Be Required**
   ```bash
   cdk bootstrap
   ```
   - CDK v2 uses a different bootstrap stack version

2. **No Code Changes to Lambda Functions**
   - Lambda function code remains unchanged
   - Only runtime version updated (3.8 → 3.13)

## Testing Performed

### Compilation Tests ✅
- [x] Python syntax validation passed
- [x] All imports resolve correctly
- [x] Type hints validated
- [x] No syntax errors

### CDK Synthesis ✅
- [x] `cdk synth` completes successfully (with Docker running)
- [x] CloudFormation templates generated
- [x] All resources defined correctly

### What Still Needs Testing
- [ ] Deploy to development environment
- [ ] Test Lambda functions with Python 3.13 runtime
- [ ] Verify IoT topic rules work correctly
- [ ] Test Lex bot integration
- [ ] Test Connect flow integration
- [ ] Verify Salesforce integration
- [ ] End-to-end testing of drug reminder flow

## Migration Guide

### For New Deployments

1. **Prerequisites**
   - Python 3.9 or higher
   - Node.js 18+ (for CDK CLI)
   - Docker Desktop installed and running
   - AWS CLI configured

2. **Installation**
   ```bash
   # Clone repository
   git clone <repo-url>
   cd iot-connect-drug-reminder-blog
   
   # Create virtual environment
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install --upgrade pip
   pip install -r requirements.txt
   
   # Install CDK CLI globally
   npm install -g aws-cdk
   
   # Verify installation
   cdk --version  # Should show 2.241.0
   ```

3. **Configure Environment**
   ```bash
   # Edit env.sh with your values
   vi env.sh
   
   # Source environment variables
   source env.sh
   ```

4. **Bootstrap CDK (first time only)**
   ```bash
   cdk bootstrap
   ```

5. **Deploy**
   ```bash
   # Start Docker Desktop first!
   cdk synth
   cdk deploy
   ```

### For Existing Deployments

1. **Backup Current Stack**
   ```bash
   aws cloudformation describe-stacks \
     --stack-name lex-sfdc-drug-reminder-blog \
     > stack-backup.json
   ```

2. **Update Code**
   ```bash
   git pull origin main
   ```

3. **Recreate Virtual Environment**
   ```bash
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Review Changes**
   ```bash
   source env.sh
   cdk diff
   ```

5. **Deploy Update**
   ```bash
   cdk deploy
   ```

## Rollback Plan

If issues occur after deployment:

1. **Revert Code Changes**
   ```bash
   git revert <commit-hash>
   ```

2. **Redeploy Previous Version**
   ```bash
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cdk deploy
   ```

3. **Or Use CloudFormation Rollback**
   ```bash
   aws cloudformation rollback-stack \
     --stack-name lex-sfdc-drug-reminder-blog
   ```

## Known Issues

### Docker Requirement
- **Issue**: `cdk synth` fails if Docker is not running
- **Error**: `docker exited with status 1`
- **Solution**: Start Docker Desktop before running CDK commands
- **Alternative**: Use standard `_lambda.Function` instead of `PythonFunction` (requires manual dependency management)

### Python 3.13 Compatibility
- **Issue**: Some Python packages may not have Python 3.13 wheels yet
- **Impact**: Slower Lambda cold starts during dependency installation
- **Mitigation**: All dependencies in this project are confirmed compatible

## References

- [AWS CDK v2 Migration Guide](https://docs.aws.amazon.com/cdk/v2/guide/migrating-v2.html)
- [AWS CDK v1 End of Support Announcement](https://aws.amazon.com/blogs/devops/cdk-v1-end-of-support/)
- [Python 3.8 EOL Notice](https://devguide.python.org/versions/)
- [AWS Lambda Python 3.13 Runtime](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)

## Additional Documentation

See also:
- `UPGRADE_NOTES.md` - Detailed technical upgrade notes
- `README.md` - Updated deployment instructions

## Checklist for Reviewers

- [ ] Review all code changes
- [ ] Verify CDK v2 best practices followed
- [ ] Check security implications of dependency updates
- [ ] Validate Python 3.13 compatibility
- [ ] Test deployment in development environment
- [ ] Update CI/CD pipelines if applicable
- [ ] Update documentation
- [ ] Notify team of breaking changes

---

**Issue Type**: Enhancement, Breaking Change  
**Priority**: High  
**Labels**: cdk-v2, migration, dependencies, breaking-change, python-3.13  
**Milestone**: Q1 2026 Maintenance
