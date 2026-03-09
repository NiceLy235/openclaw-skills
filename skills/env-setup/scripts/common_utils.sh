#!/bin/bash
# Common utilities for environment setup

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Progress tracking
TOTAL_STEPS=0
CURRENT_STEP=0

# Initialize progress tracking
init_progress() {
    TOTAL_STEPS=$1
    CURRENT_STEP=0
    echo ""
    echo -e "${BOLD}${CYAN}════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${CYAN}  Installation Progress - Total Steps: $TOTAL_STEPS${NC}"
    echo -e "${BOLD}${CYAN}════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Update progress
update_progress() {
    local step_name=$1
    local status=${2:-"running"}  # running, success, error
    
    ((CURRENT_STEP++))
    local percentage=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    
    # Create progress bar (using ASCII characters for better compatibility)
    local bar_width=40
    local filled=$((percentage * bar_width / 100))
    local empty=$((bar_width - filled))
    local bar=$(printf "%${filled}s" | tr ' ' '=')
    local bar_empty=$(printf "%${empty}s" | tr ' ' '-')
    
    # Status icon (using ASCII-friendly symbols)
    local icon
    case $status in
        running) icon="..." ;;
        success) icon="[OK]" ;;
        error)   icon="[FAIL]" ;;
        *)       icon="•" ;;
    esac
    
    echo ""
    echo -e "${BOLD}Step $CURRENT_STEP/$TOTAL_STEPS${NC}: $step_name"
    echo -e "Progress: [${GREEN}${bar}${NC}${bar_empty}] ${percentage}%"
    echo -e "Status: $icon"
    echo ""
}

# Logging function with enhanced formatting
log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%H:%M:%S')
    
    case $level in
        INFO)
            echo -e "${BLUE}[i]${NC} [${timestamp}] ${message}"
            ;;
        SUCCESS)
            echo -e "${GREEN}[+]${NC} [${timestamp}] ${message}"
            ;;
        WARNING)
            echo -e "${YELLOW}[!]${NC} [${timestamp}] ${message}"
            ;;
        ERROR)
            echo -e "${RED}[x]${NC} [${timestamp}] ${message}"
            ;;
        PROGRESS)
            echo -e "${CYAN}[~]${NC} [${timestamp}] ${message}"
            ;;
        STEP)
            echo -e "${MAGENTA}[>]${NC} [${timestamp}] ${message}"
            ;;
        *)
            echo "[-] [${timestamp}] ${message}"
            ;;
    esac
}

# Initialize log file
init_log() {
    local env_type=$1
    local log_dir="$HOME/.openclaw"
    local log_file="$log_dir/install_${env_type}_$(date '+%Y%m%d_%H%M%S').log"
    
    mkdir -p "$log_dir"
    touch "$log_file"
    
    echo "$log_file"
}

# Execute command with retry
retry_command() {
    local max_attempts=$1
    local delay=$2
    local command="${@:3}"
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log INFO "Attempt $attempt of $max_attempts: $command"
        
        if eval "$command"; then
            return 0
        fi
        
        if [ $attempt -lt $max_attempts ]; then
            log WARNING "Command failed. Retrying in ${delay} seconds..."
            sleep $delay
        fi
        
        ((attempt++))
    done
    
    log ERROR "Command failed after $max_attempts attempts: $command"
    return 1
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if directory exists and is writable
check_directory() {
    local dir=$1
    
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir" 2>/dev/null || {
            log ERROR "Cannot create directory: $dir"
            return 1
        }
    fi
    
    if [ ! -w "$dir" ]; then
        log ERROR "Directory is not writable: $dir"
        return 1
    fi
    
    return 0
}

# Check disk space (minimum 2GB)
check_disk_space() {
    local path=$1
    local min_space_kb=$((2 * 1024 * 1024))  # 2GB in KB
    local available_kb=$(df -k "$path" | awk 'NR==2 {print $4}')
    
    if [ "$available_kb" -lt "$min_space_kb" ]; then
        log ERROR "Insufficient disk space. Required: 2GB, Available: $((available_kb / 1024))MB"
        return 1
    fi
    
    log INFO "Disk space check passed. Available: $((available_kb / 1024))MB"
    return 0
}

