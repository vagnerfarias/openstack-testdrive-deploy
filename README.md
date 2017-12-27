# OpenStack Test Drive Deployment on Ravello

This set of playbooks will automate the deployment and configuration of OpenStack Test Drive labs on Ravello.

## Pre-requisites

1. git package
1. openstack-testdrive-deploy contents (aka this repository)
1. ansible
1. PuTTY (in order to generate proprietary PuTTY SSH keys)

### Cloning openstack-testdrive-deploy repository

Clone the openstack-testdrive-deploy repository to the desired location, as a regular user.

```
$ cd ~
$ git clone https://github.com/vagnerfarias/openstack-testdrive-deploy.git
```

### PuTTY

PuTTY is available in main Fedora repository and in [EPEL](https://fedoraproject.org/wiki/EPEL) for RHEL.

## Configuration

All the files mentioned below are relative to the directory where openstack-testdrive-deploy was cloned. For example, ~/openstack-testdrive-deploy.

### Ravello credentials

Edit group\_vars/all/credentials and include your Ravello domain/username and password.

~~~
ravello_login_username: 0123456/your@email.com
ravello_login_password: YourPassword
~~~

### General configuration

Edit _group\_vars/all/main.yaml_ and set:

Variable Name | Example | Explanation
--------------|---------|------------
country | BR, MX, SAC, etc | Region where you are allowed to create resources on Ravello.
customer\_name | MyCustomer, OpenStack-Day, etc | Name of customer or some event identifier.
ravello\_keypair\_name | LATAM-BR-mykey | The name of your own keypair in Ravello. All applications will be created with this keypair, so that you can access the environment.

The remaining variables shouldn't be modified, unless you understand what they do.

### Number of labs and expiration time

Edit roles/ravello.applications\_create/defaults/main.yaml and modify *ravello\_app\_list* variable, uncommenting as many lines as applications in Ravello you need. Each attendee should have its own lab.

~~~
ravello_app_list:
- [ app_name: "{{ bucket_type }}-{{ ravello_app_name }}-{{ customer_name }}-Instructor" ]
- [ app_name: "{{ bucket_type }}-{{ ravello_app_name }}-{{ customer_name }}-W1" ]
#- [ app_name: "{{ bucket_type }}-{{ ravello_app_name }}-{{ customer_name }}-W2" ]
~~~

If required, change the expiration time through the variable *ravelo\_expiration\_time\_min*. Default is 9 hours (540 minutes).

~~~
ravello_expiration_time_min: 540
~~~

Remaining variables in this file usually shouldn't be modified.

### Labs deployment

In order to deploy the labs, run the create-ravello-apps playbook, as follows:

~~~
$ ansible-playbook create-ravello-apps.yaml
~~~

### Labs post-configuration

After the labs are deployed and all VMs are up, it's required to run an additional playbook which will:

* configure the shared ssh key in every environment, so that attendees have access to the labs
* configure OpenStack nova NoVNC proxy to the proper value, so that attendees can access the console of the virtual instances they create.

To run the post-configuration playbook, run the following command:

~~~
$ ansible-playbook config-apps.yaml
~~~

## E-mail notification

It's possible to send an e-mail to each attendee with his own lab access information and with the PDF of the attendee's guide. To use this playbook, some additional steps are required.

These steps consider that Google SMTP server will be used.

### Create an application password for Google Mail

1. Enable 2-Step verification in your account, as explained in https://support.google.com/accounts/answer/185839
1. Create an App password accessing https://security.google.com/settings/security/apppasswords (Select app: Other)

### Configure playbook variables

Edit roles/sendmail.applications/defaults/main.yaml and set variables as in the example below:

~~~
 ravello_fqdn_dir: OSP-TestDrive
 sendmail_host: 'smtp.gmail.com'
 sendmail_port: '465'
 sendmail_username: 'your@email.com'
 sendmail_password: 'ProvidedByGmail'
 sendmail_from: 'your@email.com'
~~~

Later on the same file, edit *sendmail_to* variable. Each line represents one attendee, so you should include his/her name and e-mail addres.

~~~
 - { name: Your Name, email: your@email.com, txt_app_file: "{{ bucket_type }}-{{ ravello_fqdn_dir }}-{{ customer_name }}-Instructor.txt" }
 - { name: customer1name, email: customer1@email, txt_app_file: "{{ bucket_type }}-{{ ravello_fqdn_dir }}-{{ customer_name }}-W1.txt" }
# - { name: customer2name, email: customer2@email, txt_app_file: "{{ bucket_type }}-{{ ravello_fqdn_dir }}-{{ customer_name }}-W2.txt" }
~~~

### Download Test Drive attendee guide

Download Red Hat OpenStack Platform Ateendee guide from internal repository and save it in the directory where this README file is. The file should be named *Red_Hat_OpenStack_Platform_Test_Drive_Guide.pdf*.

### E-mail lab information to attendees.

Run the playbook to send lab information to attendees. It may take some time as the attendee guide has about 2 MB.

~~~
$ ansible-playbook sendmail-applications.yaml
~~~

