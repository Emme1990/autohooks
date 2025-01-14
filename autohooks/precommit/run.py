# Copyright (C) 2019 Greenbone Networks GmbH
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import importlib
import inspect
import sys

from autohooks.config import load_config_from_pyproject_toml
from autohooks.utils import get_project_autohooks_plugins_path


def run():
    print('autohooks => pre-commit')

    config = load_config_from_pyproject_toml()

    plugins = get_project_autohooks_plugins_path()
    plugins_dir_name = str(plugins)

    if plugins.is_dir():
        sys.path.append(plugins_dir_name)

    for name in config.get_pre_commit_script_names():
        try:
            script = importlib.import_module(name)
            if not hasattr(script, 'precommit') or not inspect.isfunction(
                script.precommit  # pylint: disable=bad-continuation
            ):
                print(
                    'No precommit function found in plugin {}'.format(name),
                    file=sys.stderr,
                )
                return 0

            signature = inspect.signature(script.precommit)

            if signature.parameters:
                retval = script.precommit(config=config.get_config())
            else:
                print(
                    'precommit function without kwargs is deprecated.',
                    file=sys.stderr,
                )
                retval = script.precommit()

            if retval:
                return retval

        except ImportError as e:
            print(
                'An error occurred while importing pre-commit '
                'hook {}. {}. The hook will be ignored.'.format(name, e),
                file=sys.stderr,
            )
        except Exception as e:  # pylint: disable=broad-except
            print(
                'An error occurred while running pre-commit '
                'hook {}. {}. The hook will be ignored.'.format(name, e),
                file=sys.stderr,
            )

    if plugins_dir_name in sys.path:
        sys.path.remove(plugins_dir_name)

    return 0
