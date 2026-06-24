#!/bin/sh
# Per-seed worker for the locked decoupling-control run (v0.7.0). One seed per process,
# thread-capped to 1 core, atomic + resumable: skips a seed whose JSON already exists, writes
# to a .tmp and renames on success so a crash/restart never leaves a partial file as "done".
cd /Users/benjamin/Projects/coherence-information || exit 1
. .venv/bin/activate
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1

seed="$1"
d=results/decoupling_control
out="$d/seed_${seed}.json"
log="$d/progress.log"

[ -s "$out" ] && { echo "$(date '+%H:%M:%S') skip $seed (exists)" >> "$log"; exit 0; }

start=$(date +%s)
echo "$(date '+%H:%M:%S') START $seed" >> "$log"
if python scripts/run_decoupling_control.py --T 50000 --seeds "$seed" > "$out.tmp" 2> "$d/seed_${seed}.err"; then
    mv "$out.tmp" "$out"
    echo "$(date '+%H:%M:%S') DONE  $seed ($(( ($(date +%s)-start)/60 ))min)" >> "$log"
else
    echo "$(date '+%H:%M:%S') FAIL  $seed (see seed_${seed}.err)" >> "$log"
fi
