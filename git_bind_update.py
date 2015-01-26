#!/usr/bin/env python

from git import Repo
import os
import time

import pprint

config_file = '/docker-git-dns.json'
env_vars_map = {
                'GIT_REPO': 'repo',
                'UPDATE_INTERVAL': 'update',
                'CONFIG_PATH': 'config_path'
               }
repo_dir = '/git_dns'

def get_config():
    config = {}
    try:
        with open(config_file) as d:
            config = json.load(d)
    except:
        pass

    for k,v in env_vars_map.iteritems():
        if k in os.environ.keys():
            config[v] = os.environ[k]
    # Set some defaults
    config['config_path'] = config['config_path'] if not config.has_key('config_path') else None
    config['update'] = config['update'] if not config.has_key('update') else '30m'
    return config

def __log(msg):
    print('{0} {1}').format(time.strftime("%Y-%m-%dT%H:%M:%S"), msg)

def to_sec(u, v):
    if u == 's':
        return int(v)
    elif u == 'm':
        return int(v) * 60
    elif u == 'h':
        return int(v) * 3600
    else:
        return int(v)

def clone_repo():
    repo = Repo.clone_from(config['repo'], repo_dir)
    return repo

def main():
    repo = clone_repo

if __name__ == '__main__':
    config = get_config()
    main()
