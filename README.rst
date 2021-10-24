Chatbot commerce
================

Behold My Awesome Project!

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/ambv/black
     :alt: Black code style

:License: MIT

Settings
--------

Moved to settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html

Avanced Commands
----------------

**Open your machine ssh for all Avanced Commands**

Create An Api key
^^^^^^^^^^^^^^^^^

* To create a **new api key**, Go to admin site Sign Up and select Store APIKey's that gonna be en section **STORES** click on **ADD STORE APIKEY** where say Name put the store name that belongs this new api key and provides a e-mail to send verification. then confirm your api key in your email address to active it.

* To create an **old api key**, put these commands::

    :~# sudo docker-compose -f file.yml run --rm django python manage.py shell

* Usually in this project::

    :~# sudo docker-compose -f chatbot_commerce/production.yml run --rm django python manage.py shell

* In Django shell::

    from chatbot_commerce.stores.models import StoreAPIKey

    StoreAPIKey.objects.create_my_key(name="store_name", key="old_api_key", email="my_email_address", verify=True, is_active=True)

Create Backups
^^^^^^^^^^^^^^

* To creata a **backup**, put these commands::

    :~# docker-compose -f file.yml exec service-name backup
    :~# docker cp container-name:/path/to/container/backups /path/machine/folder
    :~# docker exec --detach container-name rm /path/to/container/backups/*

* **Usually in this project**::

    :~# docker-compose -f chatbot_commerce/production.yml exec postgres backup
    :~# docker cp chatbot_commerce_postgres_1:/backups ./
    :~# docker exec --detach chatbot_commerce_postgres_1 rm ./backups/*

*Or

    In this project you can do this::

    :~# nano ./backup.sh

    then put this::

        #! /bin/bash

        # Give permissions with $ sudo chmod +x filename

        # docker exec -t chatbot_commerce_postgres_1 pg_dump -U XIjBSJxMRRouVNXkIGbTiuijaGxlTssa -W Fr5VufGKRQxZRppXQxg1vS22jQsEKftZTo27KmDMsfaazL0kZ5i6dHeWc>
        # whoami
        docker-compose -f chatbot_commerce/production.yml exec postgres backup
        docker cp chatbot_commerce_postgres_1:/backups ./
        docker exec --detach chatbot_commerce_postgres_1 rm ./backups/*

        cd ./backups && echo *

    execute::

    :~# ./backup.sh

Restore Backups
^^^^^^^^^^^^^^^

* To restore a **backup**, put these commands::

    :~# docker cp path/to/machine/backups/file.sql.gz container-name:/path/to/container/backups/
    :~# docker-compose -f ./chatbot_commerce/production.yml down --remove-orphans
    :~# docker-compose -f ./chatbot_commerce/production.yml up -d
    :~# docker-compose -f ./chatbot_commerce/production.yml exec -u root postgres restore file.sql.gz

* Example in this project when date creation backup is 2021_10_22T22_24_24::

    :~# docker cp ./backups/backup_2021_10_22T22_24_24.sql.gz chatbot_commerce_postgres_1:/backups/
    :~# docker-compose -f ./chatbot_commerce/production.yml down --remove-orphans
    :~# docker-compose -f ./chatbot_commerce/production.yml up -d
    :~# docker-compose -f ./chatbot_commerce/production.yml exec -u root postgres restore backup_2021_10_22T22_24_24.sql.gz

*Or

    In this project you can do this::

    :~# nano ./restoredb.sh

    then put this::

        #! /bin/bash

        # Give permissions with $ sudo chmod +x filename

        echo 'container:' $1, 'file:' $2

        docker cp ./backups/$2 $1:/backups/
        docker-compose -f ./chatbot_commerce/production.yml down --remove-orphans
        docker-compose -f ./chatbot_commerce/production.yml up -d
        docker-compose -f ./chatbot_commerce/production.yml exec -u root postgres restore $2
        docker exec --detach chatbot_commerce_postgres_1 rm ./backups/*

    execute::

    :~# ./restoredb.sh container_name file.sql.gz

Clear Ram And Cache
^^^^^^^^^^^^^^^^^^^

requirements
~~~~~~~~~~~~

* Links to documentation for two first step, click here_ or this one_ too works.

    .. _here: https://www.ndchost.com/wiki/guides/how-to-create-swap-file-in-linux

    .. _one: https://linuxize.com/post/create-a-linux-swap-file/

* **Warning**

    - A swap file should be the same size as your available physical memory. Having a very large swap file is not a good idea and if you are experiencing frequent crashing, you should expand your physical memory.
    - Change the count value to the size that you need. You can use the formula (<count>/1024) to determine how many megabytes you will be setting aside for swap. In this example, we are crafting 1GB swap count is in **Kilobyte**.

* First create a swap file::

    :~# dd if=/dev/zero of=/swapfile bs=1024 count=1048576
    :~# chmod 600 /swapfile
    :~# mkswap /swapfile
    :~# swapon /swapfile

* Then go to /etc/fstab and add this line on boot::

    /swapfile swap swap defaults 0 0

* To clear cache and ram you need execute this command::

    :~# echo 3 > /proc/sys/vm/drop_caches && swapoff -a && swapon -a

* link to documentation_ for last step

    .. _documentation: https://www.tecmint.com/clear-ram-memory-cache-buffer-and-swap-space-on-linux/

*Or

    In this project you can do this::

    :~# nano ./clearcache.sh

    then put this::

        #! /bin/bash

        # Give permissions with $ sudo chmod +x filename

        # Note, we are using "echo 3", but it is not recommended in production instead use "echo 1"
        echo 3 > /proc/sys/vm/drop_caches && swapoff -a && swapon -a && printf '\n%s\n' 'Ram-cache and Swap Cleared'

    execute::

    :~# ./clearcache.sh

Cron
^^^^

First you need to set up your TZ do this
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* link_ to documentation of three first step

.. _link: https://askubuntu.com/questions/54364/how-do-you-set-the-timezone-for-crontab

*  Command to select your time zone::

    :~# dpkg-reconfigure tzdata

* Follow instructions and then::

    :~# service cron restart

* Verify your date settings::

    :~# timedatectl

* Then just add_ jobs to cron .. _add: https://www.cyberciti.biz/faq/how-do-i-add-jobs-to-cron-under-linux-or-unix-oses/::

    :~# crontab -e

- Inside of file cron do this::

    # m h  dom mon dow   command
    57 23 * * * ./clearcache.sh
    53 23 * * 4 ./backup.sh

* Check cron logs events through syslog::

.. _logs: https://linuxhint.com/check-cron-logs-linux/

    :~# cat /var/log/syslog | grep cron



Basic Commands
--------------

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

Type checks
^^^^^^^^^^^

Running type checks with mypy:

::

  $ mypy chatbot_commerce

Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ pytest

Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to `Live reloading and SASS compilation`_.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html

Celery
^^^^^^

This app comes with Celery.

To run a celery worker:

.. code-block:: bash

    cd chatbot_commerce
    celery -A config.celery_app worker -l info

Please note: For Celery's import magic to work, it is important *where* the celery commands are run. If you are in the same folder with *manage.py*, you should be right.

Sentry
^^^^^^

Sentry is an error logging aggregator service. You can sign up for a free account at  https://sentry.io/signup/?code=cookiecutter  or download and host it yourself.
The system is setup with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

Deployment
----------

The following details how to deploy this application.

Docker
^^^^^^

See detailed `cookiecutter-django Docker documentation`_.

.. _`cookiecutter-django Docker documentation`: http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html
