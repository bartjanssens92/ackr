from ackr.config import Config
from ldap3 import Server, Connection, SAFE_SYNC
from ldap3.core import exceptions

def get_bind_dn(username):
  dn = Config.ldap_dn
  return ''.join(['uid=', username, ',cn=users,cn=accounts,', dn])


def get_group_dn(groupname):
  dn = Config.ldap_dn
  return ''.join(['cn=', groupname, ',cn=groups,cn=accounts,', dn])


def get_uid(conn, username):

  conn.search(get_bind_dn(username), '(uid=' + str(username) + ')', attributes=['uidNumber'])
  return conn.entries[0].uidNumber.value


def in_group(conn, username, included_group):

  conn.search(get_bind_dn(username), '(uid=' + str(username) + ')', attributes=['memberOf'])

  if get_group_dn(included_group) in conn.response[0]['attributes']['memberOf']:
    return True
  return False


def login(username, password):

  for ldap_server in Config.ldap_servers:
    print(ldap_server)
    server = Server(ldap_server)
    try:
      conn = Connection(server, user=get_bind_dn(username), password=password, auto_bind=True)
    except exceptions.LDAPBindError as e:
      if 'invalidCredentials' in str(e):
        print(str(e))
        continue
      else:
        print('smth else')
        print(str(e))
        continue
    except Exception as e:
      print('generic else')
      print(str(e))
      continue

    return conn

