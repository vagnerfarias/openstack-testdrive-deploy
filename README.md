# OpenStack Test Drive Deployment on Ravello

This set of playbooks will automate the deployment and configuration of OpenStack Test Drive labs on Ravello.

## Pre-requisites

1. git package
1. openstack-testdrive-deploy contents (aka this repository)
1. ansible

### Cloning openstack-testdrive-deploy repository

Clone the openstack-testdrive-deploy repository to the desired location, as a regular user.

```
$ cd ~
$ git clone https://github.com/vagnerfarias/openstack-testdrive-deploy.git
```

## Configuration

All the files mentioned below are relative to the directory where openstack-testdrive-deploy was cloned. For example, ~/openstack-testdrive-deploy.

### Ravello credentials

Edit group\_vars/all/credentials and include your Ravello domain/username and password.

ravello\_login\_username: 0123456/your@email.com
ravello\_login\_password: YourPassword

### General configuration

Edit group\_vars/all/main.yaml and set:

Variable Name | Example | Explanation
--------------|---------|------------
country | BR, MX, SAC, etc | Region where you are allowed to create resources on Ravello.
customer\_name | MyCustomer, OpenStack-Day, etc | Name of customer or some event identifier.
ravello\_keypair\_name | LATAM-BR-mykey | The name of your own keypair in Ravello. All applications will be created with this keypair, so that you can access the environment.
shared\_ssh\_public\_key | ./shared-key.pub | The path (absolute or relative) to the *public* key to be injected in every lab. The corresponding *secret* key needs to be made available to all attendees.

The remaining variables shouldn't be modified, unless you understand what they do.

### Number of labs and expiration time

Edit roles/ravello.applications\_create/defaults/main.yaml and modify *ravello\_app\_list* variable, uncommenting as many lines as applications in Ravello you need. Each attendee should have its own lab.

~~~
ravello\_app\_list:
- [ app\_name: "{{ bucket\_type }}-{{ ravello\_app\_name }}-{{ customer\_name }}-Instructor" ]
- [ app\_name: "{{ bucket\_type }}-{{ ravello\_app\_name }}-{{ customer\_name }}-W1" ]
\#- [ app\_name: "{{ bucket\_type }}-{{ ravello\_app\_name }}-{{ customer\_name }}-W2" ]
~~~

If required, change the expiration time through the variable *ravelo\_expiration\_time\_min*. Default is 9 hours (540 minutes).

~~~
ravello\_expiration\_time\_min: 540
~~~

Remaining variables in this file usually shouldn't be modified.

## Labs deployment

In order to deploy the labs, run the create-ravello-apps playbook, as follows:

~~~
$ ansible-playbook create-ravello-apps.yaml
~~~

## Labs post-configuration

After the labs are deployed and all VMs are up, it's required to run an additional playbook which will:

* configure the shared ssh key in every environment, so that attendees have access to the labs
* configure OpenStack nova NoVNC proxy to the proper value, so that attendees can access the console of the virtual instances they create.

To run the post-configuration playbook, run the following command:

~~~
$ ansible-playbook config-apps.yaml
~~~


