#!/usr/bin/python

DOCUMENTATION = r'''
---
module: nvidia_driver_install_dkms
short_description: Manage NVIDIA drivers on RHEL systems and Ubuntu
description:
    - This module manages NVIDIA drivers on Ubuntu (20.04+) and RHEL (9+) systems.
    - It checks for the presence of an NVIDIA GPU and compares CUDA versions before installation.
    - It can install, update, or remove NVIDIA drivers based on the specified state.
options:
    min_cuda_version:
        description:
            - The minimum required CUDA version.
        required: true
        type: str
    ansible_distribution:
        description:
            - We need to know if we're on RedHat or Ubuntu. You can pass {{ ansible_distribution }}
        required: true
        type: str
    state:
        description:
            - Desired state of the NVIDIA drivers.
            - 'present': Install drivers if not present or if they don't meet the minimum CUDA version.
            - 'latest': Always update to the latest version.
            - 'absent': Remove NVIDIA drivers.
        required: true
        type: str
        choices: [ 'present', 'latest', 'absent' ]
'''

EXAMPLES = r'''
- name: Install NVIDIA drivers
  nvidia_driver_install_dkms:
    min_cuda_version: "11.0"
    ansible_distribution: {{ ansible_distribution }}
    state: present

- name: Update NVIDIA drivers to latest version
  nvidia_driver_install_dkms:
    min_cuda_version: "11.0"
    ansible_distribution: {{ ansible_distribution }}
    state: latest

- name: Remove NVIDIA drivers
  nvidia_driver_install_dkms:
    ansible_distribution: {{ ansible_distribution }}
    state: absent
'''

from ansible.module_utils.basic import AnsibleModule
import subprocess
import re
import os

def run_command(module, command, check_mode=False):
    if check_mode:
        return (0, f"Would run command: {command}", "")
    rc, out, err = module.run_command(command, check_rc=False)
    if rc != 0:
        module.fail_json(msg=f"Command failed: {command}", stdout=out, stderr=err)
    return rc, out.strip(), err.strip()

def check_nvidia_gpu(module):
    lspci_path = module.get_bin_path('lspci', required=True)
    grep_path = module.get_bin_path('grep', required=True)
    
    cmd = f"{lspci_path} | {grep_path} -i nvidia"
    rc, out, err = module.run_command(cmd, use_unsafe_shell=True)
    
    return rc == 0 and bool(out)

def get_cuda_version(module):
    nvidia_smi_path = module.get_bin_path('nvidia-smi', required=False)
    
    if not nvidia_smi_path:
        return None  # nvidia-smi is not available   
    rc, out, err = module.run_command([nvidia_smi_path, '--version'])
    
    if rc != 0:
        module.fail_json(msg=f"nvidia-smi command failed: {err}")
    
    cuda_version_match = re.search(r"CUDA Version\s+:\s+(\d+\.\d+)", out)
    if cuda_version_match:
        return cuda_version_match.group(1)
    else:
        module.fail_json(msg=f"Unable to determine CUDA version from nvidia-smi output: {out}")

def compare_versions(current_version, min_version):
    current_parts = [int(part) for part in current_version.split('.')]
    min_parts = [int(part) for part in min_version.split('.')]
    return current_parts >= min_parts

def get_driver_version(module):
    rc, out, err = module.run_command(["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"])
    if rc == 0:
        return out.strip()
    else:
        return "Unknown"

