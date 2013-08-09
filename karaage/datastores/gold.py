# Copyright 2007-2010 VPAC
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

""" Gold datastore. """

import subprocess
import csv
import logging
logger = logging.getLogger(__name__)

from karaage.datastores import base


class GoldDataStore(base.BaseDataStore):
    """ Gold datastore. """

    def __init__(self, config):
        super(GoldDataStore, self).__init__(config)
        self.gold_prefix = config.get('GOLD_PREFIX', [])
        self.gold_path = config.get('GOLD_PATH', "/usr/local/gold/bin")
        self.gold_null_project = config.get('GOLD_NULL_PROJECT', "default")

    @staticmethod
    def _filter_string(value):
        """ Filter the string so Gold doesn't have heart failure."""
        if value is None:
            value = ""

        # replace whitespace with space
        value = value.replace("\n"," ")
        value = value.replace("\t"," ")

        # CSV seperator
        value = value.replace("|"," ")

        # remove leading/trailing whitespace
        value = value.strip()

        # hack because gold doesn't quote sql correctly
        value = value.replace("\\","")

        # Used for stripping non-ascii characters
        value = ''.join(c for c in value if ord(c) > 31 and ord(c) < 127)

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
        if (len(value) > length):
            return value[:length] + "..."
        else:
            return value

    def _call(self, command, ignore_errors=None):
        """ Call remote command with logging. """
        if ignore_errors is None:
            ignore_errors = []
        cmd = []
        cmd.extend(self.gold_prefix)
        cmd.append("%s/%s"%(self.gold_path, command[0]))
        cmd.extend(command[1:])
        command = cmd

        logger.debug("Cmd %s"%command)
        null = open('/dev/null', 'w')
        retcode = subprocess.call(command, stdout=null, stderr=null)
        null.close()

        if retcode in ignore_errors:
            logger.debug("<-- Cmd %s returned %d (ignored)"%(command, retcode))
            return

        if retcode:
            logger.error("<-- Cmd %s returned: %d (error)"%(command, retcode))
            raise subprocess.CalledProcessError(retcode, command)

        logger.debug("<-- Returned %d (good)"%(retcode))
        return

    def _read_gold_output(self, command):
        """ Read CSV delimited input from Gold. """
        cmd = []
        cmd.extend(self.gold_prefix)
        cmd.append("%s/%s"%(self.gold_path, command[0]))
        cmd.extend(command[1:])
        command = cmd

        logger.debug("Cmd %s"%command)
        null = open('/dev/null', 'w')
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=null)
        null.close()

        results = []
        reader = csv.reader(process.stdout, delimiter="|")

        try:
            headers = reader.next()
            logger.debug("<-- headers %s"%headers)
        except StopIteration:
            logger.debug("Cmd %s headers not found"%command)
            headers = []

        for row in reader:
            logger.debug("<-- row %s"%row)
            this_row = {}

            i = 0
            for i in range(0, len(headers)):
                key = headers[i]
                value = row[i]
                this_row[key] = value

            results.append(this_row)

        retcode = process.wait()
        if retcode != 0:
            logger.error("<-- Cmd %s returned %d (error)"%(command, retcode))
            raise subprocess.CalledProcessError(retcode, command)

        if len(headers) == 0:
            logger.debug("Cmd %s didn't return any headers."%command)

        logger.debug("<-- Returned: %d (good)"%(retcode))
        return results

    def get_gold_user(self, username):
        """ Get the user details from Gold. """
        cmd = [ "glsuser", "-u", username, "--raw" ]
        results = self._read_gold_output(cmd)

        if len(results) == 0:
            return None
        elif len(results) > 1:
            logger.error("Command returned multiple results for '%s'."%username)
            raise RuntimeError("Command returned multiple results for '%s'."
                    %username)

        the_result = results[0]
        the_name = the_result["Name"]
        if username.lower() != the_name.lower():
            logger.error("We expected username '%s' but got username '%s'."
                    %(username,the_name))
            raise RuntimeError("We expected username '%s' "
                    "but got username '%s'."%(username,the_name))

        return the_result

    def get_gold_user_balance(self, username):
        """ Get the user balance details from Gold. """
        cmd = [ "gbalance", "-u", username, "--raw" ]
        results = self._read_gold_output(cmd)

        if len(results) == 0:
            return None

        return results

    # AAAAA
    def get_gold_project(self, projectname):
        """ Get the project details from Gold. """
        cmd = [ "glsproject", "-p", projectname, "--raw" ]
        results = self._read_gold_output(cmd)

        if len(results) == 0:
            return None
        elif len(results) > 1:
            logger.error("Command returned multiple results for '%s'."
                    %projectname)
            raise RuntimeError("Command returned multiple results for '%s'."
                    %projectname)

        the_result = results[0]
        the_project = the_result["Name"]
        if projectname.lower() != the_project.lower():
            logger.error("We expected projectname '%s' "
                    "but got projectname '%s'."%(projectname,the_project))
            raise RuntimeError("We expected projectname '%s' "
                    "but got projectname '%s'."%(projectname,the_project))

        return the_result

    def get_gold_users_in_project(self, projectname):
        """ Get list of users in project from Gold. """
        gold_project = self.get_gold_project(projectname)
        if gold_project is None:
            logger.error("Project '%s' does not exist in Gold"
                    %(projectname))
            raise RuntimeError("Project '%s' does not exist in Gold"
                    %(projectname))

        if gold_project["Users"] == "":
            return []
        else:
            return gold_project["Users"].lower().split(",")

    # BBBBBBB
    def get_gold_projects_in_user(self, username):
        """ Get list of projects in user from Gold. """
        gold_balance = self.get_gold_user_balance(username)
        if gold_balance is None:
            logger.error("User '%s' does not exist in Gold"%(username))
            raise RuntimeError("User '%s' does not exist in Gold"%(username))

        projects = []
        for bal in gold_balance:
            projects.append(bal["Name"])
        return projects

    # CCCCCCCCC
    def save_institute(self, institute):
        """ Called when institute is created/updated. """
        name = institute.name
        logger.debug("save_institute '%s'"%name)

        # institute created
        # institute updated

        if institute.is_active:
            # date_deleted is not set, user should exist
            logger.debug("institute is active")

            self._call(["goldsh", "Organization", "Create", "Name=%s"%name],
                    ignore_errors=[185])
        else:
            # date_deleted is not set, user should not exist
            logger.debug("institute is not active")
            # delete Gold organisation if institute marked as deleted
            self._call(["goldsh", "Organization", "Delete", "Name==%s"%name])

        logger.debug("returning")
        return

    def delete_institute(self, institute):
        """ Called when institute is deleted. """
        name = institute.name
        logger.debug("institute_deleted '%s'"%name)

        # institute deleted
        self._call(["goldsh", "Organization", "Delete", "Name==%s"%name])

        logger.debug("returning")
        return

    def save_account(self, account):
        """ Called when account is created/updated. """
        username = account.username
        logger.debug("account_saved '%s'"%username)

        # retrieve default project, or use null project if none
        default_project_name = self.gold_null_project
        if account.default_project is not None:
            default_project_name = account.default_project.pid

        # account created
        # account updated

        gold_user = self.get_gold_user(username)
        if account.date_deleted is None:
            # date_deleted is not set, user should exist
            logger.debug("account is active")

            if gold_user is None:
                # create user if doesn't exist
                self._call([
                    "gmkuser", "-A",
                    "-p", default_project_name,
                    "-u", username])
            else:
                # or just set default project
                self._call([
                    "gchuser",
                    "-p", default_project_name,
                    "-u", username])

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
            for project in account.person.projects.all():
                self._call(
                    ["gchproject", "--add-user", username, "-p", project.pid],
                    ignore_errors=[74])
        else:
            # date_deleted is not set, user should not exist
            logger.debug("account is not active")
            if gold_user is not None:
                # delete Gold user if account marked as deleted
                self._call(["grmuser", "-u", username], ignore_errors=[8])

        logger.debug("returning")
        return

    def delete_account(self, account):
        """ Called when account is deleted. """
        username = account.username
        logger.debug("account_deleted '%s'"%username)

        # account deleted

        gold_user = self.get_gold_user(username)
        if gold_user is not None:
            self._call(["grmuser", "-u", username], ignore_errors=[8])

        logger.debug("returning")
        return

    def set_account_password(self, account, raw_password):
        """ Account's password was changed. """
        pass

    def set_account_username(self, account, old_username, new_username):
        """ Account's username was changed. """
        # FIXME
        pass

    def account_exists(self, username):
        """ Does the account exist? """
        gold_user = self.get_gold_user(username)
        return gold_user is not None

    def get_account_details(self, account):
        """ Get the account details """
        result = self.get_gold_user(account.username)
        if result is None:
            result = {}
        return result

    def add_account_to_group(self, account, group):
        """ Add account to group. """
        username = account.username
        for project in group.project_set.all():
            projectname = project.pid
            logger.debug("add user '%s' to project '%s'"%
                    (username, projectname))
            self._call([
                "gchproject",
                "--add-user", username,
                "-p", projectname],
                ignore_errors=[74])

    def remove_account_from_group(self, account, group):
        """ Remove account from group. """
        username = account.username
        for project in group.project_set.all():
            projectname = project.pid
            logger.debug("delete user '%s' to project '%s'"%
                    (username,projectname))
            self._call([
                "gchproject",
                "--del-users", username,
                "-p", projectname])

    def save_group(self, group):
        """ Group was saved. """
        pass

    def delete_group(self, group):
        """ Group was deleted. """
        pass

    def set_group_name(self, group, old_name, new_name):
        """ Group was renamed. """
        pass

    def get_group_details(self, group):
        """ Get the group details. """
        combined = {}
        for project in group.project_set.all():
            result = self.get_gold_project(project.pid)
            if result is None:
                result = {}
            for i, j in result.iteritems():
                combined[project.pid + "_" + i] = j
        return combined

    def save_project(self, project):
        """ Called when project is saved/updated. """
        pid = project.pid
        logger.debug("project_saved '%s'"%pid)

        # project created
        # project updated

        if project.is_active:
            # project is not deleted
            logger.debug("project is active")
            gold_project = self.get_gold_project(pid)
            if gold_project is None:
                self._call(["gmkproject", "-p", pid, "-u", "MEMBERS"])

            # update project meta information
            name = self._truncate(project.name, 40)
            self._call([
                "gchproject",
                "-d", self._filter_string(name),
                "-p", pid])
            self._call([
                "gchproject",
                "-X", "Organization=%s"%
                    self._filter_string(project.institute.name),
                "-p", pid])
        else:
            # project is deleted
            logger.debug("project is not active")
            gold_project = self.get_gold_project(pid)
            if gold_project is not None:
                self._call(["grmproject", "-p", pid])

        logger.debug("returning")
        return

    def delete_project(self, project):
        """ Called when project is deleted. """
        pid = project.pid
        logger.debug("project_deleted '%s'"%pid)

        # project deleted

        gold_project = self.get_gold_project(pid)
        if gold_project is not None:
            self._call(["grmproject", "-p", pid])

        logger.debug("returning")
        return
