#!/usr/bin/env sh
set -eu

# Single entrypoint for the Tracks Conductor Protocol scripts.
#
# Usage:
#   scripts/tcd.sh init
#   scripts/tcd.sh intake "Title"
#   scripts/tcd.sh promote-intake path/to/TD-....md
#   scripts/tcd.sh archive-promoted [path/to/TD-....md]
#   scripts/tcd.sh task "Title"
#   scripts/tcd.sh track "Title"
#   scripts/tcd.sh future "Topic"
#   scripts/tcd.sh promote-task-to-track path/to/SNN-T-....md <track-slug> [phase]
#   scripts/tcd.sh promote-future-to-adr path/to/FUT-XXX-....md
#   scripts/tcd.sh set-task-status <task-id> <status>
#   scripts/tcd.sh index
#   scripts/tcd.sh validate

cmd="${1:-}"
shift || true

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

case "$cmd" in
  init) exec "$script_dir/tcd_init.sh" "$@" ;;
  intake) exec "$script_dir/tcd_new_intake.sh" "$@" ;;
  promote-intake) exec "$script_dir/tcd_promote_intake.sh" "$@" ;;
  archive-promoted) exec "$script_dir/tcd_archive_promoted.sh" "$@" ;;
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
  archive-promoted [path/to/TD-....md]
  task "Title"
  track "Title"
  future "Topic"
  promote-task-to-track path/to/SNN-T-....md <track-slug> [phase]
  promote-future-to-adr path/to/FUT-XXX-....md
  set-task-status <task-id> <status>
  index
  validate

Env overrides:
  TCD_PROJECT_DIR, TCD_TODO_DIR, TCD_TASKS_DIR, TCD_TRACKS_DIR, TCD_FUTURES_DIR
  TCD_WORK_INDEX, TCD_TRACKS_REGISTRY, TCD_ARCHIVE_TODO_DIR, TCD_ORDER_FILE
  TCD_CONTEXT_DIR (init), TCD_OWNER (intake), TCD_SEQ/TCD_TRACK/TCD_INTAKE (task,
  promote-intake), TCD_TRACK_SLUG (track), TCD_FUT_ID/TCD_FUT_STATUS (future),
  TCD_NEW_ADR (promote-future-to-adr)
EOF
    ;;
  *)
    echo "unknown command: $cmd" >&2
    echo "run: $0 --help" >&2
    exit 2
    ;;
esac
