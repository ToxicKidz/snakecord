from . import structures
from .state import BaseState


class GuildIntegrationApplication(structures.GuildIntegrationApplication):
    __slots__ = (
        '_state', 'bot'
    )

    def __init__(self, *, state: 'GuildIntegrationState'):
        self._state = state
        self.bot = None

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)

        if self._bot is not None:
            self.bot = self._state.client.users.add(self._bot)


class GuildIntegration(structures.GuildIntegration):
    __slots__ = (
        '_state', 'guild', 'user', 'application'
    )

    def __init__(self, *, state: 'GuildIntegrationState', guild: 'Guild'):
        self._state = state
        self.guild = guild

    async def edit(self, **kwargs):
        rest = self._state.client.rest
        await rest.modify_guild_integration(self.guild.id, self.id, **kwargs)

    async def delete(self):
        rest = self._state.client.rest
        await rest.delete_guild_integration(self.guild.id, self.id)

    async def sync(self):
        rest = self._state.client.rest
        await rest.delete_guild_integration(self.guild.id, self.id)

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)

        if self._user is not None:
            self.user = self._state.client.users.append(self._user)

        if self._application is not None:
            self.application = GuildIntegrationApplication.unmarshal(
                self._application, state=self._state)


class GuildIntegrationState(BaseState):
    def __init__(self, *, client: 'Client', guild: 'Guild'):
        super().__init__(client=client)
        self.guild = guild

    def append(self, data: dict):
        integration = self.get(data['id'])
        if integration is not None:
            integration._update(data)
            return integration

        integration = GuildIntegration.unmarshal(data, state=self, guild=self.guild)
        self._items[integration.id] = integration
        return integration

    async def fetch_all(self):
        rest = self.client.rest
        data = await rest.get_guild_integrations(self.guild.id)
        integrations = [self.append(integration) for integration in data]
        return integrations

    async def create(self, integration_id: int, integration_type: str):
        rest = self.client.rest
        await rest.create_guild_integration(integration_type, integration_id)
