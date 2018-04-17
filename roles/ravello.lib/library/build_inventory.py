#!/usr/bin/python

DOCUMENTATION = '''
---

'''

EXAMPLES = '''

'''
from ansible.module_utils.basic import AnsibleModule
import json
import requests
import re

def run_module():

    module_args = dict(
        app_list = dict(type='dict', required = True, default = None),
        vm_list = dict(type='list', required = True, default=None),
        outfile = dict(required = True, default=None),
        user = dict(required = True, default = None),
        password = dict(required = True, default = None),
        keyfile = dict(required = True, default = None)
    )

    result = dict(
        changed=False,
        inventory={}
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    user = module.params['user']
    password = module.params['password']
    all_apps = module.params['app_list']['results']
    vm_list = module.params['vm_list']
    outfile = module.params['outfile']
    keyfile = module.params['keyfile']
    
    group = {}
    group['director-all'] = []
    group['overcloud-all:children'] = []

    #####
    ## loop through apps.results
    ##  get id for director and controller
    ##  loop through director and controller
    ##     send request to get fqdn for each vm (https://cloud.ravellosystems.com/api/v1/applications/{{ application_id }}/vms/{{ vm_id }}/fqdn;deployment)
    ##     store fqdn for director and controller (for this app)
    ##
    
    headers = {"Accept" : "application/json", "Content-Type" : "application/json"}
    r = ""

    if module.params['user']:
        for app in all_apps:
            #print json.dumps(app)
            app_name = app['json']['name']
            group['overcloud-all:children'].append(app_name)
            group[app_name] = []
            group[app_name+':vars'] = []
            group[app_name].append('controller-'+app_name+' nodeIp=172.16.1.22')
            group[app_name].append('compute1-'+app_name+' nodeIp=172.16.1.25')
            group[app_name].append('compute2-'+app_name+' nodeIp=172.16.1.24')

            url = "https://cloud.ravellosystems.com/api/v1/applications/{0}/vms".format(app['json']['id'])

            r = requests.get(
              url, auth = (user,password),headers=headers,)
            if r.status_code != 404:
                resources = r.json()
        
                for resource in resources:
                    vm_id = resource['id']
                    for vm in vm_list:
                        vm_name = vm['vm_name']
                        if resource['name'] == vm_name:
                            url = "https://cloud.ravellosystems.com/api/v1/applications/{0}/vms/{1}/fqdn;deployment".format(app['json']['id'],vm_id)
                            r = requests.get(
                                    url, auth = (user,password),headers=headers,)
                            if r.status_code != 404:
                                vm_fqdn = r.json()['value']
                                if re.search('^controller',vm_name.encode('utf-8')) is not None:
                                    group[app_name+':vars'].append('controllerFqdn=' +vm_fqdn)
                                elif re.search('director',vm_name.encode('utf-8')) is not None:
                                    group[app_name+':vars'].append('ansible_ssh_common_args=\'-o ProxyCommand=\"ssh -W {{ nodeIp }}:%p -q cloud-user@' + vm_fqdn + ' -i ' + keyfile + '\"\'')
                                    group['director-all'].append('director-' + app_name + ' ansible_host=' + vm_fqdn)
                            else:
                                module.fail_json(msg='Error getting FQDN for VM', **result)

            else:
                module.fail_json(msg='Error getting VM information', **result)





    with open(outfile,'w') as f:
        f.write('# DON\'T EDIT THIS FILE. IT WILL BE OVERWRITTEN\n\n')
        f.write('localhost\n\n')
        for section, items in sorted(group.iteritems()):
            f.write('[' + section + ']\n')
            for index, line in enumerate(items):
                f.write(line + '\n')
            f.write('\n')

    result['changed'] = True
    result['inventory'] = group
        
    module.exit_json(**result)




def main():
    run_module()

if __name__ == '__main__':
    main()

