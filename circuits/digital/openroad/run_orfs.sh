#!/usr/bin/env bash
# Install the ADAMAS-PDK-0 platform and the DIA-4 design into an OpenROAD-flow-scripts checkout and run the flow in Docker.
# Usage (from the repository root, in WSL, NOT inside a container):  bash circuits/digital/openroad/run_orfs.sh [ORFS_DIR]
set -euo pipefail
ORFS="${1:-$HOME/orfs}"
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
[ -d "$ORFS/flow" ] || git clone --depth 1 https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts "$ORFS"
python -c "from adamas.orfs_platform import write; write('$ORFS/flow/platforms/adamas_pdk0')"
mkdir -p "$ORFS/flow/designs/adamas/dia4"
cp "$ROOT/circuits/digital/dia4.v" "$ROOT/circuits/digital/openroad/config.mk" "$ROOT/circuits/digital/openroad/constraint.sdc" "$ORFS/flow/designs/adamas/dia4/"
rm -rf "$ORFS/flow/logs/adamas_pdk0" "$ORFS/flow/objects/adamas_pdk0" "$ORFS/flow/results/adamas_pdk0" "$ORFS/flow/reports/adamas_pdk0"
docker run --rm -u "$(id -u):$(id -g)" -v "$ORFS/flow:/OpenROAD-flow-scripts/flow" openroad/orfs \
  bash -c "cd /OpenROAD-flow-scripts/flow && make DESIGN_CONFIG=designs/adamas/dia4/config.mk" 2>&1 | tee "$ROOT/circuits/digital/openroad/last_run.log" | tail -60
echo "---- summary ----"
ls "$ORFS/flow/results/adamas_pdk0/dia4/base/" 2>/dev/null || true
for f in 6_report.log 6_finish.rpt; do r=$(find "$ORFS/flow/reports/adamas_pdk0/dia4/base" "$ORFS/flow/logs/adamas_pdk0/dia4/base" -name "$f" 2>/dev/null | head -1); [ -n "$r" ] && grep -E "wns|tns|slack|Design area|utilization|wire length|Total power" "$r" | head -20; done
