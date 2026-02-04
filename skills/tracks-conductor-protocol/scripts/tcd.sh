#!/usr/bin/env sh
set -eu

# Single entrypoint for the Tracks Conductor Protocol scripts.
#
# Usage:
#   ./tracks-conductor-protocol/scripts/tcd.sh init
#   ./tracks-conductor-protocol/scripts/tcd.sh intake "Title"
#   ./tracks-conductor-protocol/scripts/tcd.sh promote-intake path/to/TD-....md
#   ./tracks-conductor-protocol/scripts/tcd.sh task "Title"
#   ./tracks-conductor-protocol/scripts/tcd.sh track "Title"
#   ./tracks-conductor-protocol/scripts/tcd.sh future "Topic"
#   ./tracks-conductor-protocol/scripts/tcd.sh promote-task-to-track path/to/S##-T-....md <track-slug> [phase]
#   ./tracks-conductor-protocol/scripts/tcd.sh promote-future-to-adr path/to/FUT-XXX-....md
#   ./tracks-conductor-protocol/scripts/tcd.sh set-task-status <task-id> <status>
#   ./tracks-conductor-protocol/scripts/tcd.sh index
#   ./tracks-conductor-protocol/scripts/tcd.sh validate

cmd="${1:-}"
shift || true

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

case "$cmd" in
  init) exec "$script_dir/tcd_init.sh" "$@" ;;
  intake) exec "$script_dir/tcd_new_intake.sh" "$@" ;;
  promote-intake) exec "$script_dir/tcd_promote_intake.sh" "$@" ;;
  task) exec "$script_dir/tcd_new_task.sh" "$@" ;;
  track) exec "$script_dir/tcd_new_track.sh" "$@" ;;
  future) exec "$script_dir/tcd_new_future.sh" "$@" ;;
  promote-task-to-track) exec "$script_dir/tcd_promote_task_to_track.sh" "$@" ;;
  promote-future-to-adr) exec "$script_dir/tcd_promote_future_to_adr.sh" "$@" ;;
  set-task-status) exec "$script_dir/tcd_set_task_status.sh" "$@" ;;
  index) exec "$script_dir/tcd_update_index.sh" "$@" ;;
  validate) exec "$script_dir/tcd_validate_repo.sh" "$@" ;;
  ""|-h|--help|help)
    cat <<'EOF'
Tracks Conductor Protocol (tcd.sh)

Commands:
  init
  intake "Title"
  promote-intake path/to/TD-....md
  task "Title"
  track "Title"
  future "Topic"
  promote-task-to-track path/to/S##-T-....md <track-slug> [phase]
  promote-future-to-adr path/to/FUT-XXX-....md
  set-task-status <task-id> <status>
  index
  validate

Env overrides:
  TCD_PROJECT_DIR, TCD_TODO_DIR, TCD_TASKS_DIR, TCD_TRACKS_DIR, TCD_FUTURES_DIR
  TCD_WORK_INDEX, TCD_TRACKS_REGISTRY
EOF
    ;;
  *)
    echo "unknown command: $cmd" >&2
    echo "run: $0 --help" >&2
    exit 2
    ;;
esac
