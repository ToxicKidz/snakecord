from .baseobject import BaseObject, BaseTemplate
from .embedobject import Embed
from ..utils import JsonArray, JsonField, JsonTemplate, Snowflake

__all__ = ('Message',)


MessageTemplate = JsonTemplate(
    channel_id=JsonField('channel_id', Snowflake, str),
    guild_id=JsonField('guild_id', Snowflake, str),
    content=JsonField('content'),
    edited_timestamp=JsonField('edited_timestamp'),
    tts=JsonField('tts'),
    mention_everyone=JsonField('mention_everyone'),
    _mentions=JsonArray('mentions'),
    _mention_roles=JsonArray('mention_roles'),
    _mention_channels=JsonArray('mention_channels'),
    _attachments=JsonArray('attachments'),
    embeds=JsonArray('embeds', object=Embed),
    _reactions=JsonArray('reactions'),
    nonce=JsonField('nonce'),
    pinned=JsonField('pinned'),
    webhook_id=JsonField('webhook_id'),
    type=JsonField('type'),
    _activity=JsonField('activity'),
    application=JsonField('application'),
    _message_reference=JsonField('message_reference'),
    flags=JsonField('flags'),
    _stickers=JsonArray('stickers'),
    _referenced_message=JsonField('referenced_message'),
    _interaction=JsonField('interaction'),
    __extends__=(BaseTemplate,)
)


class Message(BaseObject, template=MessageTemplate):
    __slots__ = ('author', 'member')

    def __json_init__(self, *, state):
        super().__json_init__(state=state)
        self.author = None
        self.member = None

    @property
    def channel(self):
        return self.state.manager.channels.get(self.channel_id)

    @property
    def guild(self):
        return self.state.manager.guilds.get(self.guild_id)

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        author = data.get('author')
        if author is not None:
            self.author = self.state.manager.users.append(author)

            guild = self.guild

            member = data.get('member')
            if member is not None and guild is not None:
                member['user'] = author
                self.member = guild.members.append(member)
