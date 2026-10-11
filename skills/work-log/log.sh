#!/usr/bin/env bash
# Append one decision to a run's TSV log, writing the header first when the log is new.
# Usage: log.sh <logfile> <phase> <decision> <why> <evidence> <result>
set -euo pipefail

if [ "$#" -ne 6 ]; then
	echo "usage: log.sh <logfile> <phase> <decision> <why> <evidence> <result>" >&2
	exit 1
fi

log=$1
shift
mkdir -p "$(dirname "$log")"
[ -s "$log" ] || printf 'ts\tphase\tdecision\twhy\tevidence\tresult\n' > "$log"

row=$(date -u +%Y-%m-%dT%H:%M:%SZ)
for cell in "$@"; do
	cell=${cell//[$'\t\r\n']/ }
	case $cell in [=+@-]*) cell="'$cell" ;; esac
	row+=$'\t'$cell
done
printf '%s\n' "$row" >> "$log"
