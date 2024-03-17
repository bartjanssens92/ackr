import json
import time
import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
from ackr.config import Config
from datetime import datetime, timedelta

def get_host_name(e):
  """
  Lamda function to make sorting on key possible.
  """
  return e['host_name']


def parse_alert(alert):
  """
  Sub function to get the host_name and alert_type from the passed
  alert.
  """
  alert_type = 'pod'
  if 'pod' in alert['labels']:
    host_name = alert['labels']['pod']
  elif 'instance' in alert['labels']:
    alert_type = 'instance'
    host_name = alert['labels']['instance']
  else:
    alert_type = 'kube'
    host_name = 'Kube internals'

  return alert_type, host_name


def get_alerts(backend):
  """
  Get all the alerts
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

  for alert in r.json()['data']:
    if alert['status']['state'] == 'suppressed':
       silenced.append(alert)
    elif alert['labels']['severity'] == 'info':
      info.append(alert)
    elif alert['labels']['severity'] == 'warning':
      warning.append(alert)
    elif alert['labels']['severity'] == 'critical':
      critical.append(alert)
    elif alert['labels']['severity'] == 'none':
      none.append(alert)
    else:
      others.append(alert)
  
  for alert in others:
    # Debug any alerts that are not filtered correctly.
    print(alert)
    print('--------------------')
  
  s_critical = []
  s_warning = []
  s_info = []
  # Only get the 'usefull' keys as otherwise the data returns it way to detailed for what is actually used.
  for alert in critical:

    try:
      notification = alert['receivers']
    except KeyError:
      notification = {'enable': False}

    alert_type, host_name = parse_alert(alert)
    s_critical.append({
      'name': alert['fingerprint'],
      'labels': alert['labels'],
      'host_name': host_name,
      'display_name': alert['labels']['alertname'],
      'output': alert['annotations']['description'],
      'notification': notification
    })

  for alert in warning:

    try:
      notification = alert['receivers']
    except KeyError:
      notification = {'enable': False}

    alert_type, host_name = parse_alert(alert)
    s_warning.append({
      'name': alert['fingerprint'],
      'labels': alert['labels'],
      'host_name': host_name,
      'display_name': alert['labels']['alertname'],
      'output': alert['annotations']['description'],
      'notification': notification
    })

  for alert in info:

    try:
      notification = alert['receivers']
    except KeyError:
      notification = {'enable': False}

    alert_type, host_name = parse_alert(alert)
    s_info.append({
      'name': alert['fingerprint'],
      'labels': alert['labels'],
      'host_name': host_name,
      'display_name': alert['labels']['alertname'],
      'output': alert['annotations']['description'],
      'notification': notification
    })

  s_critical.sort(key=get_host_name)
  s_warning.sort(key=get_host_name)
  s_info.sort(key=get_host_name)

  return {'critical': s_critical, 'warning': s_warning, 'info': s_info}


def silence_alert(backend, host_name, alert_fingerprint, author):
  """
  Function to silence a alert defined by host_name and alert_name,
  this does a post request with a filter to the icinga frontend api.
  curl https://cluster.internal.org/path/alertmanager/api/v2/silences -H "Content-Type: application/json" -d '{
    "matchers": [
      {
        "name": "env",
        "value": "pakalu",
        "isRegex": false
      }
    ],
    "startsAt": "2023-10-25T22:12:33.533330795Z",
    "endsAt": "2023-10-25T23:11:44.603Z",
    "createdBy": "api",
    "comment": "Silence",
    "status": {
      "state": "active"
    }
  }'
  """
  headers = {
    'Content-Type':'application/json'
  }

  # Get all the labels to only silence the alert that matches the fingerprint
  matchers = []
  alerts = get_alerts(backend)
  for severity in alerts:
    for alert in alerts[severity]:
      if alert['name'] == alert_fingerprint:
        for label in alert['labels']:
          matchers.append({
            'name': str(label),
            'value': str(alert['labels'][label]),
            'isRegex': False,
          })

  startsAt = datetime.today()
  endsAt = startsAt + timedelta(hours=2)
  data = {
    'matchers': matchers,
    'startsAt': startsAt.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
    'endsAt': endsAt.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
    'createdBy': str(author),
    'comment': 'Acked by ackr',
  }

  if 'username' in backend:
    auth = (
      backend['username'],
      backend['password']
    )
    url = ''.join([backend['backend_url'], '/api/v2/silences'])
    r = requests.post(url, headers=headers, auth=auth, data=json.dumps(data), verify=False)
  else:
    url = ''.join([backend['backend_url'], '/api/v2/silences'])
    r = requests.post(url, headers=headers, data=json.dumps(data), verify=False)

  print('Response: ')
  print(r.json())
