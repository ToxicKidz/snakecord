from .basestate import (BaseState, BaseSubState, SnowflakeMapping,
                        WeakValueSnowflakeMapping)
from .. import rest
from ..objects.roleobject import Role
from ..utils import Snowflake, _validate_keys


class RoleState(BaseState):
    __container__ = SnowflakeMapping
    __recycled_container__ = WeakValueSnowflakeMapping
    __guild_class__ = Role

    def __init__(self, *, manager, guild):
        super().__init__(manager=manager)
        self.guild = guild

    async def fetch_all(self):
        data = await rest.get_guild_roles.request(
            session=self.manager.rest,
            fmt=dict(guild_id=self.guild.id))

        return self.extend(data)

    async def create(self, **kwargs):
        keys = rest.create_guild_role.json

        _validate_keys(f'{self.__class__.__name__}.create',
                       kwargs, (), keys)

        data = await rest.create_guild_role.request(
            session=self.manager.rest,
            fmt=dict(guild_id=self.guild.id),
            json=kwargs)

        return self.append(data)

    async def modify(self, positions):
        required_keys = ('id',)

        keys = rest.modify_guild_role_positions.json

        json = []

        for key, value in positions.items():
            value['id'] = Snowflake.try_snowflake(key)

            _validate_keys(f'positions[{key}]',
                           value, required_keys, keys)

            json.append(value)

        await rest.modify_guild_role_positions.request(
            session=self.manager.rest,
            fmt=dict(guild_id=self.guild.id),
            json=json)


class GuildMemberRoleState(BaseSubState):
    def __init__(self, *, superstate, member):
        super().__init__(superstate=superstate)
        self.member = member

    async def add(self, role):
        role_id = Snowflake.try_snowflake(role)

        await rest.add_guild_member_role.request(
            session=self.superstate.manager.rest,
            fmt=dict(guild_id=self.member.guild.id,
                     user_id=self.member.user.id,
                     role_id=role_id))

    async def remove(self, role):
        role_id = Snowflake.try_snowflake(role)

        await rest.remove_guild_member_role.request(
            session=self.superstate.manager.rest,
            fmt=dict(guild_id=self.member.guild.id,
                     user_id=self.member.user.id,
                     role_id=role_id))