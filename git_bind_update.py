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
    if not config.has_key('config_path'):
        config['config_path'] = None
    if not config.has_key('update'):
        config['update'] = '30m'
    config['repo_dir'] = repo_dir
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
    __log("Cloning repository : {0}".format(config['repo_dir']))
    repo = Repo.clone_from(config['repo'], config['repo_dir'])
    return repo

def has_update(repo):
    pass

def main():
    repo = clone_repo()
    unit = config['update'][-1].lower()
    if unit.isalpha():
        interval = config['update'][0:-1]
    else:
        interval = config['update']
    try:
        sec = to_sec(unit, interval)
    except ValueError:
        __log('ERR: Update interval is set to: {0}'.format(config['update']))
        __log('ERR: Problem trying to convert {0} to seconds...exiting'.format(interval))
        exit(1)
    __log("Going in to run loop")
    while True:
        if has_update(repo):
            pass
    __log("Sleeping for {0} sec".format(sec))
    time.sleep(sec)

if __name__ == '__main__':
    config = get_config()
    main()
