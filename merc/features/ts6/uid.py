import datetime

from merc import feature
from merc import message


class UidFeature(feature.Feature):
  NAME = __name__


install = UidFeature.install


@UidFeature.register_server_command
class Uid(message.Command):
  NAME = "UID"
  MIN_ARITY = 9
  FORCE_TRAILING = True

  def __init__(self, nickname, hopcount, ts, umode, username, host, ip, uid,
               realname, *args):
    self.nickname = nickname
    self.hopcount = hopcount
    self.ts = ts
    self.umode = umode
    self.username = username
    self.host = host
    self.ip = ip
    self.uid = uid
    self.realname = realname

  @property
  def sid(self):
    return self.uid[:3]

  def as_command_params(self):
    return [self.nickname, self.hopcount, self.ts, self.umode, self.username,
            self.host, self.ip, self.uid, self.realname]

  def handle_for(self, app, server, prefix):
    origin_server = app.network.get_by_sid(self.sid)

    user = app.users.new_remote_user(
        self.uid, origin_server.name,
        int(self.hopcount) + origin_server.hopcount)

    user.nickname = self.nickname
    user.username = self.username
    user.host = self.host
    user.realname = self.realname
    user.creation_time = datetime.datetime.fromtimestamp(int(self.ts))

    app.users.add(user)
    app.network.link_broadcast(server, prefix, self)


def send_uid(app, server, user):
  host = user.host
  if host[0] == ":":
    host = "0" + host

  server.send(app.network.local.sid,
              Uid(user.nickname, str(user.hopcount),
                  str(int(user.creation_time.timestamp())), "+", user.username,
                  host, "0", user.uid, user.realname))


@UidFeature.hook("network.burst.users")
def burst_uids(app, server):
  for user in app.users.all():
    send_uid(app, server, user)


@UidFeature.hook("user.register")
def send_uids_on_register(app, user):
  for neighbor in app.network.neighbors():
    send_uid(app, neighbor, user)
