# wrt_backup

A simple python script to manage your openwrt devices.

## Quickstart

Create a `wrt-backup.yml` config file with your inventory, like:

```
inventory:

  router1:
    host: 192.168.10.1

    board_target: ath79/generic
    board_device: ath79-generic-tplink_archer-c7-v2
    openwrt_version: 22.03.5

    backup_all: True
    backup_state: True

  router2:
    host: 192.168.10.2

    board_target: ipq40xx/generic
    board_device: ipq40xx-generic-linksys_mr8300
    openwrt_version: 22.03.0

```

Then run `wrt-backup hosts` to validate your inventory. Other commands are described in `--help` menu:

```
$ wrt-backup --help
Usage: wrt-backup [OPTIONS] COMMAND [ARGS]...

  wrt-backup, a tool to manage OpenWrt devices

Options:
  -v, --verbose                   Increase verbosity  [default: 0; 0<=x<=2]
  -c, --config TEXT               Path of myapp.yml configuration file or
                                  directory.  [env var: MYAPP_PROJECT_DIR]
  -V, --version                   Show version
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  backup       Backup router config
  fw_download  Download firmware
  fw_show      Show firmware info
  help         Show this help message
  hosts        Show host inventory
  show         Show uci export
```


