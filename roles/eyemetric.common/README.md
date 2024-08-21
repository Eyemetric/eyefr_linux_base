# eyemetric.common

This role will bring a server to baseline by

0. register the rhel subcription (if necessary)
1. adding package repositories
2. making the necessary system updates
3. adding the default eyemetric user account
4. adding an ssh public key to the eyemetric user accout

RHEL 9+ and Ubuntu 22+ are supported. Baseline is considered the minimum set of
updates

## Requirements

## Role Variables

A description of the settable variables for this role should go here, including
any variables that are in defaults/main.yml, vars/main.yml, and any variables
that can/should be set via parameters to the role. Any variables that are read
from other roles and/or the global scope (ie. hostvars, group vars, etc.) should
be mentioned here as well.

## Dependencies

A list of other roles hosted on Galaxy should go here, plus any details in
regards to parameters that may need to be set for other roles, or variables that
are used from other roles.

## Example Playbook

Including an example of how to use your role (for instance, with variables
passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: common.rolename, x: 42 }

## License

BSD

## Author Information

Ryan Martin
