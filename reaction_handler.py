import fileutil
from discord.utils import get


class ReactionHandler:
    def __init__(self, client):
        self.client = client
        self.vote_notified_msgs = {}
        self.POLL_ACTIVATION_COUNT = 5
        self.VOTES_FILE_PATH = 'db/votes.txt'
        self.vote_notified_msgs = fileutil.read_from_file(self.VOTES_FILE_PATH)

    async def on_raw_reaction_add(self, payload):
        reaction, message, channel = await self._get_datas(payload)
        if message.author != self.client.user:
            return

        if reaction.count < self.POLL_ACTIVATION_COUNT + 1:
            return

        poll_result = f"**{reaction.count-1}** Members are voted! : {reaction.emoji}"
        if reaction.count == self.POLL_ACTIVATION_COUNT + 1:
            poll_result += "\nLet's go get a scrim."
        elif reaction.count == self.POLL_ACTIVATION_COUNT + 4:
            poll_result = f"\nMaybe we can start a civil war."
        poll_result += f"\nMembers who reacted: {await self._get_reacted_user_mentions(reaction)}"

        key = str(payload.message_id) + str(payload.emoji.id)
        if key not in self.vote_notified_msgs:
            vote_notified_msg = await channel.send(poll_result)
            self.vote_notified_msgs[key] = vote_notified_msg.id
            fileutil.write_to_json(self.VOTES_FILE_PATH, self.vote_notified_msgs)
        else:
            vote_notified_msg = await channel.fetch_message(self.vote_notified_msgs[key])
            await vote_notified_msg.edit(content=poll_result)

    async def on_raw_reaction_remove(self, payload):
        reaction, message, channel = await self._get_datas(payload)
        if message.author != self.client.user:
            return

        if reaction.count < self.POLL_ACTIVATION_COUNT:
            return

        key = str(payload.message_id) + str(payload.emoji.id)
        if key not in self.vote_notified_msgs:
            return

        vote_notified_msg = await channel.fetch_message(self.vote_notified_msgs[key])
        if reaction.count == self.POLL_ACTIVATION_COUNT:
            await vote_notified_msg.delete()
            del self.vote_notified_msgs[key]
            fileutil.write_to_json(self.VOTES_FILE_PATH, self.vote_notified_msgs)
            return

        poll_result = f"**{reaction.count-1}** Members are voted! : {reaction.emoji}"
        poll_result += f"\nMembers who reacted: {await self._get_reacted_user_mentions(reaction)}"
        await vote_notified_msg.edit(content=poll_result)

    async def _get_datas(self, payload):
        channel = self.client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        emoji = payload.emoji
        reaction = get(message.reactions, emoji=emoji)
        return reaction, message, channel

    async def _get_reacted_user_mentions(self, reaction):
        users = [user async for user in reaction.users()]
        users.remove(self.client.user)
        return " ".join([f"<@{user.id}>" for user in users])
