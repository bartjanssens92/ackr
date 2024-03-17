![ackr, logo](ackr/static/images/logo.png)
# ACKR

Little flask frontend to create a small dashboard to just list the services that have issues from icinga2.

Allows acknowleding services by clicking on the fqdn.

## Running the app

Create a param file with content:
```bash
export SECRET_KEY=changeme!
export LDAP_DN=dc=somewhere,dc=example,dc=com
export LDAP_SERVERS=ldap01.somewhere.example.com,ldap02.somewhere.example.com

export LDAP_GROUP=icinga
export ICINGA_USERNAME=icingaapi
export ICINGA_PASSWORD=somethingsomethingsomethingsecret
export ICINGA_BACKEND_URL=https://icinga.somewhere.example.com:5665
export ICINGA_GROUP=icinga
```

OR
bash```
export SECRET_KEY=changeme!
export LDAP_DN=dc=somewhere,dc=example,dc=com
export LDAP_SERVERS=ldap01.somewhere.example.com,ldap02.somewhere.example.com

cat config.json
{
    "icinga2": [
        {
            "id": "icinga_instance_01",
            "display_name": "Icinga",
            "username": "icingaapi",
            "password": "somethingsomethingsomethingsecret",
            "backend_url": "https://icinga.somewhere.example.com:5665",
            "group": "icinga"
        },
        {
            "id": "icinga_instance_02",
            "display_name": "Icinga other deployment",
            "username": "icingaapi2",
            "password": "somethingsomethingsomethingmoresecret",
            "backend_url": "https://icinga.somewhere.else.example.com:5665",
            "group": "icinga"
        }
    ],
   "alertmanager": [
        {
            "display_name": "Cluster 01",
            "backend_url": "https://alertmanager.somewhere.example.com"
        },
        {
            "display_name": "Cluster 02",
            "backend_url": "https://alertmanager.somewhere.else.example.com"
        },
    ],
}
export BACKENDS=$(cat config.json)
```

Then run the app in gunicorn:
```bash
source params.sh
gunicorn -w 1 -t 600 -b 0.0.0.0:5000 --log-level DEBUG ackr:app
```

## Logo

Vectors and icons by [SVG Repo](https://www.svgrepo.com), link to the [specific logo](https://www.svgrepo.com/svg/72029/field)

## ToDo

- Improve logging.
- Add scheduling downtime option.

## Done

- Add toggle to show only services the user gets notification for.
- Fix bug where users are shown a "internal server error" if they have logged in on a different device.
- Add multi-backend support.
- Add support for hosts.
- Add alertmanager support.
