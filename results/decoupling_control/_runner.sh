#!/bin/sh
# Detached orchestrator for the locked decoupling-control run (v0.7.0). Spawned via setsid so it
# survives the launching shell / harness reaping; dispatches the 20 seeds P=10 across cores
# (each worker thread-capped + resumable), then merges the per-seed Deltas into verdict.json.
cd /Users/benjamin/Projects/coherence-information || exit 1
. .venv/bin/activate
d=results/decoupling_control

echo "LAUNCH(detached) $(date '+%Y-%m-%d %H:%M:%S') P=10 T=50000 seeds 7000-7019" >> "$d/progress.log"
seq 7000 7019 | xargs -P 10 -n 1 sh "$d/_worker.sh"
echo "ALL SEEDS COMPLETE $(date '+%Y-%m-%d %H:%M:%S') -- merging" >> "$d/progress.log"

if python "$d/_merge.py" > "$d/verdict.json.tmp" 2>> "$d/progress.log"; then
    mv "$d/verdict.json.tmp" "$d/verdict.json"
    echo "VERDICT WRITTEN $(date '+%Y-%m-%d %H:%M:%S')" >> "$d/progress.log"
else
    echo "MERGE FAILED $(date '+%Y-%m-%d %H:%M:%S')" >> "$d/progress.log"
fi
