import functools

from merc import emitter


class MessageTooLongError(Exception):
  pass


class Message(object):
  MAX_LENGTH = 510
  FORCE_TRAILING = False

  def as_params(self, server, user):
    raise NotImplementedError

  def emit(self, user, prefix):
    emitted = emitter.emit_message(prefix, self.NAME, self.as_params(user),
                                   force_trailing=self.FORCE_TRAILING)

    if len(emitted) > self.MAX_LENGTH:
      raise MessageTooLongError

    return emitted


class Reply(Message):
  def as_params(self, server, user):
    return [user.displayed_nickname] + self.as_reply_params(server, user)

  def as_reply_params(self, server, user):
    return []


class Command(Message):
  def __init__(self, *args):
    pass

  @classmethod
  def with_params(cls, params):
    from merc import errors

    if len(params) < cls.MIN_ARITY:
      raise errors.NeedMoreParams(cls.NAME)

    return cls(*params)

  def handle_for(self, server, user, prefix):
    raise NotImplementedError

  @staticmethod
  def requires_registration(f):
    @functools.wraps(f)
    def _wrapper(self, server, user, prefix):
      from merc import errors

      if not user.is_registered:
        raise errors.NotRegistered

      f(self, server, user, prefix)
    return _wrapper

