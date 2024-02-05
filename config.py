from os import environ

class Config(object):

  secret_key = environ.get('SECRET_KEY', 'changeme!')

  ldap_dn = environ.get('LDAP_DN', 'dc=some,dc=example,dc=com')
  ldap_servers = environ.get('LDAP_SERVERS', ['ldap01.some.example.com', 'ldap02.some.example.com'])
  ldap_group = environ.get('LDAP_GROUP', 'icinga')

  icinga_username = environ.get('ICINGA_USERNAME', 'icingaapi')
  icinga_password = environ.get('ICINGA_PASSWORD', 'somethingsomethingsomethingsecret')
  icinga_backend_url = environ.get('ICINGA_BACKEND_URL', 'https://icinga.some.example.com:5665')
  icinga_frontend_url = environ.get('ICINGA_FRONTEND_URL', 'https://icingaweb2.some.example.com')
  icinga_group = environ.get('ICINGA_GROUP', 'icinga')
