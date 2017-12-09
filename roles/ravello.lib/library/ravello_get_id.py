#!/usr/bin/env python

DOCUMENTATION = '''
---

'''

EXAMPLES = '''

'''
from distutils.version import LooseVersion
from ansible.module_utils.basic import *
import logging
import json
import requests
import httplib2

def main():

  module = AnsibleModule(
    argument_spec = dict(
      user = dict(required = False, default = None),
      password = dict(required = False, default = None),
      token = dict(required = False, default = None),
      resource_type = dict(required=True, default = None,
                           choices=['applications',
                                    'blueprints',
                                    'images',
                                    'vms',
                                    'keypairs']),
      resource_name = dict(required = True, default = None),
      application_id = dict(required = False, default = None),
      failed_if_not_found = dict(required=False, type='bool', default = False),
    ),
    supports_check_mode = False
  )

  args = module.params

  ####################################################
  ## Determine URL
  ####################################################
  url = ""
  if args['resource_type'] == 'vms' and args['application_id']:
    url = "https://cloud.ravellosystems.com/api/v1/applications/{0}/vms".format(args['application_id'])
  else:
    url = "https://cloud.ravellosystems.com/api/v1/{0}".format(args['resource_type'])

  ####################################################
  ## Determine Authentication Method
  ####################################################
  headers = {"Accept" : "application/json", "Content-Type" : "application/json"}
  r = ""
  if args['user']:
    r = requests.get(
      url,
      auth = (args['user'], args['password']),
      headers = headers,
    )
  elif args['token']:
    headers['X-Ephemeral-Token-Authorization'] = args['token']
    r = requests.get(
      url,
      headers = headers,
    )
  else:
    module.fail_json(msg = "Neither User nor Token provided")

  resp = dict(found=False)

  if r.status_code != 404:
      resources = r.json()

      for resource in resources:
          if 'name' in resource.keys():
              if resource['name'] == args['resource_name']:
                 resp['found'] = True
                 resp['json'] = resource
                 module.exit_json(**resp)

  if args['failed_if_not_found']:
        module.fail_json(msg = "Unable to find the {0} named '{1}' in Ravello, please check if it exists".format(args['application_type'], args['application_name']))
  else:
    module.exit_json(**resp)

if __name__ == "__main__":
    main()
