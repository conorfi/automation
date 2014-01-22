"""
Runners to help with testing lifecycle
"""

from fabric.api import local, shell_env, abort, lcd
import os
from framework.common_env import get_environments, get_test_sets, \
    TEST_ENVIRONMENT

# exposed tasks
__all__ = ['jenkins_nose', 'nose', 'pep8']


def jenkins_nose(test_set):
    """
    Jenkins task to run automation test set.
    :param test_set: name of the test set
    """
    nose(test_set, TEST_ENVIRONMENT, True)


def nose(test_set, environment, report=False):
    """
    Runs automation tests for a service (assuming that all apps are running)
    :param test_set: name of the test set
    :param environment: environment to run the tests against
    :param report: if a report should be created
    """
    cwd = os.getcwd()
    environments = get_environments()
    test_sets = get_test_sets()

    if not test_set in test_sets:
        abort('Not a valid test set.')

    if not environment in environments:
        abort('Not a valid environment.')

    # get NOSE_TESTCONFIG_AUTOLOAD_PYTHON location
    test_config_filename = environments[environment]['file']
    test_config = os.path.join(cwd,
                               'env_config',
                               test_config_filename)

    # get nose command
    nose_command = get_nose_command(test_set, test_sets[test_set], cwd, report)

    with shell_env(
            NOSE_TESTCONFIG_AUTOLOAD_PYTHON=test_config,
            PYTHONPATH='%s:$PYTHONPATH' % cwd):
        local(nose_command)


def pep8():
    """
    Style Checker: Runs pep8 validation over python files.
    """
    cwd = os.getcwd()
    with lcd(cwd):
        local('pep8 . --exclude lib')


def get_nose_command(test_set, test_set_map, folder, report=False):
    """
    Gets nose command for a set test
    :param test_set: name for the test set to run
    :param test_set_map: map for the test_set
    :param folder: automation folder
    :param report: if a report should be created
    """
    # reporting configuration
    report_config = '--with-xunit --xunit-file=%s/nosetests.xml' \
                    % folder if report else ''

    # service under test tests location
    service_location = os.path.join(
        folder, 'test_cases', 'service', test_set_map.get('folder', test_set)
    )

    # select specific file to run tests from
    test_case_filename = test_set_map.get('filename', None)
    if test_case_filename:
        service_location = os.path.join(service_location, test_case_filename)

    # ignore specific file
    ignore_file = test_set_map.get('ignore_filename', None)
    ignore_config = '--ignore-file %s' % ignore_file if ignore_file else ''

    # nose command
    nose_command = 'nosetests {0} {2} {1}'.format(
        service_location, ignore_config, report_config
    )

    return nose_command
