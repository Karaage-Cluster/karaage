# Copyright 2012-2014 Brian May
#
# This file is part of python-tldap.
#
# python-tldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-tldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-tldap  If not, see <http://www.gnu.org/licenses/>.

"""
This module implements a transaction manager that can be used to define
transaction handling in a request or view function. It is used by transaction
control middleware and decorators.

The transaction manager can be in managed or in auto state. Auto state means
the system is using a commit-on-save strategy (actually it's more like
commit-on-change). As soon as the .save() or .delete() (or related) methods are
called, a commit is made.

Managed transactions don't do those commits, but will need some kind of manual
or implicit commits or rollbacks.
"""
import sys
from functools import wraps

import tldap.backend


class TransactionManagementError(Exception):
    """
    This exception is thrown when something bad happens with transaction
    management.
    """
    pass


def enter_transaction_management(using=None):
    """
    Enters transaction management for a running thread. It must be balanced
    with the appropriate leave_transaction_management call, since the actual
    state is managed as a stack.

    The state and dirty flag are carried over from the surrounding block or
    from the settings, if there is no surrounding block (dirty is always false
    when no current block is running).
    """
    if using is None:
        for using in tldap.backend.connections:
            connection = tldap.backend.connections[using]
            connection.enter_transaction_management()
        return
    connection = tldap.backend.connections[using]
    connection.enter_transaction_management()


def leave_transaction_management(using=None):
    """
    Leaves transaction management for a running thread. A dirty flag is carried
    over to the surrounding block, as a commit will commit all changes, even
    those from outside. (Commits are on connection level.)
    """
    if using is None:
        for using in tldap.backend.connections:
            connection = tldap.backend.connections[using]
            connection.leave_transaction_management()
        return
    connection = tldap.backend.connections[using]
    connection.leave_transaction_management()


def is_dirty(using=None):
    """
    Returns True if the current transaction requires a commit for changes to
    happen.
    """
    if using is None:
        dirty = False
        for using in tldap.backend.connections:
            connection = tldap.backend.connections[using]
            if connection.is_dirty():
                dirty = True
        return dirty
    connection = tldap.backend.connections[using]
    return connection.is_dirty()


def is_managed(using=None):
    """
    Checks whether the transaction manager is in manual or in auto state.
    """
    if using is None:
        managed = False
        for using in tldap.backend.connections:
            connection = tldap.backend.connections[using]
            if connection.is_managed():
                managed = True
        return managed
    connection = tldap.backend.connections[using]
    return connection.is_managed()


def commit(using=None):
    """
    Does the commit itself and resets the dirty flag.
    """
    if using is None:
        for using in tldap.backend.connections:
            connection = tldap.backend.connections[using]
            connection.commit()
        return
    connection = tldap.backend.connections[using]
    connection.commit()


def rollback(using=None):
    """
    This function does the rollback itself and resets the dirty flag.
    """
    if using is None:
        for using in tldap.backend.connections:
            connection = tldap.backend.connections[using]
            connection.rollback()
        return
    connection = tldap.backend.connections[using]
    connection.rollback()

##############
# DECORATORS #
##############


class Transaction(object):
    """
    Acts as either a decorator, or a context manager.  If it's a decorator it
    takes a function and returns a wrapped function.  If it's a contextmanager
    it's used with the ``with`` statement.  In either event entering/exiting
    are called before and after, respectively, the function/block is executed.

    autocommit, commit_on_success, and commit_manually contain the
    implementations of entering and exiting.
    """
    def __init__(self, entering, exiting, using):
        self.entering = entering
        self.exiting = exiting
        self.using = using

    def __enter__(self):
        self.entering(self.using)

    def __exit__(self, exc_type, exc_value, traceback):
        self.exiting(exc_value, self.using)

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            # Once we drop support for Python 2.4 this block should become:
            # with self:
            #     func(*args, **kwargs)
            self.__enter__()
            try:
                res = func(*args, **kwargs)
            except:  # noqa: E722
                self.__exit__(*sys.exc_info())
                raise
            else:
                self.__exit__(None, None, None)
                return res
        return inner


def _transaction_func(entering, exiting, using):
    """
    Takes 3 things, an entering function (what to do to start this block of
    transaction management), an exiting function (what to do to end it, on both
    success and failure, and using which can be: None, indiciating transaction
    should occur on all defined servers, or a callable, indicating that using
    is None and to return the function already wrapped.

    Returns either a Transaction objects, which is both a decorator and a
    context manager, or a wrapped function, if using is a callable.
    """
    # Note that although the first argument is *called* `using`, it
    # may actually be a function; @autocommit and @autocommit('foo')
    # are both allowed forms.
    if callable(using):
        return Transaction(entering, exiting, None)(using)
    return Transaction(entering, exiting, using)


def commit_on_success(using=None):
    """
    This decorator activates commit on response. This way, if the view function
    runs successfully, a commit is made; if the viewfunc produces an exception,
    a rollback is made. This is one of the most common ways to do transaction
    control in Web apps.
    """
    def entering(using):
        enter_transaction_management(using=using)

    def exiting(exc_value, using):
        try:
            if exc_value is not None:
                if is_dirty(using=using):
                    rollback(using=using)
            else:
                commit(using=using)
        finally:
            leave_transaction_management(using=using)

    return _transaction_func(entering, exiting, using)


def commit_manually(using=None):
    """
    Decorator that activates manual transaction control. It just disables
    automatic transaction control and doesn't do any commit/rollback of its
    own -- it's up to the user to call the commit and rollback functions
    themselves.
    """
    def entering(using):
        enter_transaction_management(using=using)

    def exiting(exc_value, using):
        leave_transaction_management(using=using)

    return _transaction_func(entering, exiting, using)
