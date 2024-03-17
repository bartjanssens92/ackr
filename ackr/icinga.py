import json
import time
import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
from ackr.config import Config

def get_hosts(backend):
  """
  Get all the hosts that aren't in state 0
  """
  acked = []
  downtime = []
  down = []
  unknown = []
  other = []

  url = ''.join([backend['backend_url'], '/v1/objects/hosts?filter=host.state!=0'])

  r = requests.get(url, auth=(backend['username'], backend['password']), verify=False)
  for host in r.json()['results']:
    if host['attrs']['acknowledgement'] == 1:
      acked.append(host)
    elif host['attrs']['downtime_depth'] > 0 or not host['attrs']['last_check_result']['active']:
      downtime.append(host)
    elif host['attrs']['state'] == 1 and host['attrs']['last_check_result']['active']:
      down.append(host)
    elif host['attrs']['state'] == 2 and host['attrs']['last_check_result']['active']:
      unknown.append(host)
    else:
      other.append(host)

  for host in other:
    #print(host)
    print(host['attrs']['state'])
    print(host['attrs']['last_check_result'])
    print(host['attrs']['acknowledgement'])
    print('--------------------')

  h_down = []
  h_unknown = []

  for host in down:
    h_down.append({
      'name': host['attrs']['name'],
      'host_name': host['attrs']['name'],
      'display_name': 'Host alive',
      'last_state_change': host['attrs']['last_state_change'],
      'output': host['attrs']['last_check_result']['output'],
      'notification': host['attrs']['vars']['notification']
    })

  for host in unknown:
    h_unknown.append({
      'name': host['attrs']['name'],
      'host_name': host['attrs']['address'],
      'display_name': host['attrs']['display_name'],
      'last_state_change': host['attrs']['last_state_change'],
      'output': host['attrs']['last_check_result']['output'],
      'notification': host['attrs']['vars']['notification']
    })

  h_down.sort(key=get_host_name)
  h_unknown.sort(key=get_host_name)

  return {'down': h_down, 'unknown': h_unknown}


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
  
    try:
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
    except Exception as e:
       print(service)
       print('====================')
  
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

  data = {
    'author': str(author),
    'comment': 'Acked by ackr',
    'notify': False,
    'pretty': True,
    'timestamp': int(time.time()) + 3600
  }

  ack_filter = {}
  # If host_name and service_name are equal the type is Host
  # as the button is generated that way.
  if host_name == service_name:
    ack_filter = {  
      'type': 'Host',
      'filter': 'match(h_pattern,host.name)',
      'filter_vars': {
        'h_pattern': str(host_name),
      }
    }

  else:
    ack_filter = {  
      'type': 'Service',
      'filter': 'match(s_pattern,service.name) && match(h_pattern,service.host_name)',
      'filter_vars': {
        's_pattern': str(service_name),
        'h_pattern': str(host_name),
      }
    }

  data = { **data, **ack_filter }
  url = ''.join([backend['backend_url'], '/v1/actions/acknowledge-problem'])

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


def get_time_periods(backend):
  """
  Function to get the defined timeperiods
  """

  headers = {
    'Accept':'application/json'
  }

  auth = (
    backend['username'],
    backend['password']
  )

  url = ''.join([backend['backend_url'], '/v1/objects/timeperiods'])

  r = requests.get(url, headers=headers, auth=auth, verify=False)
  print('Response: ')
  print(r.json())

  timeperiods = {}

  for timeperiod in r.json()['results'][0]['attrs']:
    print(timeperiod['__name'])

  return 'Create object that has the data needed to filter if a service should be shown or not'
