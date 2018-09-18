# Copyright 2010-2011 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


class ViewBuilder(object):
    """OpenStack API base limits view builder."""

    limit_names = {}

    def __init__(self):
        self.limit_names = {
            "ram": ["maxTotalRAMSize"],
            "instances": ["maxTotalInstances"],
            "cores": ["maxTotalCores"],
            "key_pairs": ["maxTotalKeypairs"],
            "floating_ips": ["maxTotalFloatingIps"],
            "metadata_items": ["maxServerMeta", "maxImageMeta"],
            "injected_files": ["maxPersonality"],
            "injected_file_content_bytes": ["maxPersonalitySize"],
            "security_groups": ["maxSecurityGroups"],
            "security_group_rules": ["maxSecurityGroupRules"],
            "server_groups": ["maxServerGroups"],
            "server_group_members": ["maxServerGroupMembers"]
    }

    def build(self, absolute_limits, filtered_limits=None,
              max_image_meta=True):
        per_flavor_limits = self._build_per_flavor_limits(absolute_limits)
        absolute_limits = self._build_absolute_limits(
            absolute_limits, filtered_limits,
            max_image_meta=max_image_meta)

        output = {
            "limits": {
                "rate": [],
                "absolute": absolute_limits,
                "absolutePerFlavor": per_flavor_limits,
            },
        }

        return output

    def _build_absolute_limits(self, absolute_limits, filtered_limits=None,
                               max_image_meta=True):
        """Builder for absolute limits

        absolute_limits should be given as a dict of limits.
        For example: {"ram": 512, "gigabytes": 1024}.

        filtered_limits is an optional list of limits to exclude from the
        result set.
        """
        filtered_limits = filtered_limits or []
        limits = {}
        for name, value in absolute_limits.items():
            if (name in self.limit_names and
                    value is not None and name not in filtered_limits):
                for limit_name in self.limit_names[name]:
                    if not max_image_meta and limit_name == "maxImageMeta":
                        continue
                    limits[limit_name] = value
        return limits

    def _build_per_flavor_limits(self, absolute_limits):
        limits = {}
        for name, value in absolute_limits.items():
            if name.startswith('instances_'):
                flavorname = name[10:]
                limits[flavorname] = { 'maxTotalInstances': value }

        return limits
