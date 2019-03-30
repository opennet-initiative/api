import argparse
import functools
import os
import sys

import paramiko

from django.core.management.base import BaseCommand

from on_geronimo.oni_model.models import AccessPoint


class IgnoreMissingHostKeyPolicy(paramiko.client.MissingHostKeyPolicy):

    def missing_host_key(self, client, hostname, key):
        return


class Command(BaseCommand):
    """
    Run a shell snippet on a few or multiple hosts.

    Example:

      python3 manage.py run_remote_action \
          --command 'ln -s ../tmp/database.json /www/opennet-ondataservice-export.json' \
          --password-file router-passwords.secret \
          --success-file=example-success-hosts.list \
          192.168.1.23 192.168.1.50

    The above will run the given command on any reachable host.
    The passwords to be tried are read from the password file (on by line).
    The IPs of all successfully connected hosts are stored in the optional
    "success file".  They will not be tried again in a repeated operation.
    Optionally a number of target addresses can be specified.  Otherwise
    *all* known hosts are targetted.

    Care should be taken when running the action on *all* hosts.  There
    should be compliance tests at the beginning, e.g. "[ -e /etc/banner ]"
    in order to execute actions on accesspoints only (not on servers).

    Please note, that passwords and private ssh keys are used for
    connection attempts.  Thus the given action may also be executed on
    servers.
    """

    def add_arguments(self, parser):
        parser.add_argument("--password-file", dest="password_file", required=True,
                            type=argparse.FileType("r"))
        parser.add_argument("--success-file", dest="success_file", type=str)
        parser.add_argument("--command", dest="command", type=str, required=True)
        parser.add_argument("targets", nargs="*", type=str)

    def _connect(self, client, ip, passwords):
        connection_command = functools.partial(client.connect, ip, username="root",
                                               look_for_keys=False)
        for password in passwords:
            try:
                connection_command(password=password)
                return True
            except paramiko.ssh_exception.AuthenticationException:
                pass
        else:
            return False

    @classmethod
    def _load_success_list_from_file(cls, filename):
        try:
            with open(filename, "r") as in_file:
                content = in_file.read()
            return {item for item in content.strip().split() if item}
        except IOError:
            return set()

    @classmethod
    def _save_success_list_to_file(self, filename, success_list):
        try:
            with open(filename, "w") as in_file:
                in_file.write(os.linesep.join(sorted(success_list)))
        except IOError as exc:
            self.stdout.write(self.style.ERROR("Failed to write to status file: {}".format(exc)))

    def handle(self, *args, targets=None, success_file=None, password_file=None, command=None,
               **kwargs):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(IgnoreMissingHostKeyPolicy())
        if success_file is None:
            success_accesspoints = set()
        else:
            success_accesspoints = self._load_success_list_from_file(success_file)
        passwords = password_file.read().splitlines()
        statistics = {
            "failed_authentication": 0,
            "failed_connection": 0,
            "success": 0,
        }
        queryset = AccessPoint.objects
        if targets:
            queryset = queryset.filter(main_ip__in=targets)
        for accesspoint in queryset.order_by("main_ip").exclude(main_ip__in=success_accesspoints):
            try:
                if not self._connect(client, accesspoint.main_ip, passwords):
                    self.stdout.write(self.style.SUCCESS("Failed to authenticate to {}"
                                                         .format(accesspoint.main_ip)))
                    statistics["failed_authentication"] += 1
                    continue
            except (OSError, TimeoutError, paramiko.ssh_exception.NoValidConnectionsError,
                    paramiko.ssh_exception.SSHException):
                self.stderr.write(self.style.NOTICE("Failed to connect to {}"
                                                    .format(accesspoint.main_ip)))
                statistics["failed_connection"] += 1
            else:
                client.exec_command(command)
                self.stdout.write(self.style.SUCCESS("Succeeded: {}".format(accesspoint.main_ip)))
                statistics["success"] += 1
                success_accesspoints.add(accesspoint.main_ip)
                client.close()
        if success_file is not None:
            self._save_success_list_to_file(success_file, success_accesspoints)
        self.stdout.write("Successes: {:d}".format(statistics["success"]))
        self.stdout.write("Connection failures: {:d}".format(statistics["failed_connection"]))
        self.stdout.write("Authentication failures: {:d}"
                          .format(statistics["failed_authentication"]))
