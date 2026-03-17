#!/usr/bin/env bash
# Enhanced script runner with real-time progress reporting for OpenClaw
# Usage: run_with_progress.sh <command> <description> <log_file>

set -e

COMMAND="$1"
DESCRIPTION="$2"
LOG_FILE="$3"
PROGRESS_FILE="${LOG_FILE}.progress"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Initialize progress tracking
init_progress() {
    cat > "$PROGRESS_FILE" << EOF
{"status": "starting", "description": "$DESCRIPTION", "start_time": "$(date -Iseconds)"}
EOF
    echo -e "${GREEN}[PROGRESS]${NC} Starting: $DESCRIPTION"
}

# Update progress
update_progress() {
    local status="$1"
    local message="$2"
    cat > "$PROGRESS_FILE" << EOF
{"status": "$status", "description": "$DESCRIPTION", "message": "$message", "timestamp": "$(date -Iseconds)"}
EOF
    echo -e "${GREEN}[PROGRESS]${NC} $message"
}

# Complete progress
complete_progress() {
    cat > "$PROGRESS_FILE" << EOF
{"status": "completed", "description": "$DESCRIPTION", "end_time": "$(date -Iseconds)"}
EOF
    echo -e "${GREEN}[COMPLETED]${NC} $DESCRIPTION"
}

# Fail progress
fail_progress() {
    local error="$1"
    cat > "$PROGRESS_FILE" << EOF
{"status": "failed", "description": "$DESCRIPTION", "error": "$error", "timestamp": "$(date -Iseconds)"}
EOF
    echo -e "${RED}[FAILED]${NC} $DESCRIPTION: $error"
}

# Execute command with monitoring
execute_with_monitoring() {
    local cmd="$1"
    local log_file="$2"

    echo -e "${YELLOW}[EXECUTING]${NC} $cmd"

    # Execute command and capture exit code
    eval "$cmd" > "$log_file" 2>&1
    local exit_code=$?

    # Check result
    if [ $exit_code -eq 0 ]; then
        complete_progress
        return 0
    else
        fail_progress "Command failed with exit code $exit_code. Check $log_file for details."
        tail -20 "$log_file"
        return $exit_code
    fi
}

# Main execution
main() {
    if [ -z "$COMMAND" ] || [ -z "$DESCRIPTION" ]; then
        echo "Usage: $0 <command> <description> [log_file]"
        exit 1
    fi

    if [ -z "$LOG_FILE" ]; then
        LOG_FILE="/tmp/$(echo $DESCRIPTION | tr ' ' '_')_$(date +%Y%m%d_%H%M%S).log"
    fi

    init_progress
    execute_with_monitoring "$COMMAND" "$LOG_FILE"
}

# Run main
main "$@"
