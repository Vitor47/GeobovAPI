#!/usr/bin/env bash
# Publish the fixed deploy command to AWS. Run this with an admin login.
# The GitHub deploy role is not allowed to publish or edit the document.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT="${ROOT_DIR}/deploy/aws/ssm/deploy.sh"
export AWS_DEFAULT_REGION="${AWS_REGION:-sa-east-1}"
NAME="GeoBovDeploy"

python3 - "${SCRIPT}" <<'PY' > /tmp/geobov-deploy-document.json
import json
import pathlib
import sys

script = pathlib.Path(sys.argv[1]).read_text()
document = {
    "schemaVersion": "2.2",
    "description": "Apply one GeoBov release artifact. Switches are true or false.",
    "parameters": {
        name: {
            "type": "String",
            "allowedValues": ["true", "false"],
            "default": "false",
        }
        for name in (
            "updateApi",
            "updatePostgres",
            "updateRedis",
            "updateMongo",
            "runMigrations",
        )
    },
    "mainSteps": [
        {
            "action": "aws:runShellScript",
            "name": "deploy",
            "precondition": {"StringEquals": ["platformType", "Linux"]},
            "inputs": {"timeoutSeconds": "1500", "runCommand": [script]},
        }
    ],
}
json.dump(document, sys.stdout)
PY

if aws ssm describe-document --name "${NAME}" >/dev/null 2>&1; then
  VERSION="$(aws ssm update-document \
    --name "${NAME}" \
    --content "file:///tmp/geobov-deploy-document.json" \
    --document-version "\$LATEST" \
    --query 'DocumentDescription.DocumentVersion' \
    --output text)"
  aws ssm update-document-default-version \
    --name "${NAME}" \
    --document-version "${VERSION}" >/dev/null
  echo "Updated ${NAME} to version ${VERSION}"
else
  aws ssm create-document \
    --name "${NAME}" \
    --document-type Command \
    --content "file:///tmp/geobov-deploy-document.json" >/dev/null
  echo "Created ${NAME}"
fi

rm -f /tmp/geobov-deploy-document.json
