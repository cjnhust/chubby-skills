#!/bin/zsh

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: resolve-user-shell-command.sh <command> [command...]" >&2
  exit 64
fi

typeset -a candidates
candidates=("$@")

function lookup_current() {
  local cmd="$1"
  command -v "$cmd" 2>/dev/null || true
}

function lookup_in_zsh() {
  local mode="$1"
  local cmd="$2"

  case "$mode" in
    login_noninteractive)
      zsh -lc "command -v $cmd 2>/dev/null || true"
      ;;
    login_interactive)
      zsh -lic "command -v $cmd 2>/dev/null || true"
      ;;
    *)
      echo "Unsupported mode: $mode" >&2
      return 64
      ;;
  esac
}

typeset -A found
typeset -a modes
modes=(current login_noninteractive login_interactive)

recommended_mode=""
recommended_command=""
recommended_path=""

for mode in "${modes[@]}"; do
  for cmd in "${candidates[@]}"; do
    local_path=""
    if [[ "$mode" == "current" ]]; then
      local_path="$(lookup_current "$cmd")"
    else
      local_path="$(lookup_in_zsh "$mode" "$cmd")"
    fi
    found["${mode}_${cmd}"]="$local_path"
    echo "${mode}_${cmd}=${local_path}"
    if [[ -n "$local_path" && -z "$recommended_command" ]]; then
      recommended_mode="$mode"
      recommended_command="$cmd"
      recommended_path="$local_path"
    fi
  done
done

if [[ -n "$recommended_command" ]]; then
  echo "status=ok"
  echo "recommended_mode=${recommended_mode}"
  echo "recommended_command=${recommended_command}"
  echo "recommended_path=${recommended_path}"
  if [[ -z "${found[current_${recommended_command}]-}" && "$recommended_mode" != "current" ]]; then
    echo "current_shell_missing_but_user_shell_has_command=true"
  else
    echo "current_shell_missing_but_user_shell_has_command=false"
  fi
else
  echo "status=missing"
  echo "recommended_mode="
  echo "recommended_command="
  echo "recommended_path="
  echo "current_shell_missing_but_user_shell_has_command=false"
fi
