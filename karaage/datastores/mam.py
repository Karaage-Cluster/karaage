# Copyright 2014-2015 VPAC
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.

""" MOAB Account Manager datastore. """

import os.path
import subprocess
import csv
import logging
import sys

import karaage.common.trace as trace

from karaage.datastores import base

logger = logging.getLogger(__name__)

if sys.version_info < (3, 0):
    # Python2: csv module does not support unicode, we must use byte strings.

    def _input_csv(csv_data):
        for line in csv_data:
            assert isinstance(line, bytes)
            yield line

    def _output_csv(csv_line):
        for i, column in enumerate(csv_line):
            csv_line[i] = column.decode("ascii", errors='ignore')
            assert isinstance(csv_line[i], unicode)  # NOQA

else:
    # Python3: csv module does support unicode, we must use strings everywhere,
    # not byte strings

    def _input_csv(unicode_csv_data):
        for line in unicode_csv_data:
            assert isinstance(line, bytes)
            line = line.decode("ascii", errors='ignore')
            assert isinstance(line, str)
            yield line

    def _output_csv(csv_line):
        for column in csv_line:
            assert isinstance(column, str)


class MamDataStoreBase(base.MachineCategoryDataStore):
    """ MAM datastore. """
    version = None

    def __init__(self, config):
        super(MamDataStoreBase, self).__init__(config)
        self._prefix = config.get('PREFIX', [])
        self._path = config.get('PATH', "/usr/local/mam/bin")
        self._null_project = config.get('NULL_PROJECT', "default")

    @staticmethod
    def _filter_string(value):
        """ Filter the string so MAM doesn't have heart failure."""
        if value is None:
            value = ""

        # replace whitespace with space
        value = value.replace("\n", " ")
        value = value.replace("\t", " ")

        # CSV seperator
        value = value.replace("|", " ")

        # remove leading/trailing whitespace
        value = value.strip()

        # hack because MAM doesn't quote sql correctly
        value = value.replace("\\", "")

        # Used for stripping non-ascii characters
        value = ''.join(c for c in value if 31 < ord(c) < 127)

        return value

    @staticmethod
    def _truncate(value, arg):
        """
        Truncates a string after a given number of chars
        Argument: Number of chars to _truncate after
        """
        length = int(arg)
        if value is None:
            value = ""
        if len(value) > length:
            return value[:length] + "..."
        else:
            return value

    def _get_command(self, command):
        path = None
        split_path = self._path.split(":")
        for d in split_path:
            tmp_path = os.path.join(d, command[0])

            if len(self._prefix) == 0:
                # short cut process if no prefix
                if os.path.isfile(tmp_path) and os.access(tmp_path, os.X_OK):
                    path = tmp_path
                    break
            else:
                # don't short cut process
                cmd = []
                cmd.extend(self._prefix)
                cmd.extend(["test", "-x", tmp_path])
                result = subprocess.call(cmd)
                if result == 0:
                    path = tmp_path
                    break
        if path is None:
            raise RuntimeError(
                "Cannot find %s in %s" % (command[0], split_path))

        cmd = []
        cmd.extend(self._prefix)
        cmd.append(path)
        cmd.extend(command[1:])
        logger.debug("Cmd %s" % command)
        return cmd

    def _call(self, command, ignore_errors=None):
        """ Call remote command with logging. """
        if ignore_errors is None:
            ignore_errors = []

        command = self._get_command(command)
        logger.debug("Cmd %s" % command)
        null = open('/dev/null', 'w')
        retcode = subprocess.call(command, stdout=null, stderr=null)
        null.close()

        if retcode in ignore_errors:
            logger.debug(
                "<-- Cmd %s returned %d (ignored)" % (command, retcode))
            return

        if retcode:
            logger.error(
                "<-- Cmd %s returned: %d (error)" % (command, retcode))
            raise subprocess.CalledProcessError(retcode, command)

        logger.debug("<-- Returned %d (good)" % retcode)
        return

    def _read_output(self, command):
        """ Read CSV delimited input from MAM. """
        command = self._get_command(command)
        null = open('/dev/null', 'w')
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=null)
        null.close()

        results = []
        reader = csv.reader(_input_csv(process.stdout), delimiter="|")

        try:
            headers = reader.next()
            logger.debug("<-- headers %s" % headers)
        except StopIteration:
            logger.debug("Cmd %s headers not found" % command)
            headers = []

        for row in reader:
            _output_csv(row)

            logger.debug("<-- row %s" % row)
            this_row = {}

            i = 0
            for i in range(0, len(headers)):
                key = headers[i]
                value = row[i]
                this_row[key] = value

            results.append(this_row)

        process.stdout.close()
        retcode = process.wait()
        if retcode != 0:
            logger.error("<-- Cmd %s returned %d (error)" % (command, retcode))
            raise subprocess.CalledProcessError(retcode, command)

        if len(headers) == 0:
            logger.debug("Cmd %s didn't return any headers." % command)

        logger.debug("<-- Returned: %d (good)" % retcode)
        return results

    def check_version(self):
        assert self.version is not None

        cmd = ["goldsh", "System", "Query", "--raw"]
        results = self._read_output(cmd)

        for row in results:
            if row['Name'] != "Moab Accounting Manager":
                continue
            if row['Version'] == self.version:
                logger.info("Found MAM version %s" % self.version)
                return True
            else:
                return False

    def get_user(self, username):
        """ Get the user details from MAM. """
        cmd = ["glsuser", "-u", username, "--raw"]
        results = self._read_output(cmd)

        if len(results) == 0:
            return None
        elif len(results) > 1:
            logger.error(
                "Command returned multiple results for '%s'." % username)
            raise RuntimeError(
                "Command returned multiple results for '%s'." % username)

        the_result = results[0]
        the_name = the_result["Name"]
        if username.lower() != the_name.lower():
            logger.error(
                "We expected username '%s' but got username '%s'."
                % (username, the_name))
            raise RuntimeError(
                "We expected username '%s' but got username '%s'."
                % (username, the_name))

        return the_result

    def get_user_balance(self, username):
        """ Get the user balance details from MAM. """
        cmd = ["gbalance", "-u", username, "--raw"]
        results = self._read_output(cmd)

        if len(results) == 0:
            return None

        return results

    def _get_project_cmd(self, projectname):
        raise NotImplementedError()

    def get_project(self, projectname):
        """ Get the project details from MAM. """
        cmd = self._get_project_cmd(projectname)
        results = self._read_output(cmd)

        if len(results) == 0:
            return None
        elif len(results) > 1:
            logger.error(
                "Command returned multiple results for '%s'." % projectname)
            raise RuntimeError(
                "Command returned multiple results for '%s'." % projectname)

        the_result = results[0]
        the_project = the_result["Name"]
        if projectname.lower() != the_project.lower():
            logger.error(
                "We expected projectname '%s' "
                "but got projectname '%s'." % (projectname, the_project))
            raise RuntimeError(
                "We expected projectname '%s' "
                "but got projectname '%s'." % (projectname, the_project))

        return the_result

    def get_users_in_project(self, projectname):
        """ Get list of users in project from MAM. """
        ds_project = self.get_project(projectname)
        if ds_project is None:
            logger.error(
                "Project '%s' does not exist in MAM" % projectname)
            raise RuntimeError(
                "Project '%s' does not exist in MAM" % projectname)

        user_list = []
        if ds_project["Users"] != "":
            user_list = ds_project["Users"].lower().split(",")
        return user_list

    def get_projects_in_user(self, username):
        """ Get list of projects in user from MAM. """
        ds_balance = self.get_user_balance(username)
        if ds_balance is None:
            return []

        project_list = []
        for bal in ds_balance:
            project_list.append(bal["Name"])
        return project_list

    def _create_user(self, username, default_project_name):
        raise NotImplementedError()

    def _set_user_default_project(self, username, default_project_name):
        raise NotImplementedError()

    def _save_account(self, account, username):
        """ Called when account is created/updated. With username override. """

        # retrieve default project, or use null project if none
        default_project_name = self._null_project
        if account.default_project is not None:
            default_project_name = account.default_project.pid

        # account created
        # account updated

        ds_user = self.get_user(username)
        if account.date_deleted is None:
            # date_deleted is not set, user should exist
            logger.debug("account is active")

            if ds_user is None:
                # create user if doesn't exist
                self._create_user(username, default_project_name)
            else:
                # or just set default project
                self._set_user_default_project(username, default_project_name)

            # update user meta information
            self._call([
                "gchuser",
                "-n", self._filter_string(account.person.get_full_name()),
                "-u", username])
            self._call([
                "gchuser",
                "-E", self._filter_string(account.person.email),
                "-u", username])

            # add rest of projects user belongs to
            mam_projects = self.get_projects_in_user(username)
            for project in account.person.projects.all():
                if project.pid not in mam_projects:
                    self.add_account_to_project(account, project)
        else:
            # date_deleted is not set, user should not exist
            logger.debug("account is not active")
            if ds_user is not None:
                # delete MAM user if account marked as deleted
                self._call(["grmuser", "-u", username], ignore_errors=[8])

        return

    def save_account(self, account):
        """ Called when account is created/updated. """
        self._save_account(account, account.username)

    def _delete_account(self, account, username):
        """ Called when account is deleted. With username override. """

        # account deleted

        ds_user = self.get_user(username)
        if ds_user is not None:
            self._call(["grmuser", "-u", username], ignore_errors=[8])

        return

    def delete_account(self, account):
        """ Called when account is deleted. """
        self._delete_account(account, account.username)

    def set_account_password(self, account, raw_password):
        """ Account's password was changed. """
        pass

    def set_account_username(self, account, old_username, new_username):
        """ Account's username was changed. """
        self._delete_account(account, old_username)
        self._save_account(account, new_username)

    def add_account_to_project(self, account, project):
        """ Add account to project. """
        raise NotImplementedError()

    def remove_account_from_project(self, account, project):
        """ Remove account from project. """
        raise NotImplementedError()

    def account_exists(self, username):
        """ Does the account exist? """
        ds_user = self.get_user(username)
        return ds_user is not None

    def get_account_details(self, account):
        """ Get the account details """
        result = self.get_user(account.username)
        if result is None:
            result = {}
        return result

    def save_group(self, group):
        """ Group was saved. """
        pass

    def delete_group(self, group):
        """ Group was deleted. """
        pass

    def set_group_name(self, group, old_name, new_name):
        """ Group was renamed. """
        pass

    def _create_project(self, pid):
        raise NotImplementedError()

    def _set_project(self, pid, description, institute):
        raise NotImplementedError()

    def _delete_project(self, pid):
        raise NotImplementedError()

    def save_project(self, project):
        """ Called when project is saved/updated. """
        pid = project.pid

        # project created
        # project updated

        if project.is_active:
            # project is not deleted
            logger.debug("project is active")
            ds_project = self.get_project(pid)
            if ds_project is None:
                self._create_project(pid)

            # update project meta information
            name = self._truncate(project.name, 40)
            self._set_project(pid, name, project.institute)
        else:
            # project is deleted
            logger.debug("project is not active")
            ds_project = self.get_project(pid)
            if ds_project is not None:
                self._delete_project(pid)

        return

    def delete_project(self, project):
        """ Called when project is deleted. """
        pid = project.pid

        # project deleted

        ds_project = self.get_project(pid)
        if ds_project is not None:
            self._delete_project(pid)

        return

    def get_project_details(self, project):
        """ Get the project details. """
        result = self.get_project(project.pid)
        if result is None:
            result = {}
        return result

    def set_project_pid(self, project, old_pid, new_pid):
        """ Project's pid was changed. """
        # FIXME
        return

    def save_institute(self, institute):
        """ Called when institute is created/updated. """
        name = institute.name
        logger.debug("save_institute '%s'" % name)

        # institute created
        # institute updated

        if institute.is_active:
            # date_deleted is not set, user should exist
            logger.debug("institute is active")

            self._call(
                ["goldsh", "Organization", "Create", "Name=%s" % name],
                ignore_errors=[185])
        else:
            # date_deleted is not set, user should not exist
            logger.debug("institute is not active")
            # delete MAM organisation if institute marked as deleted
            self._call(["goldsh", "Organization", "Delete", "Name==%s" % name])

        logger.debug("returning")
        return

    def delete_institute(self, institute):
        """ Called when institute is deleted. """
        name = institute.name
        logger.debug("institute_deleted '%s'" % name)

        # institute deleted
        self._call(["goldsh", "Organization", "Delete", "Name==%s" % name])

        logger.debug("returning")
        return


