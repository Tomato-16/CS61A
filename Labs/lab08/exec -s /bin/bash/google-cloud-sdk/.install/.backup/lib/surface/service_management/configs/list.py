# -*- coding: utf-8 -*- #
# Copyright 2016 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""service-management configs list command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base


_ERROR = ('The `service-management configs list` command has been '
          'replaced by `endpoints configs list`.')


@base.Deprecate(is_removed=True, error=_ERROR)
class List(base.ListCommand):
  """Lists the configurations for a given service.

  This command lists all the configurations for a given service by ID.

  To get more detailed information about a specific configuration, run:

    $ {parent_command} describe

  ## EXAMPLES

  To list the configurations for a service named `my-service`, run:

    $ {command} --service my-service
  """

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    parser.add_argument(
        '--service',
        required=True,
        help='The name of service for which to list existing configurations.')
    parser.display_info.AddFormat("""
          table(
            id:label=CONFIG_ID,
            name:label=SERVICE_NAME
          )
        """)

  def Run(self, args):
    """Run 'service-management configs list'.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.
    """
    pass