def install_nvidia_drivers(module, os_type):
    min_cuda_version = module.params['min_cuda_version']
    state = module.params['state']
    check_mode = module.check_mode
    
    current_cuda_version = get_cuda_version(module) if not check_mode else None
    if current_cuda_version:
        if compare_versions(current_cuda_version, min_cuda_version) and state != 'latest':
            return {'changed': False, 'msg': f"Current CUDA version {current_cuda_version} meets minimum requirements. No action taken."}
    
    if check_mode:
        return {'changed': True, 'msg': f"Would install/update NVIDIA drivers for {os_type}"}
    
    if os_type == 'Ubuntu':
        rc, out, err = module.run_command(["ubuntu-drivers", "install"])
    elif os_type == 'RedHat':
        rc, out, err = module.run_command(["dnf", "config-manager", "--add-repo", "https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/cuda-rhel9.repo"])
        if rc != 0:
            module.fail_json(msg=f"Failed to add NVIDIA repository: {err}")
        
        rc, out, err = module.run_command(["dnf", "module", "install", "-y", "nvidia-driver:latest-dkms"])
    else:
        module.fail_json(msg=f"Unsupported OS type: {os_type}")
    
    if rc != 0:
        module.fail_json(msg=f"Failed to install NVIDIA drivers: {err}")
    
    installed_cuda_version = get_cuda_version(module)
    if installed_cuda_version == None:
        installed_cuda_version = "Unknown"

    driver_version = get_driver_version(module)
    
    result = {
        'changed': True,
        'msg': "NVIDIA drivers installed/updated successfully, reboot highly recommended to complete setup",
        'cuda_version': installed_cuda_version,
        'driver_version': driver_version,
        'reboot_required': True
    }
    
    return result

def remove_nvidia_drivers(module, os_type):
    check_mode = module.check_mode
    
    if check_mode:
        return {'changed': True, 'msg': f"Would remove NVIDIA drivers for {os_type}"}

    if get_cuda_version(module) == None:
        return {'changed': False, 'msg': f"Nvidia drivers not currently installed. nothing to remove!"}

    if os_type == 'RedHat':
        commands = [
            ["dnf", "module", "remove", "-y", "nvidia-driver" ],
            ["dnf", "module", "reset", "-y", "nvidia-driver"],
            ["dnf", "clean", "all"]
        ]
    elif os_type == 'Ubuntu':
        commands = [
            ["apt", "purge", "-y", "*nvidia*"],
            ["apt", "autoremove", "-y"],
            ["apt", "clean"]
        ]
    else:
        module.fail_json(msg=f"Unsupported OS type: {os_type}")
    
    for cmd in commands:
        rc, out, err = module.run_command(cmd)
        if rc != 0:
            module.fail_json(msg=f"Failed to remove NVIDIA drivers: {err}")
    
    result = {
        'changed': True,
        'msg': "NVIDIA drivers removed successfully, reboot recommended",
        'reboot_required': True
    }
    
    return result

def get_os_type(module):
    distribution = module.params.get('ansible_distribution')

    if not distribution:
        module.fail_json(msg="Unable to determine distribution. Ensure fact gathering is enabled.")

    if distribution == 'Ubuntu':
        return 'Ubuntu'
    elif distribution in ['RedHat', 'CentOS', 'Rocky', 'AlmaLinux']:  # RHEL and its derivatives
        return 'RedHat'
    else:
        module.fail_json(msg=f"Unsupported OS: {distribution}")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            min_cuda_version=dict(type='str', required=False),
            ansible_distribution=dict(type='str', required=True),
            state=dict(type='str', required=True, choices=['present', 'latest', 'absent'])
        ),
        supports_check_mode=True
    )

    state = module.params['state']
    os_type = get_os_type(module)

    if state != 'absent' and not module.params['min_cuda_version']:
        module.fail_json(msg="min_cuda_version is required when state is 'present' or 'latest'")

    if state != 'absent' and not check_nvidia_gpu(module):
        module.fail_json(msg="No NVIDIA GPU detected")

    try:
        if state in ['present', 'latest']:
            result = install_nvidia_drivers(module, os_type)
        elif state == 'absent':
            result = remove_nvidia_drivers(module, os_type)
        else:
            module.fail_json(msg=f"Invalid state: {state}")
        
        module.exit_json(**result)
    except Exception as e:
        module.fail_json(msg=f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()