import json
from os import environ

class Config(object):

  secret_key = environ.get('SECRET_KEY', 'changeme!')
  supported_backends = ['icinga2', 'alertmanager']

  ldap_dn = environ.get('LDAP_DN', 'dc=some,dc=example,dc=com')
  ldap_servers = environ.get('LDAP_SERVERS', ['ldap01.some.example.com', 'ldap02.some.example.com']).split(',')

  icinga_username = environ.get('ICINGA_USERNAME', 'icingaapi')
  icinga_password = environ.get('ICINGA_PASSWORD', 'somethingsomethingsomethingsecret')
  icinga_backend_url = environ.get('ICINGA_BACKEND_URL', 'https://icinga.some.example.com:5665')
  icinga_group = environ.get('ICINGA_GROUP', 'icinga')

  monitoring_backends = environ.get('BACKENDS', json.dumps({
    "icinga2": [{
      "name": "Default",
      "username": icinga_username,
      "password": icinga_password,
      "backend_url": icinga_backend_url,
      "group": icinga_group,
    }]
  }) )

  # Do parameter validation here!
  try:
    valid_json = json.loads(monitoring_backends)
  except Exception as e:
    print(e)

  monitoring_backends = json.loads(monitoring_backends)
  valid_config = {}
  for backend_type in monitoring_backends:
    # Remove unsupported backends first
    if backend_type in supported_backends:

      valid_backend = []
      for backend in monitoring_backends[backend_type]:

        valid_backend_config = {}
        # Every backend should have a name specified
        if not 'id' in backend and not 'display_name' in backend:
          raise ValueError('Backend does not have either "display_name" or "id" specified!')
        elif not 'id' in backend:
          # Substitute spaces with underscores to generate the id value.
          valid_backend_config['id'] = '_'.join(backend['display_name'].split(' '))

        if backend_type == 'icinga2':
          if not 'username' in backend:
            raise ValueError('Backend "' + str(backend['display_name']) + " does not have username specified!")
          if not 'password' in backend:
            raise ValueError('Backend "' + str(backend['display_name']) + " does not have password specified!")
          if not 'backend_url' in backend:
            raise ValueError('Backend "' + str(backend['display_name']) + " does not have backend_url specified!")
          if not 'group' in backend:
            valid_backend_config['group'] = 'none'

        if backend_type == 'alertmanager':
          if not 'backend_url' in backend:
            raise ValueError('Backend "' + str(backend['display_name']) + " does not have backend_url specified!")

        valid_backend.append({**backend, **valid_backend_config})

      valid_config[backend_type] = valid_backend

  # Move back to the first name
  monitoring_backends = valid_config
