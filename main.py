import os
from time import time, ctime

from nextcord import *
from nextcord.ext import tasks, commands

from DataBase import DB
from config import *

__author__ = "Vladi4ka | DendriveVlad"

db = DB()


class Bot(commands.Bot):
    async def on_ready(self):
        if not self.check_event.is_running():
            self.check_event.start()
        if not self.voice_check.is_running():
            self.voice_check.start()
        if not self.invites_check.is_running():
            self.invites_check.start()
        for member in self.get_guild(GUILD_ID).members:
            if not (db.select("members", f"id == {member.id}") or member.id == MY_ID):
                db.insert("members", id=member.id, date_connection=time())
        print("Ready")

    async def on_member_join(self, member: Member):
        if not (db.select("members", f"id == {member.id}") or member.id == MY_ID):
            db.insert("members", id=member.id, date_connection=int(time()))

    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        if not after.channel and before.channel:
            if before.channel.id == CHANNELS["Gazebo"]:
                await member.remove_roles(self.get_guild(GUILD_ID).get_role(ROLES["GazeboRole"]))
                return
            if db.select("members", f"id == {member.id}", "voice_time")["voice_time"] == 0:
                return
            if int(time()) - db.select("members", f"id == {member.id}", "voice_time")["voice_time"] >= 300:
                db.update("members", f"id == {member.id}", voice_time=1)
            else:
                db.update("members", f"id == {member.id}", voice_time=0)
        elif after.channel != before.channel and after.channel.id != IGNORE_VS:
            if before.channel and before.channel.id == CHANNELS["Gazebo"]:
                await member.remove_roles(self.get_guild(GUILD_ID).get_role(ROLES["GazeboRole"]))
                return
            if after.channel.id == CHANNELS["Gazebo"]:
                await member.add_roles(self.get_guild(GUILD_ID).get_role(ROLES["GazeboRole"]))
                return
            if db.select("members", f"id == {member.id}", "voice_time")["voice_time"] != 1:
                db.update("members", f"id == {member.id}", voice_time=int(time()))

    @tasks.loop(seconds=60)
    async def check_event(self):
        channel = utils.get(self.get_guild(GUILD_ID).channels, id=CHANNELS["Schedule"])
        if ctime()[0:3] not in ("Sat", "Sun"):
            if ctime()[0:3] == "Mon" and db.select("bot_todo", "bot == 0", "events_list")["events_list"]:
                await channel.purge()
                await channel.send("Сегодня ничего нет")
                db.update("bot_todo", "bot == 0", events_list=0)
                for member in db.select("members"):
                    if member["id"] in PROTECTED_FROM_KICK:
                        db.update("members", f"id == {member['id']}", voice_time=0, missed_events=0, kicked=0)
                        continue
                    if member["voice_time"]:
                        db.update("members", f"id == {member['id']}", voice_time=0, missed_events=0)
                    else:
                        if member["missed_events"] >= 2:
                            user = self.get_guild(GUILD_ID).get_member(member["id"])
                            if member["organizer"]:
                                await user.remove_roles(utils.get(user.guild.roles, id=ROLES["Organizer"]))
                                db.update("members", f"id == {member['id']}", missed_events=1, organizer=0, voice_time=0)
                            else:
                                if member["kicked"] >= 2:
                                    await user.ban(reason="Третий кик. Пропуск ивентов более 3-х недель")
                                    db.update("members", f"id == {member['id']}", missed_events=0, kicked=3, voice_time=0)
                                else:
                                    await user.kick(reason="Пропуск ивентов более 3-х недель")
                                    db.update("members", f"id == {member['id']}", missed_events=0, kicked=member["kicked"] + 1, voice_time=0)
                        else:
                            db.update("members", f"id == {member['id']}", missed_events=member["missed_events"] + 1, voice_time=0)
                voice = self.get_guild(GUILD_ID).get_channel(CHANNELS["Gazebo"])
                await voice.set_permissions(self.get_guild(GUILD_ID).get_role(ROLES["everyone"]), view_channel=False)
            return
        if ctime()[0:3] == "Sat" and not db.select("bot_todo", "bot == 0", "events_list")["events_list"]:
            sat = ["Расписание на Субботу:"]
            sun = ["Расписание на Воскресенье:"]
            events = db.select("events")
            events.sort(key=lambda d: d["datetime"])
            for event in events:
                match ctime(event["datetime"])[0:3]:
                    case "Sat":
                        sat.append(f"**{event['name']}** [Описание]({event['info']}) пройдёт в <t:{event['datetime']}:t>\nОрганизатор: <@{event['organizer']}>")
                    case "Sun":
                        sun.append(f"**{event['name']}** [Описание]({event['info']}) пройдёт в <t:{event['datetime']}:t>\nОрганизатор: <@{event['organizer']}>")
            await channel.purge()
            await channel.send(embed=Embed(title=sat[0], description="\n\n".join(sat[1::]), colour=0xF9BA1C))
            await channel.send(embed=Embed(title=sun[0], description="\n\n".join(sun[1::]), colour=0xF9BA1C))
            kick_members = [f"<@{m}>" for m in db.select("members", f"missed_events == 2", "id")]
            if kick_members:
                await channel.send(embed=Embed(title=sun[0],
                                               description="**Следующие участники будут кикнуты с сервера в понедельник, если не будут участвовать в ивентах:**\n" + ", ".join(kick_members),
                                               colour=0xF9BA1C))
            voice = self.get_guild(GUILD_ID).get_channel(CHANNELS["Gazebo"])
            await voice.set_permissions(self.get_guild(GUILD_ID).get_role(ROLES["everyone"]), view_channel=True, speak=True, video=True)
            db.update("bot_todo", "bot == 0", events_list=1)

        events = db.select("events")
        if type(events) == dict:
            events = [events]
        for event in events:
            if event["datetime"] - int(time()) <= 900 and not event["mention"]:
                m = await channel.send(f"@everyone \n<t:{event['datetime']}:R> будет проходить ивент: **{event['name']}** от <@{event['organizer']}>")
                db.update("events", f"name == '{event['name']}'", mention=m.id)
            elif event["datetime"] - int(time()) < 30 and not event["voice_channel"]:
                fm = await channel.fetch_message(event["mention"])
                await fm.delete()
                overwrites = {
                    self.get_guild(GUILD_ID).get_member(event["organizer"]): PermissionOverwrite(priority_speaker=True, mute_members=True, deafen_members=True, move_members=True, manage_permissions=True)
                }
                if ctime(event["datetime"])[0:3] == "Sun":
                    overwrites[self.get_guild(GUILD_ID).get_role(ROLES["everyone"])] = PermissionOverwrite(speak=False)
                voice = await self.get_guild(GUILD_ID).create_voice_channel(name=event["name"], category=utils.get(self.get_guild(GUILD_ID).categories, id=EVENTS_CATEGORY), overwrites=overwrites)
                m = await channel.send(f"@everyone \nИвент **{event['name']}** от <@{event['organizer']}> уже начался. Заходите: <#{voice.id}>")
                db.update("events", f"name == '{event['name']}'", mention=m.id, voice_channel=voice.id)

    @tasks.loop(minutes=10)
    async def voice_check(self):
        events = db.select("events", "voice_channel != 0")
        if events is None:
            return
        if type(events) == dict:
            events = [events]

        for event in events:
            if int(time()) - event["datetime"] >= 1800:
                voice = utils.get(self.get_guild(GUILD_ID).voice_channels, id=event["voice_channel"])
                if voice.members:
                    continue
                try:
                    await voice.delete(reason="Ивент окончен")
                except AttributeError:
                    pass
                mess = await utils.get(self.get_guild(GUILD_ID).text_channels, id=CHANNELS["Schedule"]).fetch_message(event["mention"])
                mess2 = await utils.get(self.get_guild(GUILD_ID).text_channels, id=CHANNELS["Events_list"]).fetch_message(event["message_id"])
                try:
                    await mess.delete()
                except AttributeError:
                    pass
                await mess2.delete()
                db.delete("events", f"voice_channel == {event['voice_channel']}")

    @tasks.loop(hours=24)
    async def invites_check(self):
        for invite in await self.get_guild(GUILD_ID).invites():
            if invite.uses:
                invite_count = db.select("members", f"id == {invite.inviter.id}", "invites")["invites"]
                if invite_count < 5 <= invite_count + invite.uses:
                    member = self.get_guild(GUILD_ID).get_member(invite.inviter.id)
                    await member.add_roles(self.get_guild(GUILD_ID).get_role(ROLES["Extrovert"]))
                db.update("members", f"id == {invite.inviter.id}", invites=db.select("members", f"id == {invite.inviter.id}", "invites")["invites"] + invite.uses)
                await invite.delete()


client = Bot(command_prefix="/", intents=Intents.all())
client.remove_command("help")
for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        client.load_extension(f"cogs.{file[:-3]}")
client.run(TOKEN)
