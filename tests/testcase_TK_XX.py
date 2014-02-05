#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
testcase_TK_XX.py module

Test Cases are coded as following:
      TK_XX
        TK: trunk test cases.
        XX: test number.
"""

from testcase_abstract import (TestCaseAbstract, TestFunctionalTestSuite,
    TestCaseError)
from trac.tests.functional import *
import inspect


class TK_01(TestCaseAbstract):

    """
    Test name: TK_01, case delivers sandbox on trunk

    Objective:
        * Verify sandbox creation message in ticket
        * Verify sandbox commit message in ticket
        * Verify sandbox close message in ticket
        * Verify trunk delivers message
        * Verify sandbox delivered message

    Conditions:
        * Repository structure:
            * branches
                * component (empty)
            * sandboxes
                * component (empty)
            * trunk
                * component (empty)
            * vendor
                * component (empty)

    Pass Criteria:
        * Expected ticket messages:
            * (In [x]) Creates tx for #1
            * (In [x]) Refs #x, Add driver.py module
            * (In [x]) Closes #x, Add driver-i2c.py module
    """

    def runTest(self):
        self.do_delivers()


class TK_02(TestCaseAbstract):

    """
    Test name: TK_02, case delivers no closed sandbox on trunk, deliver is
    rejected.

    Objective:
        * Verify sandbox creation message in ticket
        * Verify sandbox commit message in ticket
        * Verify sandbox close message in ticket
        * Verify trunk delivers message
        * Verify sandbox delivered message

    Conditions:
        * Repository structure:
            * branches
                * component (empty)
            * sandboxes
                * component (empty)
            * trunk
                * component (empty)
            * vendor
                * component (empty)

    Pass Criteria:
        * Error message displayed
            * Not all tickets closed, delivery rejected
    """

    def runTest(self):
        # Creates tickets for sandbox
        summary = 'ticket for delivers'
        ticket_id = self._tester.create_ticket(summary=summary,
                                               info={'keywords': ""})
        revs = self.sandbox_create(ticket_id, close=False)

        # Update trunk
        self.svn_update('trunk')

        # Merge trunk with sandbox
        self.svn_merge('trunk',
                       'sandboxes/t%s' % ticket_id,
                       revs)

        with self.assertRaises(TestCaseError) as cm:
            commit_msg = 'Delivers [%s:%s]' % revs
            self.svn_commit('trunk', commit_msg)

        msg = cm.exception.message
        expected_msg = 'Commit blocked by pre-commit hook'
        self.assertFalse(msg.find(expected_msg) == -1,
                         msg="Missing error message='%s', get " \
                         "message='%s'" % (expected_msg, msg))

        expected_msg = 'Not all tickets closed, delivery rejected'
        self.assertFalse(msg.find(expected_msg) == -1,
                         msg="Missing error message='%s', get " \
                         "message='%s'" % (expected_msg, msg))


class TK_03(TestCaseAbstract):

    """
    Test name: TK_03, case bring and revert a commit

    Objective:
        * Verify sandbox creation message in ticket
        * Verify sandbox commit message in ticket
        * Verify revert message
        * Verify sandbox ticket revert message

    Conditions:
        * Repository structure:
            * branches
                * component (empty)
            * sandboxes
                * component (empty)
            * trunk
                * component (empty)
            * vendor
                * component (empty)

    Pass Criteria:
        * Expected ticket messages:
            * (In [x]) Creates tx for #1
            * (In [x]) Refs #x, Add driver.py module
        * Delivers error message displayed:
            * Cannot deliver to /vendor/component branch
    """

    def runTest(self):
        # Creates tickets for sandbox
        ticket_id, deliver_rev = self.do_delivers()

        # Revert brings
        cset = deliver_rev
        self.svn_merge('trunk', 'trunk', (-1 * cset, ))

        # Commit reverts
        commit_msg = 'Reverts [%s]' % cset
        rev = self.svn_commit('trunk', commit_msg)

        # Get change set message
        cset_msg = self.svn_log_rev('trunk', cset)

        # Verify revision log
        msg = cset_msg.splitlines()[0]
        commit_msg = r"Reverts [%s] (''was: %s...'')" % (cset, msg)
        self.verify_log_rev('trunk', commit_msg, rev)

        # Get revision log of trunk delivers
        msg = self.svn_log_rev('trunk', deliver_rev)
        msg = msg.splitlines()[0]

        # Verify ticket entry
        commit_msg = 'Reverted in [%s] in /trunk  (was: %s)' % (rev, msg)
        self.verify_ticket_entry(ticket_id, rev, commit_msg, 'trunk')


class TK_04(TestCaseAbstract):

    """
    Test name: TK_04, case multi branches commit, the commit is rejected

    Objective:
        * Verify that multi-branches commit is rejected by pre-commit

    Conditions:
        * Repository structure:
            * branches
                * component (empty)
            * sandboxes
                * component (empty)
            * trunk
                * component (empty)
            * vendor
                * component (empty)

    Pass Criteria:
        * Error messages are displayed:
            * Commit blocked by pre-commit hook
            * Multiple branches in commit not allowed
    """

    def runTest(self):
        summary = 'ticket for test'
        ticket_id = self._tester.create_ticket(summary=summary,
                                               info={'keywords': ""})

        # Update root repository
        self.svn_update('')

        # Creates files
        for item in ('trunk', 'branches', 'vendor'):
            self.svn_add('%s/component' % item, 'test.py', '# dummy code')

        with self.assertRaises(TestCaseError) as cm:
            self.svn_commit('', 'Refs #%s, multi-branches commit' % ticket_id)

        msg = cm.exception.message
        expected_msg = 'Commit blocked by pre-commit hook'
        self.assertFalse(msg.find(expected_msg) == -1,
                         msg="Missing error message='%s', get "
                         "message='%s'" % (expected_msg, msg))

        expected_msg = 'Multiple branches in commit not allowed'
        self.assertFalse(msg.find(expected_msg) == -1,
                         msg="Missing error message='%s', get "
                         "message='%s'" % (expected_msg, msg))


class TK_05(TestCaseAbstract):

    """
    Test name: TK_05, case delivers with invalid ticket component Triage

    Objective:
        * Verify delivery is jrejected by pre-commit hook

    Conditions:
        * Repository structure:
            * branches
                * component (empty)
            * sandboxes
                * component (empty)
            * trunk
                * component (empty)
            * vendor
                * component (empty)

    Pass Criteria:
        * Error messages are displayed:
            * Commit blocked by pre-commit hook
            * No valid component, delivery rejected
    """

    def runTest(self):
        with self.assertRaises(TestCaseError) as cm:
            self.do_delivers(ticket_info=dict(component='Triage'))

        msg = cm.exception.message
        expected_msg = 'Commit blocked by pre-commit hook'
        self.assertFalse(msg.find(expected_msg) == -1,
                         msg="Missing error message='%s', get "
                         "message='%s'" % (expected_msg, msg))

        expected_msg = 'No valid component, delivery rejected'
        self.assertFalse(msg.find(expected_msg) == -1,
                         msg="Missing error message='%s', get "
                         "message='%s'" % (expected_msg, msg))


class TK_06(TestCaseAbstract):

    """
    Test name: TK_06, case delivers with invalid ticket component None

    Objective:
        * Verify delivery is rejected by pre-commit hook

    Conditions:
        * Repository structure:
            * branches
                * component (empty)
            * sandboxes
                * component (empty)
            * trunk
                * component (empty)
            * vendor
                * component (empty)

    Pass Criteria:
        * Error messages are displayed:
            * Commit blocked by pre-commit hook
            * No valid component, delivery rejected
    """

    def runTest(self):
        with self.assertRaises(TestCaseError) as cm:
            self.do_delivers(ticket_info=dict(component='None'))

        msg = cm.exception.message
        expected_msg = 'Commit blocked by pre-commit hook'
        self.assertFalse(msg.find(expected_msg) == -1,
                         msg="Missing error message='%s', get "
                         "message='%s'" % (expected_msg, msg))

        expected_msg = 'No valid component, delivery rejected'
        self.assertFalse(msg.find(expected_msg) == -1,
                         msg="Missing error message='%s', get "
                         "message='%s'" % (expected_msg, msg))


class TK_07(TestCaseAbstract):

    """
    Test name: TK_07, case brings from vendor in sandbox and delivers on
    trunk

    Objective:
        * Verify brings from vendor in sandbox and delivers on
    trunk work properly

    Conditions:
        * Repository structure:
            * branches
                * component (empty)
            * sandboxes
                * component (empty)
            * trunk
                * component (empty)
            * vendor
                * component (empty)

    Pass Criteria:
        * Expected ticket message:
            * (In [x]) Brings [y] (from /vendor/component)
    """

    def runTest(self):
        self.svn_update('')

        # Create file in vendor
        self.svn_add('vendor/component', 'vendor1.py', '# Dummy header')

        commit_msg = 'Admins , Add vendor.py'
        vendor_rev = self.svn_commit('vendor/component', commit_msg)
        self.verify_log_rev('vendor/component', commit_msg, vendor_rev)

        # Create sandboxe
        summary = 'ticket for sandbox'
        ticket_id = self._tester.create_ticket(summary=summary,
                                               info={'keywords': ""})

        self.sandbox_create(ticket_id, 'trunk', close=False)
        sandbox_path = 'sandboxes/t%s' % ticket_id

        # Merge sandbox with vendor changeset
        self.svn_merge(sandbox_path, 'vendor/component', (vendor_rev,))
        commit_msg = 'Brings [%s]' % vendor_rev
        rev = self.svn_commit(sandbox_path, commit_msg)

        msg = 'Brings [%s] (from [source:/vendor/component@%s /vendor/' \
              'component])' % (vendor_rev, vendor_rev)
        self.verify_log_rev(sandbox_path, msg, rev)

        msg = '(In [%s]) Brings [%s] (from /vendor/component)' % (rev,
                                                                 vendor_rev)
        self.verify_ticket_entry(ticket_id, rev, msg, sandbox_path)


def functionalSuite(suite=None):
    if not has_svn:
        raise Exception("Missing python-subversion module")

    def is_testcase(obj):
        """ is_testcase """

        if inspect.isclass(obj) and getattr(obj, "runTest", False):
            return True

        return False

    _, file_name = os.path.split(__file__)
    module_name = file_name.replace('.py', '')
    with file("./%s_test_docs.txt" % module_name, "wt") as _fd:
        module = __import__(module_name)

        testcases = inspect.getmembers(module, is_testcase)

        _fd.write("=== %s ===\n\n" % module_name)
        for _, test in testcases:
            _fd.write("{{{\n%s\n}}}\n\n\n" % inspect.getdoc(test))

    if not suite:
        suite = TestFunctionalTestSuite()
        suite.addTest(TK_01())
        suite.addTest(TK_02())
        suite.addTest(TK_03())
        suite.addTest(TK_04())
        suite.addTest(TK_05())
        suite.addTest(TK_06())
        suite.addTest(TK_07())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='functionalSuite')
