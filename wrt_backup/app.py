import os
import json
import sh
import re
import logging
from ruamel import yaml

from pprint import pprint

from xdg import BaseDirectory

from wrt_backup.hosts import Host
from wrt_backup.common import list_parent_dirs, find_file_up
import wrt_backup.errors as error


logger = logging.getLogger(__name__)

class MyApp:
    "This is MyApp Class"

    version = "0.1.0"
    name = "My Super App"

    app_name = 'wrt-backup'
    config_name = 'wrt-backup.yml'

    def __init__(self, path=None):

        # Load configuration
        self.find_cfg(path)
        self.read_cfg()
        self.build_host_cfg()

    def read_cfg(self):
        "Read yaml configuration file"

        cfg_file = self.config_file

        with open(cfg_file, encoding="utf-8") as _file:
            payload = "".join(_file.readlines())

        self.cfg_data = yaml.safe_load(payload)

    def find_cfg(self, path):
        "Search for project config file"

        config_file = None

        # Search in upper dir if not explicit path
        if not path or path == "AUTO":
            cfg = find_file_up([self.config_name], list_parent_dirs(os.getcwd()))

            if len(cfg) > 0:
                config_file = cfg[0]

        # Search for regular positions
        if not config_file:
            if not path:
                path = os.path.join(BaseDirectory.xdg_config_home, self.app_name)
            config_file = os.path.join(path, self.config_name)

        # Safety check
        if not os.path.isfile(config_file):
            msg = f"Could not find configuration file: {config_file}"
            raise error.MissingConfig(msg)

        # Save config
        self.config_dir = os.path.dirname(config_file)
        self.config_file = config_file
        self.fw_path = os.path.join(self.config_dir, "firmwares")

    def build_host_cfg(self):
        "Build host configuration"

        self._hosts = []
        self._inventory = self.cfg_data.get('inventory', {})
        for name, conf in self._inventory.items():
            self._hosts.append(Host(self, name, path=self.config_dir, **conf))


    # Cli commands
    # =================

    def _loop_hosts(self, limit=None, log_msg=None):
        "Loop over hosts on limit"

        for host in self._hosts:
            if limit and host._name not in limit:
                continue
            if log_msg:
                logger.info(log_msg.format(hostname = host._name, host = host))
            yield host

    def cmd_backup(self, list_files=False, limit=None):
        "Run backup on hosts"

        #for host in self._hosts:
        #    if limit and host._name not in limit:
        #        continue

        log_msg='Backuping device: {hostname}'
        for host in self._loop_hosts(limit=limit, log_msg=log_msg):
            host.cmd_backup(list_files=list_files)

    def cmd_uci_show(self, structured=True, native_type=False, limit=None):
        "Show uci config on each hosts"

        ret = {}
        log_msg='Get uci config for device: {hostname}'
        for host in self._loop_hosts(limit=limit, log_msg=log_msg):
        #for host in self._hosts:
        #    if limit and host._name not in limit:
        #        continue
            ret[host._name] = host.uci_show(native_type=native_type, structured=structured)

        return ret

    def cmd_fw_download(self, limit=None, upgrade=True, version=None):
        "Download firmware configuration"

        ret = {}
        log_msg='Download firmware for device: {hostname}'
        for host in self._loop_hosts(limit=limit, log_msg=log_msg):
            ret[host._name] = host.fw_download(upgrade=upgrade, version=version)
        return ret


    def cmd_facts(self, limit=None):
        "Show device facts"

        ret = {}
        log_msg='Get facts for device: {hostname}'
        for host in self._loop_hosts(limit=limit, log_msg=log_msg):
            ret[host._name] = host.cmd_show_facts()

        return ret


    def cmd_fw_show(self, limit=None):
        "Show firmware configuration"

        ret = {}
        for host in self._hosts:
            if limit and host._name not in limit:
                continue
            ret[host._name] = host.fw_show()

        return ret

    def cmd_inventory(self, structured=True, native_type=False, limit=None):
        "Show host inventory"

        return self._inventory


