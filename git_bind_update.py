#!/usr/bin/env python

from git import Repo, exc
import os
import time

import pprint

config_file = '/docker-git-dns.json'

def set_config_defaults():
    return {
        'GIT_REPO': None,
        'CONFIG_PATH': None,
        'UPDATE_INTERVAL': '30m',
        'REPO_DIR': '/git_dns',
        'LOCAL_NET': 'any',
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
    if config.has_key('LOCAL_NET'):
        config['LOCAL_NET'] = config['LOCAL_NET'].replace(',', ';')
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

def named_acl(acl_name, acl_net):
    rule = """
acl "%s" {
    %s;
}
""" % (acl_name, acl_net)
    with open('/etc/bind/acl.conf', 'w+') as acl:
        acl.write(rule)

def named_conf():
    named_acl('localnets', config['LOCAL_NET'])

def clone_repo():
    __log("Cloning repository : {0}".format(config['REPO_DIR']))
    failed = False
    if os.path.exists(config['REPO_DIR']):
        try:
            repo = Repo(config['REPO_DIR'])
            if not repo.remotes.origin.url == config['GIT_REPO']:
                __log("ERR: {0} exists but origin is not {1}, not sure what to do so exiting..".format(config['REPO_DIR'], config['GIT_REPO']))
                failed = True
        except exc.InvalidGitRepositoryError:
            __log("ERR: {0} exists but isn't a git repo, not sure what to do so exiting..".format(config['REPO_DIR']))
            failed = True
    else:
        repo = Repo.clone_from(config['GIT_REPO'], config['REPO_DIR'])
    return repo if failed == False else exit(1)

def has_update(repo):
    __log('Fetching refs from origin')
    # GitPython may raise an exception after doing a fetch, workaround is to
    # try again. Found the fix here --> https://github.com/saltstack/salt/commit/6ef26b188013dd0f249cdf8432222224d4375156
    try:
        repo.remotes.origin.fetch()
    except AssertionError:
        repo.remotes.origin.fetch()
    if repo.rev_parse('master') == repo.rev_parse('origin/master'):
        __log('Local master == Remote master')
        return False
    else:
        __log('Local master != Remote master')
        return True
    fi

def main():
    repo = clone_repo()
    origin = repo.remotes.origin
    named_conf()
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
           __log('Pulling git repo from origin')
           origin.pull()
        __log("Sleeping for {0} sec".format(sec))
        time.sleep(sec)

if __name__ == '__main__':
    config = get_config()
    main()
