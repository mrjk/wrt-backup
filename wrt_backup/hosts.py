import os
import datetime
import json
import sh
import re
import logging
from ruamel import yaml

from pprint import pprint

from xdg import BaseDirectory

from wrt_backup.common import uci2dict
import wrt_backup.errors as error


logger = logging.getLogger(__name__)

class Host:
    "This is a router class"

    def __init__(self, name, host=None, port=None, user=None, path='.', backup_all=False, backup_state=False):

        self.prepare(name, host=host, port=port, user=user)
        self.path = os.path.join(path, name)
        self.backup_all = backup_all
        self.backup_state = backup_state
        self.date_now = datetime.datetime.now()


    def prepare(self, name, host=None, port=None, user=None):

        if not host:
            assert False, f"Missing IP for host {name}"

        self._host = host
        self._name = name
        self._user = user or 'root'
        self._port = port or '22'

        ssh_args = [
                "-l", self._user,
                "-p", self._port,
                self._host,
        ]
        self.ssh_conn = sh.ssh.bake(*ssh_args)

    def cmd_backup_states(self, fmt="md"):
        "Get command outputs"


        cmds = {
                #"uptime": "uptime",
                #"ps": "ps w",
                #"mem": "free -h",

                "df": "df -h",
                "ip_addresses": "ip a",
                "ip_route": "ip route",
                "backup_files": "sysupgrade -l",
                "uci_export": "uci export",
                "uci_show": "uci show",
            }

        ret = {}
        for name, cmd in cmds.items():
            out = self.ssh_conn(cmd)
            ret[name] = out


        # Loop for switch config
        # TODO


        if fmt == 'json':
            # Save results
            dest_file = os.path.join(self.path, "state.json")
            out_file = open(dest_file, "w")
            json.dump(ret, out_file, indent = 4)
            out_file.close()
        else:
            dest_file = os.path.join(self.path, "state.md")
            str_out = [f"# Configuration for {self._name}/{self._host}\n"]
            for name, output in ret.items():
                str_out.append(f"\n## {name}\n\n")
                str_out.append("```")
                str_out.append(output)
                str_out.append("```")

            str_out = '\n'.join(str_out) + '\n'

            out_file = open(dest_file, "w")
            out_file.write(str_out)
            out_file.close()

        logger.info ("Created state file: %s", dest_file)



    def check_git_status(self):
        "Check if git is in a correct state"
        target = self.path

        states = sh.git("status", "--porcelain", ".", _cwd=target)

        failed = []
        for state in states.split('\n'):
            splitted = state.split(' ',2)

            if len(splitted) < 2:
                continue

            opts = splitted[0]
            file = splitted[1]
            if opts.startswith('?'):
                failed.append(f"Please add, commit or remove from git file: {file}")

        if failed:
            msg = "Some errors has been discovered:\n" + '\n'.join(failed)
            raise error.UncommitedWork(msg)

    def cmd_backup(self, list_files=False):
        "Backup an host"

        conn = self.ssh_conn
        if list_files:
            out = conn("sysupgrade -l")
            print (out)
            return

        self.check_git_status()

        # Run state backup
        if self.backup_state:
            self.cmd_backup_states()

        # Create backup directory
        if not os.path.isdir(self.path):
            os.makedirs(self.path)
        backup_name = os.path.join(self.path, f"backup-{self._name}.tar.gz")

        # Prepare backup command
        logger.info("Start device backup")
        bckp_cmd = "sysupgrade -b - -k"
        if self.backup_all:
            bckp_cmd = bckp_cmd + " -o"
        out = conn(bckp_cmd, _out=backup_name)

        # Decompress backup archive
        logger.debug("Start backup extraction")
        tmp_dest = os.path.join(self.path, "config")
        if not os.path.isdir(tmp_dest):
            os.makedirs(tmp_dest)
        sh.tar("-xf", backup_name, "-C", tmp_dest)

        # Save archive
        tmp_dest = os.path.join(self.path, "archives")
        file_dest = f"{self._name}-{self.date_now.strftime('%Y%m%d-%H%M%S')}.tar.gz"
        if not os.path.isdir(tmp_dest):
            os.makedirs(tmp_dest)
        tmp_dest = os.path.join(tmp_dest, file_dest)
        sh.mv(backup_name, tmp_dest)
        logger.debug("Save backup archive in: %s", tmp_dest)


    def uci_show(self, structured=True, native_type=False):
        "Return uci show on device"
        conn = self.ssh_conn
        out = conn("uci show")

        if structured:
            return uci2dict(out, native_type=native_type)
        return str(out)


