<p align="center">
  <h3 align="center">Get2Unix</h3>

  <p align="center">
    This is a "little" tool for daily simplify some daily operations for Unix servers.
    <br />
    <br />
    <a href="https://github.com/death-finger/get2unix/issues">Report Bug</a>
    ·
    <a href="https://github.com/death-finger/get2unix/issues">Request Feature</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

For managing around 1000 Unix boxes in ebay, I always have similar tasks on different boxes.
Especially for things like taking snapshots and remove them after some days or granting temporary sudo accesses for 
certain period. We usually forget to remove the old snapshots (it will waste lots of datastore space and if you remove 
lots of snapshots in bulk it will cost quite a lot disk I/O) or revoke the sudo access (security risk).
<br />
So here comes the Get2Unix, currently it can:
1. Scan the vCenters and grab the VM inventory
2. Take snapshots for VMs (using terraform, for now only 1 snapshot supported per VM)
3. VM Deploy (call pyvmoni, using customize policy and template)
4. Temp sudo management (calling AWX job)
5. Sudo scan (calling AWX job)
6. Vuls scan (with vulsctl)

<!-- Usage -->
## Usage

#### Running celery
On windows:
```shell script
celery -A get2unix worker -l info -P eventlet
python manage.py shell
from flush_win import *
runme()
```
On Mac / Linux:
```shell script
celery -A get2unix worker -l info &
celery -A get2unix beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &
```

#### Create Database
```mysql
 create database get2unix DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
```

#### Crypto
```shell script
Joshuas-MacBook-Pro:site-packages joshuapu$ pwd
/Users/joshuapu/Development/PycharmProjects/get2unix/venv/lib/python3.7/site-packages
Joshuas-MacBook-Pro:site-packages joshuapu$ mv crypto Crypto
```

#### mysqlclient
```shell script
apt-get install python3-dev default-libmysqlclient-dev
yum install python3-devel mysql-devel 
```

#### django-auth-ldap
```shell script
sudo apt install libsasl2-dev python-dev libldap2-dev libssl-dev
yum install python3-devel openldap-devel
```



### Built With

* [Django](https://www.djangoproject.com/)
* [Bootstrap](https://getbootstrap.com)
* [JQuery](https://jquery.com)
* [VUE](https://vuejs.org/)
* [celery](https://docs.celeryproject.org/en/stable/)
* [pyvmoni](https://github.com/vmware/pyvmomi)


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<!-- CONTACT -->
## Contact

Joshua Pu - death_finger@sina.com

Project Link: [https://github.com/death-finger/get2unix](https://github.com/death-finger/get2unix)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
As listed above, this is only a personal project, for resolving some boring tasks in my work, and if you tried to use it 
in your environment, **I DEFINITELY WILL NOT TAKE ANY RESPONSIBILITY FOR ANY RESULTS CAUSED BY IT**. So think twice if 
you bring it into use.
