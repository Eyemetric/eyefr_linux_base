# eyemetric.container_engine

Install podman and docker side by side on RedHat and installs just docker on
Ubuntu. If an Nvidia gpu is detected then nvidia-container-toolkit is installed
and the container engines are configured for gpu access.

Requirements ------------jj

Any pre-requisites that may not be covered by Ansible itself or the role should
be mentioned here. For instance, if the role uses the EC2 module, it may be a
good idea to mention in this section that the boto package is required.

## Role Variables

### install, update or remove container engines.

container_management_state: present

### paths for gpu access related configurations. You probable won't ever need to change these.

cdi_spec_path: "/etc/cdi/nvidia.yaml" containers_conf_path:
"/etc/containers/containers.conf" nvidia_container_runtime_path:
"/etc/nvidia-container-runtime/config.toml" cdi_spec_dirs: ["/etc/cdi"]

docker_on_rhel: true # option to install docker alongside podman on rhel
machines. docker_daemon_json_path: "/etc/docker/daemon.json"

## Dependencies

geelingguy.docker

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
