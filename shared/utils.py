import yaml


def read_hosts(is_docker=True):
    with open('hosts.yml', 'r') as f:
        hosts = yaml.safe_load(f)
    if not is_docker:
        # Change to hosts to localhost
        for x, vals in hosts.items():
            if x != 'frontend' and x != 'clients':
                hosts[x]['host'] = 'localhost'
            if x == 'clients':
                for c in vals:
                    c['host'] = 'localhost'

    return hosts
