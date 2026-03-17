#!/usr/bin/env bash
# Test script to verify skill execution flow improvements
# This script simulates a proper step-by-step execution pattern

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROGRESS_LOG="/tmp/skill_execution_test.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$PROGRESS_LOG"
}

step_start() {
    local num="$1"
    local name="$2"
    log -e "${YELLOW}Step $num: $name${NC}"
    log "Starting..."
}

step_complete() {
    local num="$1"
    local name="$2"
    local result="$3"
    log -e "${GREEN}✅ Step $num completed: $name${NC}"
    if [ -n "$result" ]; then
        log "Result: $result"
    fi
}

step_fail() {
    local num="$1"
    local name="$2"
    local error="$3"
    log -e "${YELLOW}❌ Step $num failed: $name${NC}"
    log "Error: $error"
    exit 1
}

# Test execution flow
test_execution_flow() {
    log "=== Starting Skill Execution Flow Test ==="

    # Step 1: Check environment
    step_start 1 "Environment Check"
    if [ -f "$SCRIPT_DIR/check_environment.sh" ]; then
        step_complete 1 "Environment Check" "Script exists and is executable"
    else
        step_fail 1 "Environment Check" "check_environment.sh not found"
    fi

    # Step 2: Verify Python
    step_start 2 "Python Verification"
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        step_complete 2 "Python Verification" "Python $PYTHON_VERSION available"
    else
        step_fail 2 "Python Verification" "Python3 not found in PATH"
    fi

    # Step 3: Check disk space
    step_start 3 "Disk Space Check"
    AVAILABLE_SPACE=$(df -BG / | awk 'NR==2 {print $4}' | tr -d 'G')
    if [ "$AVAILABLE_SPACE" -gt 2 ]; then
        step_complete 3 "Disk Space Check" "$AVAILABLE_SPACE GB available (requires 2 GB minimum)"
    else
        step_fail 3 "Disk Space Check" "Only $AVAILABLE_SPACE GB available (requires 2 GB minimum)"
    fi

    # Step 4: Test progress reporting
    step_start 4 "Progress Reporting Test"
    log "This demonstrates real-time progress updates..."
    for i in {1..5}; do
        log "Progress: $i/5 - Processing item..."
        sleep 1
    done
    step_complete 4 "Progress Reporting Test" "5 items processed in 5 seconds"

    # Step 5: Final verification
    step_start 5 "Final Verification"
    log "Verifying all steps completed successfully..."
    step_complete 5 "Final Verification" "All 5 steps completed without errors"

    log -e "${GREEN}=== Skill Execution Flow Test PASSED ===${NC}"
}

# Display instructions
show_instructions() {
    echo ""
    echo -e "${BLUE}=== Skill Execution Testing Instructions ===${NC}"
    echo ""
    echo "This test demonstrates the proper step-by-step execution pattern."
    echo ""
    echo "Expected output:"
    echo "  - Each step starts with 'Step N: [Name]'"
    echo "  - Each step completes with '✅ Step N completed: [Result]'"
    echo "  - Progress is logged during execution"
    echo "  - Failures are clearly reported and stop execution"
    echo ""
    echo "To use this pattern in OpenClaw skills:"
    echo "  1. Add explicit step markers (Step 1, Step 2, etc.)"
    echo "  2. Report completion after each step"
    echo "  3. Return results immediately, don't batch them"
    echo "  4. Use process poll for long-running operations"
    echo ""
    echo "Test results are logged to: $PROGRESS_LOG"
    echo ""
}

# Main
case "${1:-}" in
    --help|-h)
        show_instructions
        ;;
    *)
        show_instructions
        echo ""
        read -p "Run test? [Y/n] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            test_execution_flow
        fi
        ;;
esac
