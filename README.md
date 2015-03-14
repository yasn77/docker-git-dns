docker-git-dns
==============
    OS Base : Ubuntu 14.04
    Exposed Ports : 53/udp 53/tcp

Environment Variables
---------------------
    SSH_AUTH_SOCK
        Path to SSH Agent socket
    GIT_REPO
        Path to git repository
    CONFIG_PATH
        Relative path to custom named configuration file in the Git repository
        (default : named.local)
    UPDATE_INTERVAL
        Interval to check for Git updates. This can be specified in (h)ours, (m)inutes or seconds (just an integer) (default : 30m)
    REPO_DIR
        Absolute path to where the Git repository is checked out (default: /git_dns)
    LOCAL_NET
        Networks that will be considered 'local'. An ACL entry will be created for this network called mynet (recursion is allowed for 'mynet'). (default: any)

This was orignally inspired by [somejedi/docker-bind9](https://registry.hub.docker.com/u/somejedi/docker-bind9/). Thanks!

Run Bind 9 in docker and manage its configuration using Git and automatically reload when the repository is updated. The instance will come up with a basic Bind server that will read `named.local` from the root of your git repository (you can override the location with `CONFIG_PATH`).

An important note is that the reload will be of the server not of a particular zone. So for large number of zones, this may not be ideal.

The above environment variables can be stored in a json configuration file that can be mounted in the docker instance (`/docker-git-dns.json`). The environment variables will override settings in the configuration file.

### Configuration file example
```json
{
    "SSH_AUTH_SOCK": "/custom/path/to/ssh/socket",
    "GIT_REPO" : "https://<token>:x-oauth-basic@github.com/owner/repo.git",
    "CONFIG_PATH" : "relative/path/in/git/repo/named.conf",
    "UPDATE_INTERVAL" : "1h",
    "REPO_DIR" : "/path/in/container/repo_clone",
    "LOCAL_NET" : "any"
}
```

If you decide to use SSH to clone your repoistory, you will need to mount launch SSH Agent (and your key) on the host and mount `$SSH_AUTH_SOCK` to `/ssh_auth_sock` (`-v $SSH_AUTH_SOCK:/ssh_auth_sock`)

### Examples

Clone from Github using API token and check for updates every 30 seconds:
```bash
docker run -P -e UPDATE_INTERVAL=30 -e GIT_REPO="https://<token>:x-oauth-basic@github.com/owner/repo.git" yasn77/docker-git-dns
```

Clone using SSH and check for updates every hour:
```bash
[ -S $SSH_AUTH_SOCK ] || eval `ssh-agent`
ssh-add /path/to/ssh/key
docker run -P -e UPDATE_INTERVAL=1h -v $SSH_AUTH_SOCK:/ssh_auth_sock -e GIT_REPO="git@github.com:some_user/some_repo.git" yasn77/docker-git-dns
```

Use a JSON configuration file:
```bash
docker run -P -v /path/to/config.json:/docker-git-dns.json yasn77/docker-git-dns
```