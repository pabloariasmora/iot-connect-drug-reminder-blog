# Dependency Upgrade Notes

## Summary of Changes

This project has been upgraded from AWS CDK v1 to v2 with all dependencies updated to their latest versions as of March 2026.

## Major Changes

### 1. AWS CDK Migration (v1.122.0 → v2.241.0)

**Breaking Changes:**
- CDK v1 used separate packages (`aws-cdk.core`, `aws-cdk.aws_lambda`, etc.)
- CDK v2 consolidates everything into `aws-cdk-lib` and `constructs`
- Import statements have changed significantly

**Updated Files:**
- `setup.py` - Simplified dependencies to use `aws-cdk-lib` and `constructs`
- `app.py` - Changed `from aws_cdk import core` to `from aws_cdk import App`
- `lex_sf_drug_reminder_blog/lex_sf_drug_reminder_stack.py` - Updated all imports
- `iot_resources/__init__.py` - Updated imports and added `Construct` from `constructs`

### 2. Python Runtime Upgrade (3.8 → 3.13)

All Lambda functions now use Python 3.13 runtime:
- `_lambda.Runtime.PYTHON_3_8` → `_lambda.Runtime.PYTHON_3_13`

**Note:** Python 3.8 reaches end of life in October 2024, so upgrading to 3.13 ensures long-term support.

### 3. Lambda Dependencies Updated

All Lambda function requirements files updated with pinned versions:

| Package | Old Version | New Version |
|---------|-------------|-------------|
| requests | unpinned | 2.32.5 |
| simple-salesforce | unpinned | 1.12.9 |
| dynamodb-json | unpinned | 1.4.2 |

### 4. Python Version Requirements

- Minimum Python version: 3.6 → 3.9
- Added support for Python 3.9, 3.10, 3.11, 3.12, 3.13

## Installation Instructions

1. **Clean existing virtual environment:**
   ```bash
   rm -rf .venv
   ```

2. **Create new virtual environment with Python 3.9+:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install updated dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Verify CDK installation:**
   ```bash
   cdk --version
   # Should show: 2.241.0 (build ...)
   ```

5. **Bootstrap CDK v2 (if not already done):**
   ```bash
   source env.sh
   cdk bootstrap
   ```

6. **Synthesize and deploy:**
   ```bash
   source env.sh
   cdk synth
   cdk deploy
   ```

## Key Import Changes

### Before (CDK v1):
```python
from aws_cdk import core
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_lambda_python as lambda_python

class MyStack(core.Stack):
    def __init__(self, scope: core.Construct, ...):
        super().__init__(scope, construct_id, **kwargs)
```

### After (CDK v2):
```python
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda
)
from constructs import Construct
from aws_cdk.aws_lambda_python_alpha import PythonFunction

class MyStack(Stack):
    def __init__(self, scope: Construct, ...):
        super().__init__(scope, construct_id, **kwargs)
```

## Notable API Changes

1. **RemovalPolicy**: `core.RemovalPolicy` → `RemovalPolicy`
2. **Duration**: `core.Duration` → `Duration`
3. **CustomResource**: `core.CustomResource` → `CustomResource`
4. **PythonFunction**: Now imported from `aws_cdk.aws_lambda_python_alpha`
5. **Code.asset()**: Changed to `Code.from_asset()`

## Testing Recommendations

After upgrading, test the following:

1. **CDK Synthesis:**
   ```bash
   cdk synth
   ```
   Should complete without errors.

2. **Lambda Functions:**
   - Verify all Lambda functions deploy successfully
   - Test each Lambda function individually
   - Check CloudWatch logs for any runtime errors

3. **IoT Integration:**
   - Test IoT topic rule triggers
   - Verify DynamoDB updates from IoT events

4. **Lex Bot:**
   - Verify Lex bot deployment
   - Test conversation flows

5. **Connect Integration:**
   - Test outbound calling functionality
   - Verify Connect flow integration

## Rollback Instructions

If you need to rollback to CDK v1:

1. Restore original files from git:
   ```bash
   git checkout HEAD -- setup.py app.py requirements.txt
   git checkout HEAD -- lex_sf_drug_reminder_blog/
   git checkout HEAD -- iot_resources/
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Additional Resources

- [AWS CDK v2 Migration Guide](https://docs.aws.amazon.com/cdk/v2/guide/migrating-v2.html)
- [AWS CDK v2 API Reference](https://docs.aws.amazon.com/cdk/api/v2/)
- [Python 3.13 Release Notes](https://docs.python.org/3.13/whatsnew/3.13.html)

## Support

For issues related to this upgrade, please check:
1. AWS CDK GitHub Issues
2. AWS Developer Forums
3. Project README.md for deployment instructions
