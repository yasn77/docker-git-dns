#!/usr/bin/env python

from git import Repo
import os
import time

import pprint

config_file = '/docker-git-dns.json'

def set_config_defaults():
    return {
        'GIT_REPO': None,
        'CONFIG_PATH': None,
        'UPDATE_INTERVAL': '30m',
        'REPO_DIR': '/git_dns'
    }

def get_config():
    config = set_config_defaults()
    try:
        with open(config_file) as d:
            config = config.update(json.load(d))
    except:
        pass

    for k in config.keys():
        if k in os.environ.keys():
            config[k] = os.environ[k]
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
    __log("Cloning repository : {0}".format(config['REPO_DIR']))
    repo = Repo.clone_from(config['GIT_REPO'], config['REPO_DIR'])
    return repo

def has_update(repo):
    pass

def main():
    repo = clone_repo()
    unit = config['UPDATE_INTERVAL'][-1].lower()
    if unit.isalpha():
        interval = config['UPDATE_INTERVAL'][0:-1]
    else:
        interval = config['UPDATE_INTERVAL']
    try:
        sec = to_sec(unit, interval)
    except ValueError:
        __log('ERR: Update interval is set to: {0}'.format(config['UPDATE_INTERVAL']))
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
