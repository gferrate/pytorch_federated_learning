import yaml


def read_hosts():
    with open('hosts.yml', 'r') as f:
        return yaml.safe_load(f)
