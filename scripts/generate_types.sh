#!/usr/bin/env bash
# Generate the committed TypeScript and C# types from the canonical JSON Schema.
#
# Usage:  ./scripts/generate_types.sh
# Requires Node (npx). Uses quicktype, which reads JSON Schema and targets both
# TS and C# from a single tool (ecosystem-research §3). C# output uses
# Newtonsoft.Json, which the .NET occultation world is comfortable with.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCHEMA="$ROOT/schema/iota-report.schema.json"
TS_OUT="$ROOT/generated/typescript/iota-report.ts"
CS_OUT="$ROOT/generated/csharp/IotaReport.cs"

mkdir -p "$(dirname "$TS_OUT")" "$(dirname "$CS_OUT")"

echo "Generating TypeScript -> $TS_OUT"
npx --yes quicktype \
  --src-lang schema \
  --src "$SCHEMA" \
  --lang ts \
  --just-types \
  -o "$TS_OUT"

echo "Generating C# -> $CS_OUT"
npx --yes quicktype \
  --src-lang schema \
  --src "$SCHEMA" \
  --lang cs \
  --namespace IotaReport \
  -o "$CS_OUT"

echo "Done."
