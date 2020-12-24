class EventHandler:
    def __init__(self, client):
        handlers = (
            self.invite_create,
            self.message_create,
            self.guild_create
        )
        self.handlers = {handler.__name__.lower(): handler for handler in handlers}
        self.listeners = {handler.__name__.lower(): [] for handler in handlers}
        self._client = client

    def dispatch(self, payload):
        name = payload.event_name.lower()
        handler = self.handlers.get(name)
        if handler is not None:
            handler(payload)

    def add_listener(self, func):
        name = func.__name__.lower()
        listeners = self.listeners.get(name)
        if listeners is None:
            raise Exception
        listeners.append(func)

    def _call_listeners(self, name, *args):
        for listener in self.listeners[name]:
            self._client.loop.create_task(listener(*args))

    def invite_create(self, payload):
        data = payload.data
        print(data)
        invite = self._client.invites._add(data)
        self._call_listeners('invite_create', invite)

    def message_create(self, payload):
        data = payload.data
        channel = self._client.channels.get(data.get('channel_id'))
        if channel is None:
            return
        message = channel.messages._add(data)
        self._call_listeners('message_create', message)

    def guild_create(self, payload):
        guild = self._client.guilds._add(payload.data)
        self._call_listeners('guild_create', guild)