class MamDataStore71(MamDataStoreBase):
    version = "7.1"

    def _get_project_cmd(self, projectname):
        cmd = ["glsproject", "-p", projectname, "--raw"]
        return cmd

    def _create_user(self, username, default_project_name):
        self._call([
            "gmkuser", "-A",
            "-p", default_project_name,
            "-u", username])

    def _set_user_default_project(self, username, default_project_name):
        self._call([
            "gchuser",
            "-p", default_project_name,
            "-u", username])

    def add_account_to_project(self, account, project):
        """ Add account to project. """
        username = account.username
        projectname = project.pid
        self._call([
            "gchproject",
            "--add-user", username,
            "-p", projectname],
            ignore_errors=[74])

    def remove_account_from_project(self, account, project):
        """ Remove account from project. """
        username = account.username
        projectname = project.pid
        self._call([
            "gchproject",
            "--del-users", username,
            "-p", projectname])

    def _create_project(self, pid):
        self._call(["gmkproject", "-p", pid, "-u", "MEMBERS"])

    def _set_project(self, pid, description, institute):
        self._call([
            "gchproject",
            "-d", self._filter_string(description),
            "-p", pid])
        self._call([
            "gchproject",
            "-X", "Organization=%s"
            % self._filter_string(institute.name),
            "-p", pid])

    def _delete_project(self, pid):
        self._call(["grmproject", "-p", pid])


