#!/usr/bin/env bash
# Screening tool: filters traces with LLC MPKI > 1.0
TRACE_DIR=${1:-"traces"}
CHAMPSIM_BIN=${2:-"bin/champsim"}

echo "Scanning traces in $TRACE_DIR for LLC MPKI > 1.0..."
echo "Trace Name | Total Misses | LLC MPKI | Status"
echo "------------------------------------------------"

for trace in "$TRACE_DIR"/*.champsimtrace.xz; do
    [ -e "$trace" ] || continue
    trace_name=$(basename "$trace")
    output=$("$CHAMPSIM_BIN" --warmup_instructions 5000000 --simulation_instructions 10000000 "$trace" 2>/dev/null)
    
    misses=$(echo "$output" | grep "LLC TOTAL" | awk '{for(i=1;i<=NF;i++) if($i=="MISS:") print $(i+1)}')
    if [ -n "$misses" ]; then
        mpki=$(awk "BEGIN {printf \"%.2f\", $misses / 10000}")
        status=$(awk "BEGIN {if ($mpki >= 1.0) print \"KEEP (>1.0)\"; else print \"DROP\"}")
        echo "$trace_name | $misses | $mpki | $status"
    fi
done
