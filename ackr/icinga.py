import json
import time
import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
from ackr.config import Config

def get_hosts():
  """
  Get all the hosts that aren't in state 0
  """
  acked = []
  downtime = []
  down = []
  unknown = []
  other = []

  url = ''.join([Config.icinga_backend_url, '/v1/objects/hosts?filter=host.state!=0'])

  r = requests.get(url, auth=(Config.icinga_username, Config.icinga_password), verify=False)
  for host in r.json()['results']:
    if host['attrs']['acknowledgement'] == 1:
      acked.append(host)
    elif host['attrs']['downtime_depth'] > 0 or not host['attrs']['last_check_result']['vars_before']['reachable']:
      downtime.append(host)
    elif host['attrs']['state'] == 2 and host['attrs']['last_check_result']['vars_before']['reachable']:
      down.append(host)
    elif host['attrs']['state'] == 3 and host['attrs']['last_check_result']['vars_before']['reachable']:
      unknown.append(host)
    else:
      other.append(host)

  print(len(acked))
  print(len(downtime))
  print(len(down))
  print(len(unknown))
  print(len(other))


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
  acked = []
  downtime = []
  unknown = []
  others = []
  pending = []

  url = ''.join([backend['backend_url'], '/v1/objects/services?filter=service.state!=ServiceOK'])
  
  r = requests.get(url, auth=(backend['username'], backend['password']), verify=False)
  for service in r.json()['results']:
  
    if service['attrs']['acknowledgement'] == 1:
      acked.append(service)
    elif service['attrs']['downtime_depth'] > 0 and not 'vars_before' in service['attrs']['last_check_result']:
      pending.append(service)
    elif service['attrs']['downtime_depth'] > 0 or not service['attrs']['last_check_result']['vars_before']['reachable']:
      downtime.append(service)
    elif service['attrs']['state'] == 1 and service['attrs']['last_check_result']['vars_before']['reachable']:
      warning.append(service)
    elif service['attrs']['state'] == 2 and service['attrs']['last_check_result']['vars_before']['reachable']:
      critical.append(service)
    elif service['attrs']['state'] == 3 and service['attrs']['last_check_result']['vars_before']['reachable']:
      unknown.append(service)
    else:
      others.append(service)
  
  for service in others:
    # Debug any services that are not filtered correctly.
    print(service['attrs']['__name'])
    #print(service['attrs']['host_name'])
    #print(service['attrs']['display_name'])
    #print(service['attrs']['downtime_depth'])
    #print(service['attrs']['acknowledgement'])
    #print(service)
    print('--------------------')
  
  s_critical = []
  s_warning = []
  s_unknown = []
  # Only get the 'usefull' keys as otherwise the data returns it way to detailed for what is actually used.
  for service in critical:

    try:
      notification = service['attrs']['vars']['notification']
    except KeyError:
      notification = {'enable': False}

    s_critical.append({
      'name': service['attrs']['name'],
      'host_name': service['attrs']['host_name'],
      'display_name': service['attrs']['display_name'],
      'last_state_change': service['attrs']['last_state_change'],
      'output': service['attrs']['last_check_result']['output'],
      'notification': notification
    })

  for service in warning:

    try:
      notification = service['attrs']['vars']['notification']
    except KeyError:
      notification = {'enable': False}

    s_warning.append({
      'name': service['attrs']['name'],
      'host_name': service['attrs']['host_name'],
      'display_name': service['attrs']['display_name'],
      'last_state_change': service['attrs']['last_state_change'],
      'output': service['attrs']['last_check_result']['output'],
      'notification': notification
    })

  for service in unknown:

    try:
      notification = service['attrs']['vars']['notification']
    except KeyError:
      notification = {'enable': False}

    s_unknown.append({
      'name': service['attrs']['name'],
      'host_name': service['attrs']['host_name'],
      'display_name': service['attrs']['display_name'],
      'last_state_change': service['attrs']['last_state_change'],
      'output': service['attrs']['last_check_result']['output'],
      'notification': notification
    })

  s_critical.sort(key=get_host_name)
  s_warning.sort(key=get_host_name)
  s_unknown.sort(key=get_host_name)

  return {'critical': s_critical, 'warning': s_warning, 'unknown': s_unknown}


def ack_service(backend, host_name, service_name, author):
  """
  Function to acknowledge a service defined by host_name and service_name,
  this does a post request with a filter to the icinga frontend api.
  """
  headers = {
    'Accept':'application/json'
  }

  auth = (
    backend['username'],
    backend['password'],
  )

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


def down_service(service):
  """
  Function to put a service in downtime defined by host_name and service_name,
  this does a post request with a filter to the icinga frontend api.
  """
  host_name = service['attrs']['host_name']
  service_name = service['attrs']['name']

  headers = {
    'Accept':'application/json'
  }

  auth = (
    Config.icinga_username,
    Config.icinga_password
  )

  url = ''.join([Config.icinga_backend_url, '/v1/actions/schedule-downtime'])
  data = {
    'type': 'Service',
    'filter': 'match(s_pattern,service.name) && match(h_pattern,service.host_name)',
    'filter_vars': {
      's_pattern': str(service_name),
      'h_pattern': str(host_name),
    },
    'author': 'me',
    'comment': 'testing',
    'pretty': True,
    'start_time': int(time.time()),
    'end_time': int(time.time()) + 3600*12
  }

  r = requests.post(url, headers=headers, auth=auth, data=json.dumps(data), verify=False)
  print('Response: ')
  print(r.json())


def get_user_info(username):
  """
  Function to get the user info to determin what services to show.
  """

  headers = {
    'Accept':'application/json'
  }

  auth = (
    Config.icinga_username,
    Config.icinga_password
  )

  url = ''.join([Config.icinga_backend_url, '/v1/objects/users'])
  data = {
    'filter': 'match(s_pattern,user.name)',
    'filter_vars': {
      's_pattern': str(username),
    },
    'pretty': True,
  }

  r = requests.get(url, headers=headers, auth=auth, data=json.dumps(data), verify=False)
  print('Response: ')
  print(r.json())

  return r.json()['results'][0]['attrs']['groups']


def get_time_periods():
  """
  Function to get the defined timeperiods
  """

  headers = {
    'Accept':'application/json'
  }

  auth = (
    Config.icinga_username,
    Config.icinga_password
  )

  url = ''.join([Config.icinga_backend_url, '/v1/objects/timeperiods'])

  r = requests.get(url, headers=headers, auth=auth, data=json.dumps(data), verify=False)
  print('Response: ')
  print(r.json())

  timeperiods = {}

  for timeperiod in r.json()['results'][0]['attrs']:
    print(timeperiod['__name'])

  return 'Create object that has the data needed to filter if a service should be shown or not'