# Check network connectivity
check_network() {
    log INFO "Checking network connectivity..."
    
    if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        log SUCCESS "Network connectivity check passed"
        return 0
    else
        log ERROR "Network connectivity check failed"
        return 1
    fi
}

# Detect operating system
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID $VERSION_ID"
    elif [ "$(uname)" = "Darwin" ]; then
        echo "macOS $(sw_vers -productVersion)"
    else
        echo "Unknown"
    fi
}

# Detect architecture
detect_arch() {
    uname -m
}

# Install package using appropriate package manager
install_package() {
    local package=$1
    
    if command_exists apt-get; then
        sudo apt-get update -qq && sudo apt-get install -y "$package"
    elif command_exists yum; then
        sudo yum install -y "$package"
    elif command_exists brew; then
        brew install "$package"
    else
        log ERROR "No supported package manager found"
        return 1
    fi
}

# Generate installation report
generate_report() {
    local env_type=$1
    local install_path=$2
    local version=$3
    local log_file=$4
    
    cat << EOF

${BOLD}${GREEN}==================================================${NC}
${BOLD}${GREEN}  Installation Complete! [OK]${NC}
${BOLD}${GREEN}==================================================${NC}

${BOLD}Installation Report:${NC}
${CYAN}--------------------------------------------------${NC}
  ${BOLD}Environment:${NC}    $env_type
  ${BOLD}Version:${NC}        $version
  ${BOLD}Install Path:${NC}   $install_path
  ${BOLD}Date:${NC}           $(date '+%Y-%m-%d %H:%M:%S')
  ${BOLD}OS:${NC}             $(detect_os)
  ${BOLD}Architecture:${NC}   $(detect_arch)
  ${BOLD}Log File:${NC}       $log_file
${CYAN}--------------------------------------------------${NC}

EOF
}

# Show real-time command output with progress indicator
run_with_progress() {
    local description=$1
    local command=$2
    local show_output=${3:-true}
    
    log PROGRESS "$description ..."
    
    if [ "$show_output" = true ]; then
        # Show command output in real-time
        local temp_log=$(mktemp)
        eval "$command" 2>&1 | tee "$temp_log"
        local exit_code=${PIPESTATUS[0]}
        rm -f "$temp_log"
    else
        # Run silently, show only result
        local temp_log=$(mktemp)
        if eval "$command" > "$temp_log" 2>&1; then
            log SUCCESS "$description - Done"
            rm -f "$temp_log"
            return 0
        else
            log ERROR "$description - Failed"
            echo "Last few lines of output:"
            tail -20 "$temp_log"
            rm -f "$temp_log"
            return 1
        fi
    fi
    
    return $exit_code
}

# Display a spinner for long-running operations
show_spinner() {
    local pid=$1
    local message=$2
    local spin='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0
    
    while kill -0 $pid 2>/dev/null; do
        i=$(( (i+1) % 10 ))
        printf "\r${CYAN}${spin:$i:1}${NC} $message"
        sleep 0.1
    done
    
    printf "\r"
}

# Display installation header
show_header() {
    local env_type=$1
    local version=${2:-"latest"}
    
    clear
    echo ""
    echo -e "${BOLD}${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${CYAN}║                                                        ║${NC}"
    echo -e "${BOLD}${CYAN}║${NC}  ${BOLD}${GREEN}$env_type${NC} Installation                            ${BOLD}${CYAN}║${NC}"
    echo -e "${BOLD}${CYAN}║${NC}  Version: $version                                     ${BOLD}${CYAN}║${NC}"
    echo -e "${BOLD}${CYAN}║${NC}  Started: $(date '+%Y-%m-%d %H:%M:%S')                      ${BOLD}${CYAN}║${NC}"
    echo -e "${BOLD}${CYAN}║                                                        ║${NC}"
    echo -e "${BOLD}${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Display download progress
show_download_progress() {
    local url=$1
    local description=$2
    
    log INFO "Downloading: $description"
    log STEP "URL: $url"
    echo ""
}
