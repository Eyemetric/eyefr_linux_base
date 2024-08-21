#!/bin/bash
#NOTE: currently not in use. served as the template on which we build the ansible module in the library dir. 
# Function to log error messages to stderr and exit
log_error() {
    echo "ERROR: $1" >&2
    exit 1
}

# Function to log info messages to stdout
log_info() {
    echo "INFO: $1"
}

add_repos() {
    sudo dnf update -y
    # sudo dnf install -y epel-release
    sudo dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm
    sudo subscription-manager repos --enable codeready-builder-for-rhel-9-$(arch)-rpms
    # Install the NVIDIA drivers
    sudo dnf config-manager --add-repo http://developer.download.nvidia.com/compute/cuda/repos/rhel9/$(uname -i)/cuda-rhel9.repo
}
# Check if script is run with root privileges
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root"
fi

# Check for required argument
if [ "$#" -lt 1 ]; then
    log_error "Usage: $0 <minimum_cuda_version> [update_existing=false]"
fi

MIN_CUDA_VERSION=$1
UPDATE_EXISTING=${2:-false}

# Check for NVIDIA card
if ! lspci | grep -i nvidia > /dev/null; then
    log_error "No NVIDIA card detected"
fi

# Check for existing NVIDIA driver and CUDA version
if command -v nvidia-smi &> /dev/null; then
    CURRENT_CUDA_VERSION=$(nvidia-smi --version | grep -i "CUDA Version" | awk '{print $4}')

    log_info "Current CUDA version: $CURRENT_CUDA_VERSION"

    # Compare versions
    if (( $(echo "$CURRENT_CUDA_VERSION >= $MIN_CUDA_VERSION" | bc -l) )); then
        log_info "Installed CUDA version meets minimum requirements. No action needed."
        log_info "if you want to update to the latest version pass update_existing=true"
        exit 0
    elif [ "$UPDATE_EXISTING" != "true" ]; then
        log_error "Installed CUDA version does not meet minimum requirements. Set update_existing=true to update."
    fi

    # Check if non-DKMS drivers are installed
    if ! rpm -qa | grep -q nvidia-driver-cuda-libs; then
        log_error "Non-DKMS NVIDIA drivers are installed. DKMS drivers are preferred."
    fi
fi


log_info "Adding epel repository..."
dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm

log_info "enabling code ready repository..."
subscription-manager repos --enable codeready-builder-for-rhel-9-$(arch)-rpms

log_info "Adding NVIDIA repository..."
dnf config-manager --add-repo http://developer.download.nvidia.com/compute/cuda/repos/rhel9/$(uname -i)/cuda-rhel9.repo || log_error "Failed to add NVIDIA repository"

# Proceed with installation/update
log_info "Updating system packages..."
dnf update -y || log_error "Failed to update system packages"

log_info "Installing/Updating NVIDIA drivers..."
dnf module install -y nvidia-driver:dkms-latest || log_error "Failed to install/update NVIDIA drivers"

log_info "NVIDIA drivers installation/update completed successfully"
exit 0