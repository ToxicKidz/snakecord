from .basestate import BaseState
from .. import rest
from ..objects.reactionsobject import Reactions

__all__ = ('ReactionsState',)


class ReactionsState(BaseState):
    __reactions_class__ = Reactions

    def __init__(self, *, manager, message):
        super().__init__(manager=manager)
        self.message = message

    def upsert(self, data):
        ident = self.message.guild.emojis.upsert(data['emoji']).id
        reactions = self.get(ident)
        if reactions is not None:
            reactions.update(data)
        else:
            reactions = self.__reactions_class__.unmarshal(data, state=self)
            reactions.cache()

        return reactions

    async def add(self, emoji):
        await rest.create_reaction.request(
            session=self.manager.rest,
            fmt=dict(channel_id=self.message.channel_id,
                     message_id=self.message.id,
                     emoji=emoji.to_reaction()))

    async def remove_all(self):
        await rest.delete_all_reactions.request(
            session=self.manager.rest,
            fmt=dict(channel_id=self.message.channel_id,
                     message_id=self.message.id))
