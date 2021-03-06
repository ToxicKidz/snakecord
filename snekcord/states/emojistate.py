from .basestate import BaseState
from .. import rest
from ..objects.emojiobject import BUILTIN_EMOJIS, GuildEmoji
from ..utils import Snowflake

__all__ = ('GuildEmojiState',)


class GuildEmojiState(BaseState):
    __key_transformer__ = Snowflake.try_snowflake
    __guild_emoji_class__ = GuildEmoji

    def __init__(self, *, manager, guild):
        super().__init__(manager=manager)
        self.guild = guild

    def upsert(self, data):
        emoji_id = data['id']
        if emoji_id is not None:
            emoji = self.get(emoji_id)
            if emoji is not None:
                emoji.update(data)
            else:
                emoji = self.__guild_emoji_class__.unmarshal(
                    data, state=self, guild=self.guild)
                emoji.cache()
        else:
            surrogates = data['name'].encode()
            emoji = BUILTIN_EMOJIS.get(surrogates)

        return emoji

    async def fetch(self, emoji):
        emoji_id = Snowflake.try_snowflake(emoji)

        data = await rest.get_guild_emoji.request(
            session=self.manager.rest,
            fmt=dict(guild_id=self.guild.id, emoji_id=emoji_id))

        return self.upsert(data)

    async def fetch_all(self):
        data = await rest.get_guild_emojis.request(
            session=self.manager.rest,
            fmt=dict(guild_id=self.guild.id))

        return self.upsert_many(data)
