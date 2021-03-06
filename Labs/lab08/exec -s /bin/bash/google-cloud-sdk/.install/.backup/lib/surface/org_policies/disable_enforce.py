# -*- coding: utf-8 -*- #
# Copyright 2019 Google LLC. All Rights Reserved.
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
"""Disable-enforce command for the Org Policy CLI."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import copy

from googlecloudsdk.api_lib.orgpolicy import utils as org_policy_utils
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.org_policies import arguments
from googlecloudsdk.command_lib.org_policies import exceptions
from googlecloudsdk.command_lib.org_policies import interfaces


@base.Hidden
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class DisableEnforce(interfaces.OrgPolicyGetAndUpdateCommand):
  r"""Disable enforcement of a boolean constraint.

  Disables enforcement of a boolean constraint. A condition can optionally be
  specified to filter the resources this lack of enforcement applies to. The
  policy will be created if it does not exist.

  ## EXAMPLES

  To disable enforcement of the constraint `iam.disableServiceAccountCreation`
  on the project `foo-project`, run:

    $ {command} iam.disableServiceAccountCreation --project=foo-project

  To only disable enforcement for resources that have the label value `2222`
  associated with the label key `1111`, run:

    $ {command} iam.disableServiceAccountCreation --project=foo-project \
    --condition='resource.matchLabels("labelKeys/1111", "labelValues/2222")'
  """

  @staticmethod
  def Args(parser):
    super(DisableEnforce, DisableEnforce).Args(parser)
    arguments.AddConditionFlagToParser(parser)

  def UpdatePolicy(self, policy, args):
    """Disables enforcement by removing old rules containing the specified condition and creating a new rule with enforce set to False.

    This first does validation to ensure the specified action can be carried out
    according to the boolean policy contract. This contract states that exactly
    one unconditional rule has to exist on nonempty boolean policies, and that
    every conditional rule that exists on a boolean policy has to take the
    opposite enforcement value as that of the unconditional rule.

    This then searches for and removes the rules that contain the specified
    condition from the policy. In the case that the condition is not specified,
    the search is scoped to rules without conditions set. A new rule with a
    matching condition is created. The enforce field on the created rule is set
    to False.

    If the policy is empty and the condition is specified, then a new rule
    containing the specified condition is created. In order to comply with the
    boolean policy contract, a new unconditional rule is created as well with
    enforce set to True.

    Args:
      policy: messages.GoogleCloudOrgpolicyV2alpha1Policy, The policy to be
        updated.
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the Args method.

    Returns:
      The updated policy.
    """
    if policy.rules:
      unconditional_rules = org_policy_utils.GetMatchingRulesFromPolicy(
          policy, None)
      if not unconditional_rules:
        raise exceptions.BooleanPolicyValidationError(
            'An unconditional enforce value does not exist on the nonempty '
            'policy.'
        )
      unconditional_rule = unconditional_rules[0]

      if args.condition is None and len(policy.rules) > 1:
        # Unconditional enforce value cannot be changed on policies with more
        # than one rule.

        if unconditional_rule.enforce:
          raise exceptions.BooleanPolicyValidationError(
              'Unconditional enforce value cannot be the same as a conditional '
              'enforce value on the policy.'
          )

        # No changes needed.
        return policy

      if args.condition is not None and not unconditional_rule.enforce:
        raise exceptions.BooleanPolicyValidationError(
            'Conditional enforce value cannot be the same as the unconditional '
            'enforce value on the policy.'
        )

    new_policy = copy.deepcopy(policy)

    if not new_policy.rules and args.condition is not None:
      unconditional_rule, new_policy = org_policy_utils.CreateRuleOnPolicy(
          new_policy, None)
      unconditional_rule.enforce = True

    new_policy.rules = org_policy_utils.GetNonMatchingRulesFromPolicy(
        new_policy, args.condition)

    rule_to_update, new_policy = org_policy_utils.CreateRuleOnPolicy(
        new_policy, args.condition)
    rule_to_update.enforce = False

    return new_policy
