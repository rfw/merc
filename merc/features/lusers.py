from merc import message


class LUserClient(message.Reply):
  NAME = "251"
  FORCE_TRAILING = True

  def as_reply_params(self, client):
    num_invisible = sum(
        client.is_invisible for client in client.server.clients.values())

    return ["There are {} users and {} invisible on {} servers".format(
        len(client.server.clients) - num_invisible,
        num_invisible,
        1)]


class LUserOp(message.Reply):
  NAME = "252"
  FORCE_TRAILING = True

  def as_reply_params(self, client):
    return ["0", "IRC operators online"]

class LUserUnknown(message.Reply):
  NAME = "253"
  FORCE_TRAILING = True

  def as_reply_params(self, client):
    return ["0", "unknown connections"]


class LUserChannels(message.Reply):
  NAME = "254"
  FORCE_TRAILING = True

  def as_reply_params(self, client):
    return [str(len(client.server.channels)), "channels formed"]


class LUserMe(message.Reply):
  NAME = "255"
  FORCE_TRAILING = True

  def as_reply_params(self, client):
    return ["I have {} clients and {} servers".format(
        len(client.server.clients),
        1)]


@message.Command.register
class LUsers(message.Command):
  NAME = "LUSERS"
  MIN_ARITY = 0

  @message.Command.requires_registration
  def handle_for(self, client, prefix):
    client.send_reply(LUserClient())
    client.send_reply(LUserOp())
    client.send_reply(LUserUnknown())
    client.send_reply(LUserChannels())
    client.send_reply(LUserMe())
