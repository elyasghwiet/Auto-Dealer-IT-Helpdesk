#!/usr/bin/env bash
# disk_cleanup.sh - safe disk cleanup for Linux servers (Ubuntu).
# Default is a DRY RUN: it only lists what it would delete. Use --apply to delete.
#
# Usage:  ./disk_cleanup.sh [--apply] [--days N] [--target DIR]... [--log FILE]
#   --apply        really delete (default: dry run)
#   --days N       only files older than N days (default 7)
#   --target DIR   clean this directory (can be repeated); default targets are below
#   --log FILE     write a log (default ./disk_cleanup.log)
#
# Safety rules: never leaves the file system of the target (-xdev), never follows symlinks,
# deletes regular files only, refuses system-critical targets, and logs every action.
set -u

APPLY=0; DAYS=7; LOG="./disk_cleanup.log"; TARGETS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --apply)  APPLY=1 ;;
    --days)   DAYS="${2:-}"; shift ;;
    --target) TARGETS+=("${2:-}"); shift ;;
    --log)    LOG="${2:-}"; shift ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

case "$DAYS" in ''|*[!0-9]*) echo "--days must be a number" >&2; exit 2 ;; esac
if [ ${#TARGETS[@]} -eq 0 ]; then
  TARGETS=("/tmp" "/var/tmp" "/var/log" "/var/cache/apt/archives" "$HOME/.cache/thumbnails")
fi

# Directories that must never be cleaned
is_forbidden() {
  case "$1" in
    /|/bin|/boot|/dev|/etc|/home|/lib*|/opt|/proc|/root|/run|/sbin|/srv|/sys|/usr|/var) return 0 ;;
  esac
  return 1
}

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOG"; }

START=$(date +%s)
MODE="DRY RUN"; [ "$APPLY" -eq 1 ] && MODE="APPLY"
log "=== disk_cleanup start | mode=$MODE | older than ${DAYS} days ==="
used_before=$(df -P / | awk 'NR==2{print $3}')   # 1K blocks
total_files=0; total_kb=0

for dir in "${TARGETS[@]}"; do
  dir="${dir%/}"
  if [ -z "$dir" ] || is_forbidden "$dir"; then log "SKIP  $dir (forbidden or empty target)"; continue; fi
  if [ ! -d "$dir" ]; then log "SKIP  $dir (not a directory)"; continue; fi

  # /var/log: only rotated/compressed logs, never the live ones
  if [ "$dir" = "/var/log" ]; then
    FIND=(find "$dir" -xdev -type f \( -name '*.gz' -o -name '*.[0-9]' -o -name '*.old' \) -mtime +"$DAYS")
  else
    FIND=(find "$dir" -xdev -type f -mtime +"$DAYS")
  fi

  files=0; kb=0
  while IFS= read -r -d '' f; do
    size=$(du -k -- "$f" 2>/dev/null | cut -f1); size=${size:-0}
    files=$((files+1)); kb=$((kb+size))
    if [ "$APPLY" -eq 1 ]; then
      if rm -f -- "$f" 2>/dev/null; then :; else log "WARN  cannot delete $f"; fi
    fi
  done < <("${FIND[@]}" -print0 2>/dev/null)

  log "DIR   $dir -> $files file(s), $((kb/1024)) MB $([ "$APPLY" -eq 1 ] && echo deleted || echo 'would be deleted')"
  total_files=$((total_files+files)); total_kb=$((total_kb+kb))
done

used_after=$(df -P / | awk 'NR==2{print $3}')
END=$(date +%s)
log "SUMMARY files=$total_files size=$((total_kb/1024))MB mode=$MODE disk_used_before=$((used_before/1024))MB disk_used_after=$((used_after/1024))MB"
log "=== finished in $((END-START)) second(s) ==="
exit 0
