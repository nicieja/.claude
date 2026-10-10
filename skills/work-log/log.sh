#!/usr/bin/env bash
# Append one row to a decision log (TSV).
# Usage: log.sh <logfile> <phase> <decision> <why> <evidence> <result>
#
# Ported from show-me-your-work/scripts/log.sh in Lauren Tan's pstack (MIT).
# It stamps the time, writes the header on first use, keeps every cell on one
# line, and quotes a cell a spreadsheet would read as a formula.
set -euo pipefail

if [ "$#" -ne 6 ]; then
	printf 'usage: log.sh <logfile> <phase> <decision> <why> <evidence> <result>\n' >&2
	exit 1
fi

logfile="$1"
shift
mkdir -p "$(dirname "$logfile")"

if [ ! -s "$logfile" ]; then
	printf 'ts\tphase\tdecision\twhy\tevidence\tresult\n' >> "$logfile"
fi

clean() {
	local v
	v=$(printf '%s' "$1" | tr '\t\n\r' '   ')
	case "$v" in
		=*|+*|-*|@*) printf "'%s" "$v" ;;
		*) printf '%s' "$v" ;;
	esac
}

printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
	"$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(clean "$1")" "$(clean "$2")" "$(clean "$3")" "$(clean "$4")" "$(clean "$5")" \
	>> "$logfile"