class MamDataStore72(MamDataStoreBase):
    version = "7.2"

    def _get_project_cmd(self, projectname):
        cmd = ["glsaccount", "-a", projectname, "--raw"]
        return cmd

    def _create_user(self, username, default_project_name):
        self._call([
            "gmkuser", "-A",
            "-a", default_project_name,
            "-u", username])

    def _set_user_default_project(self, username, default_project_name):
        self._call([
            "gchuser",
            "-a", default_project_name,
            "-u", username])

    def add_account_to_project(self, account, project):
        """ Add account to project. """
        username = account.username
        projectname = project.pid
        self._call([
            "gchaccount",
            "--add-user", username,
            "-a", projectname],
            ignore_errors=[74])

    def remove_account_from_project(self, account, project):
        """ Remove account from project. """
        username = account.username
        projectname = project.pid
        self._call([
            "gchaccount",
            "--del-users", username,
            "-a", projectname])

    def _create_project(self, pid):
        self._call(["gmkaccount", "-a", pid, "-u", "MEMBERS"])

    def _set_project(self, pid, description, institute):
        self._call([
            "gchaccount",
            "-d", self._filter_string(description),
            "-a", pid])
        self._call([
            "gchaccount",
            "-X", "Organization=%s"
            % self._filter_string(institute.name),
            "-a", pid])

    def _delete_project(self, pid):
        self._call(["grmaccount", "-a", pid])


def MamDataStore(config):
    ds = MamDataStore71(config)
    if ds.check_version():
        return ds
    ds = MamDataStore72(config)
    if ds.check_version():
        return ds
    raise RuntimeError("We do not support this version of MAM")

trace.attach(trace.trace(logger), MamDataStoreBase)
trace.attach(trace.trace(logger), MamDataStore71)
trace.attach(trace.trace(logger), MamDataStore72)
