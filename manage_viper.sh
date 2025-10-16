#!/bin/bash
# ============================================================
# manage_viper.sh — Unified control panel for ExtremeViper bots
# Usage:
#   ./manage_viper.sh start live
#   ./manage_viper.sh stop dryrun
#   ./manage_viper.sh restart live
#   ./manage_viper.sh status
# ============================================================

SERVICE_LIVE="extremeviper-live.service"
SERVICE_DRYRUN="extremeviper-dryrun.service"

function banner() {
  echo "=============================================="
  echo " 🚀 ExtremeViper Bot Manager"
  echo "=============================================="
}

function usage() {
  echo "Usage:"
  echo "  $0 start [live|dryrun]"
  echo "  $0 stop [live|dryrun]"
  echo "  $0 restart [live|dryrun]"
  echo "  $0 status"
  echo "----------------------------------------------"
  exit 1
}

function manage_service() {
  local action=$1
  local mode=$2

  if [[ "$mode" == "live" ]]; then
    service=$SERVICE_LIVE
  elif [[ "$mode" == "dryrun" ]]; then
    service=$SERVICE_DRYRUN
  else
    echo "❌ Invalid mode: choose 'live' or 'dryrun'."
    usage
  fi

  sudo systemctl $action $service
  echo "✅ $mode service $action complete."
}

banner

case "$1" in
  start)
    manage_service start "$2"
    ;;
  stop)
    manage_service stop "$2"
    ;;
  restart)
    manage_service restart "$2"
    ;;
  status)
    echo "📊 LIVE Service:"
    sudo systemctl status $SERVICE_LIVE --no-pager
    echo
    echo "📊 DRYRUN Service:"
    sudo systemctl status $SERVICE_DRYRUN --no-pager
    ;;
  *)
    usage
    ;;
esac
