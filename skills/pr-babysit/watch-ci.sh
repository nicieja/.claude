#!/usr/bin/env bash
# Poll a pull request's checks on its current head until they reach a verdict.
# Usage: watch-ci.sh [--once] [--interval S] [--timeout S] [--expect NAME]... <pr>
# <pr> is a number or branch in the current checkout's repo, or a full PR URL.
# Exit: 0 green or merged, 1 failed, conflicting, closed, or a gh error,
# 2 pending under --once or past --timeout, 64 usage error.
set -euo pipefail

usage() {
	echo "usage: watch-ci.sh [--once] [--interval S] [--timeout S] [--expect NAME]... <pr>" >&2
	exit 64
}

once=false
interval=30
timeout=
expect=
pr=
while [ "$#" -gt 0 ]; do
	case $1 in
		--once) once=true ;;
		--interval | --timeout | --expect)
			[ "$#" -ge 2 ] || usage
			case $1 in
				--interval) interval=$2 ;;
				--timeout) timeout=$2 ;;
				--expect) expect+=$2$'\n' ;;
			esac
			shift
			;;
		-*) usage ;;
		*)
			[ -z "$pr" ] || usage
			pr=$1
			;;
	esac
	shift
done
[ -n "$pr" ] || usage
case $interval in '' | *[!0-9]*) usage ;; esac
case $timeout in *[!0-9]*) usage ;; esac

verdict_program() {
	cat <<'JQ'
def passing: . == "SUCCESS" or . == "NEUTRAL" or . == "SKIPPED";
.headRefOid as $sha
| ([.statusCheckRollup[]
	| if .__typename == "CheckRun"
		then {key: "\(.workflowName)/\(.name)", name, at: .startedAt,
			done: (.status == "COMPLETED"), passed: (.conclusion | passing)}
		else {key: .context, name: .context, at: .startedAt,
			done: (.state != "PENDING" and .state != "EXPECTED"), passed: (.state | passing)}
		end]
	| group_by(.key) | map(max_by([(.done | not), .at]))) as $runs
| (($required | split("\n") | map(select(. != "")) | unique) - ($runs | map(.name))) as $missing
| ($runs | map(select(.done | not) | .name)) as $running
| ($runs | map(select(.done and (.passed | not)) | .name)) as $failed
| ([.reviews[] | select(.commit.oid == $sha)] | group_by(.author.login)
	| map(max_by(.submittedAt) | "\(.author.login) \(.state)")) as $reviews
| ($runs | length) as $total
| if .state == "MERGED" then ["merged", "merged into \(.baseRefName)"]
	elif .state == "CLOSED" then ["closed", "closed without merging"]
	elif .mergeable == "CONFLICTING" then ["conflicting", "conflicts with \(.baseRefName), and GitHub won't start checks until it merges cleanly"]
	elif $total == 0 then ["pending", "no check runs on the head yet"]
	elif $missing != [] then ["pending", "waiting for \($missing | join(", "))"]
	elif $running != [] then ["pending", "\($running | length) of \($total) running: \($running | join(", "))"
		+ (if $failed == [] then "" else " (failed so far: \($failed | join(", ")))" end)]
	elif $failed != [] then ["failed", "\($failed | length) of \($total) failed: \($failed | join(", "))"]
	else ["green", "\($total) of \($total) passed"]
	end
| "\(.[0])\t\(.[0]) \($sha[0:7]): \(.[1])"
	+ (if $reviews == [] then "" else " | reviews on head: \($reviews | join(", "))" end)
JQ
}

started=$SECONDS
last=
while :; do
	view=$(gh pr view "$pr" --json url,state,mergeable,baseRefName,headRefOid,statusCheckRollup,reviews) || exit 1
	state=$(jq -r .state <<<"$view")
	required=$expect
	if [ "$state" = OPEN ]; then
		url=$(jq -r .url <<<"$view")
		host=${url#https://}
		host=${host%%/*}
		repo=${url#https://"$host"/}
		repo=${repo%/pull/*}
		base=$(jq -r .baseRefName <<<"$view")
		protected=$(gh api --hostname "$host" "repos/$repo/branches/$base" \
			--jq '.protection.required_status_checks | select(.enforcement_level != "off") | .contexts[]') || exit 1
		ruled=$(gh api --hostname "$host" --paginate "repos/$repo/rules/branches/$base" \
			--jq '.[] | select(.type == "required_status_checks") | .parameters.required_status_checks[].context') || exit 1
		required+=$protected$'\n'$ruled
	fi
	status=$(jq -r --arg required "$required" "$(verdict_program)" <<<"$view")
	verdict=${status%%$'\t'*}
	line=${status#*$'\t'}

	if [ "$line" != "$last" ]; then
		echo "$(date +%H:%M:%S) $line"
		last=$line
	fi
	case $verdict in
		green | merged) exit 0 ;;
		failed | conflicting | closed) exit 1 ;;
	esac
	if $once; then
		exit 2
	fi
	if [ -n "$timeout" ] && [ $((SECONDS - started)) -ge "$timeout" ]; then
		echo "watch-ci: still pending after ${timeout}s" >&2
		exit 2
	fi
	sleep "$interval"
done
