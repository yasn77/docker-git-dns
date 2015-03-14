#!/usr/bin/env python

from git import Repo, exc
import os
import time
import subprocess

import pprint

config_file = '/docker-git-dns.json'

def set_config_defaults():
    return {
        'GIT_REPO': None,
        'CONFIG_PATH': 'named.local',
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

    config['NAMED_LOCAL'] = '/etc/bind/named.conf.local'
    return config

def __log(msg):
    print('{0} {1}').format(time.strftime("%Y-%m-%dT%H:%M:%S"), msg)

def disable_ssh_host_key_verify():
    ssh_config_path = "/etc/ssh/ssh_config"
    ssh_config = """Host *
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel=QUIET
"""
    with open(ssh_config_path, 'w') as ssh_conf:
        ssh_conf.write(ssh_config)

def to_sec(interval):
    unit = interval[-1].lower()
    if unit.isalpha():
       i  = interval[0:-1]
    else:
        i = interval
    if unit == 's':
        return int(i)
    elif unit == 'm':
        return int(i) * 60
    elif unit == 'h':
        return int(i) * 3600
    else:
        return int(i)

def named_conf_local(content):
    with open(config['NAMED_LOCAL'], 'a') as git_conf:
        git_conf.write(content)

def start_named():
    subprocess.Popen(["/usr/sbin/named", "-c", "/etc/bind/named.conf"])

def named_reload():
    subprocess.Popen(['/usr/sbin/rndc', '-p', '9953', 'reload'])

def named_acl(acl_name, acl_net):
    rule = """
acl "%s" {
    %s;
};
""" % (acl_name, acl_net)
    named_conf_local(rule)

def named_conf():
    os.unlink(config['NAMED_LOCAL'])
    os.chown('/etc/bind/rndc.key', 0, 0)
    git_named = "{0}/{1}".format(config['REPO_DIR'],config['CONFIG_PATH'])
    named_acl('mynet', config['LOCAL_NET'])
    named_conf_local('controls { inet 127.0.0.1 port 9953 allow {localhost;};};\n')
    if os.path.exists(git_named):
        named_conf_local('include "{0}";\n'.format(git_named))
    else:
        __log("ERR: {0} not found, exiting.".format(git_named))
        exit(1)

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
    disable_ssh_host_key_verify()
    repo = clone_repo()
    origin = repo.remotes.origin
    named_conf()
    start_named()
    try:
        sec = to_sec(config['UPDATE_INTERVAL'])
    except ValueError:
        __log('ERR: Update interval is set to: {0}'.format(config['UPDATE_INTERVAL']))
        __log('ERR: Problem trying to convert {0} to seconds...exiting'.format(interval))
        exit(1)
    __log("Going in to run loop")
    while True:
        if has_update(repo):
           __log('Pulling git repo from origin and reloading bind')
           origin.pull()
           named_reload()
        __log("Sleeping for {0} sec".format(sec))
        time.sleep(sec)

if __name__ == '__main__':
    config = get_config()
    main()
