import json
import time
import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
from ackr.config import Config

def get_host_name(e):
  """
  Lamda function to make sorting on key possible.
  """
  return e['host_name']


def get_services(backend):
  """
  Get all the services that aren't in state ServiceOK.
  """
  warning = []
  critical = []
  silenced = []
  others = []
  info = []
  none = []

  url = ''.join([backend['backend_url'], '/api/v1/alerts'])
  
  if 'username' in backend:
    r = requests.get(url, auth=(backend['username'], backend['password']))
  else:
    r = requests.get(url)

  for service in r.json()['data']:
    if service['labels']['severity'] == 'info':
      info.append(service)
    elif service['labels']['severity'] == 'warning':
      warning.append(service)
    elif service['labels']['severity'] == 'critical':
      critical.append(service)
    elif service['labels']['severity'] == 'none':
      none.append(service)
    else:
      others.append(service)
  
  for service in others:
    # Debug any services that are not filtered correctly.
    print(service)
    print('--------------------')
  
  s_critical = []
  s_warning = []
  s_info = []
  # Only get the 'usefull' keys as otherwise the data returns it way to detailed for what is actually used.
  for service in critical:

    try:
      notification = service['receivers']
    except KeyError:
      notification = {'enable': False}

    if 'pod' in service['labels']:
      host_name = service['labels']['pod']
    elif 'instance' in service['labels']:
      host_name = service['labels']['instance']
    else:
      host_name = 'Kube internals'
    s_critical.append({
      'host_name': host_name,
      'display_name': service['labels']['alertname'],
      'output': service['annotations']['description'],
      'notification': notification
    })

  for service in warning:

    try:
      notification = service['receivers']
    except KeyError:
      notification = {'enable': False}

    if 'pod' in service['labels']:
      host_name = service['labels']['pod']
    elif 'instance' in service['labels']:
      host_name = service['labels']['instance']
    else:
      host_name = 'Kube internals'
    s_warning.append({
      'host_name': host_name,
      'display_name': service['labels']['alertname'],
      'output': service['annotations']['description'],
      'notification': notification
    })

  for service in info:

    try:
      notification = service['receivers']
    except KeyError:
      notification = {'enable': False}

    if 'pod' in service['labels']:
      host_name = service['labels']['pod']
    elif 'instance' in service['labels']:
      host_name = service['labels']['instance']
    else:
      host_name = 'Kube internals'
    s_info.append({
      'host_name': host_name,
      'display_name': service['labels']['alertname'],
      'output': service['annotations']['description'],
      'notification': notification
    })

  s_critical.sort(key=get_host_name)
  s_warning.sort(key=get_host_name)
  s_info.sort(key=get_host_name)

  return {'critical': s_critical, 'warning': s_warning, 'info': s_info}


def silence_alert(backend, host_name, service_name, author):
  """
  Function to silence a service defined by host_name and service_name,
  this does a post request with a filter to the icinga frontend api.
  """
  headers = {
    'Accept':'application/json'
  }

  if 'username' in backend:
    auth = (
      backend['username'],
      backend['password']
    )
    url = ''.join([backend['backend_url'], '/v1/actions/acknowledge-problem'])
  else:
    url = ''.join([backend['backend_url'], '/v1/actions/acknowledge-problem'])

  data = {
    'type': 'Service',
    'filter': 'match(s_pattern,service.name) && match(h_pattern,service.host_name)',
    'filter_vars': {
      's_pattern': str(service_name),
      'h_pattern': str(host_name),
    },
    'author': str(author),
    'comment': 'Acked by ackr',
    'notify': False,
    'pretty': True,
    'timestamp': int(time.time()) + 3600
  }

  r = requests.post(url, headers=headers, auth=auth, data=json.dumps(data), verify=False)
  print('Response: ')
  print(r.json())
