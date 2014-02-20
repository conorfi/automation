"""
Runners to help with testing lifecycle
"""

from fabric.api import local, shell_env, abort, lcd
from fabric.state import env, win32
from fabric import operations
import os
from framework.common_env import get_environments, get_test_sets, \
    TEST_ENVIRONMENT

# exposed tasks
__all__ = ['jenkins_nose', 'nose', 'pep8']


working_dir = os.path.dirname(__file__)


# monkey-patching fix for fabric to make Windows SET work with absolute paths
# TODO: taken from blAAM, integrate blAAM as required lib?
def _prefix_env_vars(command, local=False):
    """
    Prefixes ``command`` with any shell environment vars, e.g. ``PATH=foo ``.

    Currently, this only applies the PATH updating implemented in
    `~fabric.context_managers.path` and environment variables from
    `~fabric.context_managers.shell_env`.

    Will switch to using Windows style 'SET' commands when invoked by
    ``local()`` and on a Windows localhost.
    """
    env_vars = {}

    # path(): local shell env var update, appending/prepending/replacing $PATH
    path = env.path
    if path:
        if env.path_behavior == 'append':
            path = '$PATH:\"%s\"' % path
        elif env.path_behavior == 'prepend':
            path = '\"%s\":$PATH' % path
        elif env.path_behavior == 'replace':
            path = '\"%s\"' % path

        env_vars['PATH'] = path

    # shell_env()
    env_vars.update(env.shell_env)

    if env_vars:
        set_cmd, exp_cmd, quote, glue = '', '', '"', ' '
        if win32 and local:
            set_cmd = 'SET '
            # disable quotes in Windows to support absolute paths
            quote = ''
            glue = ' && '
        else:
            exp_cmd = 'export '

        exports = glue.join(
            '%(set)s%(key)s=%(quote)s%(value)s%(quote)s' % {
                'set': set_cmd,
                'key': k,
                'value': v if k == 'PATH' else operations._shell_escape(v),
                'quote': quote
            }
            for k, v in env_vars.iteritems()
        )
        shell_env_str = '%s%s && ' % (exp_cmd, exports)
    else:
        shell_env_str = ''

    return shell_env_str + command
operations._prefix_env_vars = _prefix_env_vars


def _pythonpath(cwd):
    if os.name == 'nt':
        base_path = '%PYTHONPATH%'
    else:
        base_path = '$PYTHONPATH'
    return os.pathsep.join([cwd, base_path])


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
    environments = get_environments()
    test_sets = get_test_sets()

    if not test_set in test_sets:
        abort('Not a valid test set.')

    if not environment in environments:
        abort('Not a valid environment.')

    # get NOSE_TESTCONFIG_AUTOLOAD_PYTHON location
    test_config_filename = environments[environment]['file']
    test_config = os.path.join(working_dir,
                               'env_config',
                               test_config_filename)

    # get nose command
    nose_command = get_nose_command(test_config, test_set, test_sets[test_set],
                                    working_dir, report)

    with shell_env(PYTHONPATH=_pythonpath(working_dir)):
        local(nose_command)


def pep8():
    """
    Style Checker: Runs pep8 validation over python files.
    """
    with lcd(working_dir):
        local('pep8 . --exclude lib')


def get_nose_command(test_config, test_set, test_set_map, folder, report=False):
    """
    Gets nose command for a set test
    :param test_config: path to the testconfig
    :param test_set: name for the test set to run
    :param test_set_map: map for the test_set
    :param folder: automation folder
    :param report: if a report should be created
    """
    # base configuration
    base_config = '--tc-file %s --tc-format python' % test_config

    # reporting configuration
    report_config = '--with-xunit --xunit-file=%s/nosetests.xml' \
                    % folder if report else ''

    # service under test tests location
    service_location = os.path.join(
        folder, 'test_cases', 'service', test_set_map.get('folder', test_set)
    )

    # select specific file to run tests from
    test_case_filename = test_set_map.get('filename', None)
    test_locations = ""
    if test_case_filename:
        service_location = '-w ' + service_location
        for tc_file in test_case_filename:
            test_locations += " " + tc_file


    # ignore specific file
    ignore_file = test_set_map.get('ignore_filename', None)
    ignore_config = ""

    if ignore_file:
        for ignore in ignore_file:
            ignore_config += '--ignore-files=%s ' % ignore

    # nose command
    nose_command = 'nosetests %s %s %s %s %s' % (
        service_location, test_locations,
        base_config, report_config, ignore_config
    )

    return nose_command
