#!/usr/bin/env bash
# Run the complete demo against a backend already running on localhost:8000.
# Usage: ./run_demo.sh <SUPABASE_ACCESS_TOKEN>

set -euo pipefail

if [[ $# -ne 1 || -z "${1:-}" ]]; then
  echo "Usage: ./run_demo.sh <SUPABASE_ACCESS_TOKEN>"
  exit 1
fi

TOKEN="$1"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
API="${API_BASE_URL:-http://localhost:8000}"
DATASET="$SCRIPT_DIR/sample_data/demo.csv"

echo "Checking backend..."
curl --fail --silent --show-error "$API/health" >/dev/null
echo "Backend is healthy."

echo "Uploading $DATASET..."
UPLOAD_RESPONSE="$(
  curl --fail --silent --show-error     -X POST "$API/upload"     -H "Authorization: Bearer $TOKEN"     -F "file=@$DATASET"
)"
echo "$UPLOAD_RESPONSE" | python3 -m json.tool

RUN_ID="$(
  echo "$UPLOAD_RESPONSE" |
    python3 -c 'import json,sys; print(json.load(sys.stdin)["run_id"])'
)"

echo "Running checks for run_id=$RUN_ID..."
curl --fail --silent --show-error   -X POST "$API/checks/run"   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d "{"run_id":"$RUN_ID","expected_columns":["name","age","email"],"custom_rule":{"column":"age","type":"range","min":0,"max":120}}" |
  python3 -m json.tool
