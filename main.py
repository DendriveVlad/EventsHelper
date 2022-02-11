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
            db.insert("members", id=member.id, date_connection=time())

    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        if not after.channel and before.channel:
            if db.select("members", f"id == {member.id}", "voice_time")["voice_time"] == 0:
                return
            if int(time()) - db.select("members", f"id == {member.id}", "voice_time")["voice_time"] >= 300:
                db.update("members", f"id == {member.id}", voice_time=1)
            else:
                db.update("members", f"id == {member.id}", voice_time=0)
        elif after.channel != before.channel:
            if db.select("members", f"id == {member.id}", "voice_time")["voice_time"] != 1:
                db.update("members", f"id == {member.id}", voice_time=time())

    @tasks.loop(seconds=60)
    async def check_event(self):
        channel = utils.get(self.get_guild(GUILD_ID).channels, id=CHANNELS["Schedule"])
        if ctime()[0:3] not in ("Sat", "Sun"):
            if ctime()[0:3] == "Mon" and db.select("bot_todo", "bot == 0", "events_list")["events_list"]:
                await channel.purge()
                await channel.send("Сегодня ничего нет")
                db.update("bot_todo", "bot == 0", events_list=0)
                for member in db.select("members"):
                    if member["voice_text"]:
                        db.update("members", f"id == {member.id}", voice_time=0, missed_events=0)
                    else:
                        if member["missed_events"] >= 2:
                            if member["organizer"]:
                                await member.remove_roles(utils.get(member.guild.roles, id=ROLES["Organizer"]))
                                db.update("members", f"id == {member.id}", missed_events=1, organizer=0)
                            else:
                                if member["kicked"] >= 2:
                                    await member.ban(reason="Третий кик. Пропуск ивентов более 3-х недель")
                                    db.update("members", f"id == {member.id}", missed_events=0, kicked=3)
                                else:
                                    await member.kick(reason="Пропуск ивентов более 3-х недель")
                                    db.update("members", f"id == {member.id}", missed_events=0, kicked=member["kicked"] + 1)
                        else:
                            db.update("members", f"id == {member.id}", missed_events=member["missed_events"] + 1)

            return
        if ctime()[0:3] == "Sat" and not db.select("bot_todo", "bot == 0", "events_list")["events_list"]:
            sat = ["Расписание на Субботу:"]
            sun = ["Расписание на Воскресенье:"]
            events = db.select("events")
            events.sort(key=lambda d: d["datetime"])
            for event in events:
                match ctime(event["datetime"])[0:3]:
                    case "Sat":
                        sat.append(f"**{event['name']}** пройдёт <t:{event['datetime']}:t>\nОрганизатор: <@{event['organizer']}>")
                    case "Sun":
                        sun.append(f"**{event['name']}** пройдёт <t:{event['datetime']}:t>\nОрганизатор: <@{event['organizer']}>")
            await channel.purge()
            await channel.send(embed=Embed(title=sat[0], description="\n\n".join(sat[1::]) + "\n\n***Время указано в МСК (UTC+3)**", colour=0xF9BA1C))
            await channel.send(embed=Embed(title=sun[0], description="\n\n".join(sun[1::]) + "\n\n***Время указано в МСК (UTC+3)**", colour=0xF9BA1C))
            db.update("bot_todo", "bot == 0", events_list=1)
        for event in db.select("events"):
            if event["datetime"] - int(time()) <= 900 and not event["mention"]:
                m = await channel.send(f"@everyone \nЧерез <t:{event['datetime']}:R> будет проходить ивент: \"{event['name']}\" от <@{event['organizer']}>")
                db.update("events", f"name == '{event['name']}'", mention=m.id)
            elif event["datetime"]- int(time())  < 30:
                fm = await channel.fetch_message(event["mention"])
                await fm.delete()
                m = await channel.send(f"@everyone \nУже совсем скоро начнётся ивент: \"{event['name']}\" от <@{event['organizer']}>")
                overwrites = {
                    self.get_guild(GUILD_ID).get_member(event["organizer"]): PermissionOverwrite(priority_speaker=True, mute_members=True, deafen_members=True, move_members=True, manage_channels=True)
                }
                if ctime(event["datetime"])[0:3] == "Sun":
                    overwrites[self.get_guild(GUILD_ID).get_role(ROLES["everyone"])] = PermissionOverwrite(speak=False)
                voice = await self.get_guild(GUILD_ID).create_voice_channel(name=event["name"], category=utils.get(self.get_guild(GUILD_ID).categories, id=EVENTS_CATEGORY), overwrites=overwrites)
                db.update("events", f"name == '{event['name']}'", mention=m.id, voice_channel=voice)

    @tasks.loop(minutes=10)
    async def voice_check(self):
        for voice in self.get_guild(GUILD_ID).voice_channels:
            if voice.members or voice.id == IGNORE_VS:
                continue
            event = db.select("events", f"voice == {voice.id}", "datetime", "message_id", "mention")
            if int(time()) - event["datetime"] >= 1800:
                try:
                    await voice.delete(reason="Ивент окончен")
                except AttributeError:
                    pass
                mess = await utils.get(self.get_guild(GUILD_ID).text_channels, id=CHANNELS["Schedule"]).fetch_message(event["mention"])
                mess2 = await utils.get(self.get_guild(GUILD_ID).text_channels, id=CHANNELS["Events_list"]).fetch_message(event["message_id"])
                await mess.delete()
                await mess2.delete()
                db.delete("events", f"voice == {voice.id}")

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
