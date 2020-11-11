#!/usr/bin/python
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

DOCUMENTATION = '''
---
module: customer_master_key
short_description: Add/Delete customer master key from the OTC
extends_documentation_fragment: opentelekomcloud.cloud.otc
version_added: "0.0.1"
author: "Polina Gubina (@Polina-Gubina)"
description:
  - Add or Remove customer master key in OTC.
options:
  key:
    description:
      - Alias of a non default key or id.
      - It can be only name in order to create the resource.
      - It can be name or id in order to delete the resource.
    required: true
    type: str
  key_description:
    description:
      - CMK description.
    required: false
    type: str
  origin:
    description:
      - Origin of a CMK. The default value is kms.
      - 'kms' indicates that the CMK material is generated by KMS.
      - 'external' indicates that the CMK material is imported.
    required: false
    type: str
  sequence:
    description:
      - 36-byte serial number of a request message.
    required: false
    type: str
  pending_days:
    description:
      - Number of days after which a CMK is scheduled to be deleted.
      - Mandatory for deleting.
      - Default value is 7.
    required: false
    type: int
  enable:
    description:
      - This option allows you to enable a CMK. This will only have an effect if the key exists and is disabled.
    choices: ['yes', 'no']
    default: 'no'
    required: false
    type: str
  disable:
    description:
      - This option allows you to disable a CMK. This will only have an effect if the key exists and is enabled.
    choices: ['yes', 'no']
    default: 'no'
    required: false
    type: str
  cancel_deletion:
    description:
      - This option allows you to cancel key deletion. This will only have an effect if the key exists and is scheduled
       to be deleted.
    choices: ['yes', 'no']
    default: 'no'
    required: false
    type: str
  state:
    choices: [present, absent]
    default: present
    description: Instance state
    type: str
requirements: ["openstacksdk", "otcextensions"]
'''

RETURN = '''
key_id:
    description: CMK ID.
    returned: On success when C(state=present)
    type: str
    sample: "39007a7e-ee4f-4d13-8283-b4da2e037c69"
domain_id:
    description: User domain ID.
    returned: On success when C(state=present)
    type: str
    sample: "56007a7e-ee4f-4d13-8283-b4da2e037c69"
'''

EXAMPLES = '''
'''

from ansible_collections.opentelekomcloud.cloud.plugins.module_utils.otc import OTCModule


class VPCPeeringInfoModule(OTCModule):
    argument_spec = dict(
        key=dict(required=True),
        key_description=dict(required=False),
        origin=dict(required=False),
        sequence=dict(required=False),
        pending_days=dict(required=False, type='int'),
        enable=dict(required=False, choices=['yes', 'no'], default='no'),
        disable=dict(required=False, choices=['yes', 'no'], default='no'),
        cancel_deletion=dict(required=False, choices=['yes', 'no'], default='no'),
        state=dict(required=False, choices=['present', 'absent'], default='present')
    )

    module_kwargs = dict(
        supports_check_mode=True
    )

    def run(self):

        key = self.params['key']
        key_description = self.params['key_description']
        origin = self.params['origin']
        sequence = self.params['sequence']

        key = self.conn.kms.find_key(key, ignore_missing=True)

        if self.params['state'] == 'present':

            if not key:

                attrs = {'key': key}

                if self.params['key_description']:
                    attrs['key_description'] = key_description
                if self.params['origin']:
                    attrs['origin'] = origin
                if self.params['sequence']:
                    attrs['sequence'] = sequence

                key = self.conn.kms.create_key(**attrs)
                self.exit(changed=True, key=key)
            else:
                if self.params['enable'] == 'yes':
                    if key.key_state == "3":
                        enabled_key = self.conn.kms.enable_key(key)
                        self.exit(changed=True, key=enabled_key, msg='The key was enabled')
                    else:
                        self.fail_json(msg='Only a disabled key can be used.')
                if self.params['disable'] == 'yes':
                    if key.key_state == "2":
                        disabled_key = self.conn.kms.disable_key(key)
                        self.exit(changed=True, key=disabled_key, msg='The key was disabled')
                    else:
                        self.fail_json(msg='Only an enabled key can be used.')
                if self.params['cancel_deletion'] == 'yes':
                    if key.key_state == "4":
                        key_cancel_dltn = self.conn.kms.cancel_key_deletion(key)
                        self.exit(changed=True, key=key_cancel_dltn, msg='The deletion was canceled')
                    else:
                        self.fail_json(key=key, msg='Only an scheduled to be deleted key can be used.')
                else:
                    self.fail_json(msg="Key already exists")
        else:
            if key:
                if key.key_state != 4:
                    if self.params['pending_days']:
                        self.conn.kms.schedule_key_deletion(key, self.params['pending_days'])
                        self.exit(msg="The key is scheduled to be deleted.")
                    else:
                        self.conn.kms.schedule_key_deletion(key)
                else:
                    self.fail_json(msg="The key deletion is already scheduled.")
            else:
                self.fail_json(msg="The key doesn't exist")


def main():
    module = VPCPeeringInfoModule()
    module()


if __name__ == '__main__':
    main()
