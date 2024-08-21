# eyemetric.nvidia

Installs, updates or uninstalls DKMS based drivers on RHEL and precompiled
drivers on Ubuntu.

This role just runs a custom module that handles the nvidia installation. check
out library/nvidia_driver_install_dkms

## Requirements

## Role Variables

### Defaults

```yaml
nvidia_driver_state: present 
min_cuda_version: "12.0"
```

## Dependencies

A list of other roles hosted on Galaxy should go here, plus any details in
regards to parameters that may need to be set for other roles, or variables that
are used from other roles.

## Example Playbook

Including an example of how to use your role (for instance, with variables
passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

## License

BSD

## Author Information

Ryan Martin
