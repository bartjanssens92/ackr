# ACKR

Little flask frontend to create a small dashboard to just list the services that have issues from icinga2.

Allows acknowleding services by clicking on the fqdn.

## Example running

Create a param file with content:
```bash
export SECRET_KEY=changeme!
export LDAP_DN=dc=somewhere,dc=example,dc=com
export LDAP_SERVERS=ldap01.somewhere.example.com,ldap02.somewhere.example.com
export LDAP_GROUP=icinga
export ICINGA_USERNAME=icingaapi
export ICINGA_PASSWORD=somethingsomethingsomethingsecret
export ICINGA_BACKEND_URL=https://icinga.somewhere.example.com:5665
export ICINGA_FRONTEND_URL=https://icingaweb2.somewhere.example.com
export ICINGA_GROUP=icinga
```

Then run the app in gunicorn:
```bash
source params.sh
gunicorn -w 1 -t 600 -b 0.0.0.0:5000 --log-level DEBUG ackr:app
```
