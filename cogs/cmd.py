from time import time, ctime

from nextcord import *
from nextcord.ext import commands

from config import *
from DataBase import DB
from Buttons import ChoiceDay, EventRemoveAccept, Voting

db = DB()


class CMD(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    @slash_command(name="create", description="Создать ивент", guild_ids=[GUILD_ID])
    async def create(self, interaction: Interaction, event_name):
        if interaction.channel_id != CHANNELS["Organizers"]:
            await interaction.response.send_message(embed=Embed(title="❌Wrong channel❌", colour=0xBF1818), ephemeral=True)
            return
        if len(event_name) > 128:
            await interaction.response.send_message(embed=Embed(title="❌Название ивента не может быть больше 128 символов❌", description=f"Скопируйте и сделайте его короче: **{event_name}**", colour=0xBF1818), ephemeral=True)
            return
        view = ChoiceDay()
        await interaction.response.send_message("Выберите день проведения", ephemeral=True, view=view)
        await view.wait()
        if not view.time:
            return

        weekdays = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
        now_time = int(time())
        if weekdays.index(ctime(now_time)[0:3]) > 4:
            now_time += 172800
        unix_event = ((now_time + 86400 * (view.day - (weekdays.index(ctime(now_time)[0:3]) + 1))) - [(h * 60 + m) * 60 + s for h, m, s in [list(map(int, ctime(now_time)[11:19].split(":")))]][0]) + (view.time * 60 * 60 if view.time < 100 else ((view.time // 10) * 60 + 30) * 60)
        event = ctime(unix_event).split()
        schedule_event = self.__getEventDetails(event)
        for channel in interaction.guild.channels:
            if channel.id == CHANNELS["Events_list"]:
                event_message = await channel.send(embed=Embed(title=event_name, description=f'Запланировано на **{schedule_event["day"]} {schedule_event["date"]} {schedule_event["month"]}** в **{schedule_event["time"]}** по МСК.\n'
                                                                                             f'Организатор: {interaction.user.mention}', colour=0x5BF5D1))
                db.insert("events", datetime=unix_event, name=event_name, organizer=interaction.user.id, message_id=event_message.id)
            elif channel.id == CHANNELS["Organizers"]:
                await channel.send(f"<@{interaction.user.id}> создал событие", embed=Embed(title=event_name, description=f'На {schedule_event["day"]} {schedule_event["date"]} {schedule_event["month"]} в {schedule_event["time"]} по МСК.', colour=0x21F300))

    @slash_command(name="remove", description="Отменить ивент", guild_ids=[GUILD_ID])
    async def remove(self, interaction: Interaction, event_name):
        if interaction.channel_id != CHANNELS["Organizers"]:
            await interaction.response.send_message(embed=Embed(title="❌Wrong channel❌", colour=0xBF1818), ephemeral=True)
            return
        if len(event_name) > 128:
            await interaction.response.send_message(embed=Embed(title="❌Название ивента не может быть больше 128 символов❌", colour=0xBF1818), ephemeral=True)
            return
        event = db.select("events", f"name == '{event_name}'")
        if not event:
            await interaction.response.send_message(embed=Embed(title="❌Такого ивента не существует❌", colour=0xBF1818), ephemeral=True)
            return
        today = ctime(int(time())).split()
        if today[0] in ("Sat", "Sun"):
            block_date = (int(today[2])) if today[0] == "Sun" else (int(today[2]), int(today[2]) + 1)
            if int(ctime(event["datetime"]).split()[2]) in block_date:
                await interaction.response.send_message(embed=Embed(title="❌Невозможно удалить уже утверждённый ивент❌", description="Если Вы не можете провести ивент, то попросите это сделать кого-нибудь другого", colour=0xBF1818), ephemeral=True)
                return

        view = EventRemoveAccept()
        await interaction.response.send_message(f"Вы уверены, что хотите удалить ивент **{event['name']}**?", ephemeral=True, view=view)
        await view.wait()
        if view.accept:
            db.delete("events", f"name == '{event_name}'")
            for channel in interaction.guild.channels:
                if channel.id == CHANNELS["Events_list"]:
                    m = await channel.fetch_message(event["message_id"])
                    await m.delete()
                elif channel.id == CHANNELS["Organizers"]:
                    schedule_event = self.__getEventDetails(ctime(event["datetime"]).split())
                    await channel.send(f"{interaction.user.mention} отменяет событие", embed=Embed(title=event_name, description=f'На {schedule_event["day"]} {schedule_event["date"]} {schedule_event["month"]} в {schedule_event["time"]} по МСК.', colour=0x21F300))

    @slash_command(name="promote", description="Принять участника на Организатора", guild_ids=[GUILD_ID])
    async def promote(self, interaction: Interaction, mention):
        if interaction.channel_id != CHANNELS["Organizers"]:
            await interaction.response.send_message(embed=Embed(title="❌Wrong channel❌", colour=0xBF1818), ephemeral=True)
            return
        member = self.__getMember(mention)
        if not member:
            await interaction.response.send_message(embed=Embed(title="❌Данного пользователя не существует❌", colour=0xBF1818), ephemeral=True)
            return
        if member.id == MY_ID:
            await interaction.response.send_message(embed=Embed(title="❌🤖Бот не человек❌", colour=0xBF1818), ephemeral=True)
            return
        member_date = db.select("members", f"id == '{member.id}'")
        if member_date["organizer"]:
            await interaction.response.send_message(embed=Embed(title="❌Данного пользователя уже является Организатором❌", colour=0xBF1818), ephemeral=True)
            return

        orgs_count = self.__GetOrgsCount()
        view = Voting(orgs_count, interaction.user, f"{interaction.user.mention} хочет повысить участника {member.mention} до организатора. Нажмите на кнопку нижу, чтобы проголосовать **ЗА**.")
        await interaction.response.send_message(f"{interaction.user.mention} хочет повысить участника {member.mention} до организатора. Нажмите на кнопку нижу, чтобы проголосовать **ЗА**. (1/{orgs_count if orgs_count <= 5 else 5})", view=view)
        await view.wait()
        for channel in interaction.guild.channels:
            if channel.id == CHANNELS["Organizers"]:
                if view.accept_count >= view.max:
                    await channel.send(embed=Embed(title=f"{member} принят на роль Организатора", colour=0x21F300))
                    await member.add_roles(utils.get(member.guild.roles, id=ROLES["Organizer"]))
                    db.update("members", f"id == {member.id}", organizer=1)
                else:
                    await channel.send(embed=Embed(title=f"{member} НЕ принят на роль Организатора", description="Недостаточно голосов", colour=0xBF1818))
                break

    @slash_command(name="demote", description="Снять участника с Организатора", guild_ids=[GUILD_ID])
    async def demote(self, interaction: Interaction, mention):
        if interaction.channel_id != CHANNELS["Organizers"]:
            await interaction.response.send_message(embed=Embed(title="❌Wrong channel❌", colour=0xBF1818), ephemeral=True)
            return
        member = self.__getMember(mention)
        if not member:
            await interaction.response.send_message(embed=Embed(title="❌Данного пользователя не существует❌", colour=0xBF1818), ephemeral=True)
            return
        if member.id == MY_ID:
            await interaction.response.send_message(embed=Embed(title="❌🤖Бот не человек❌", colour=0xBF1818), ephemeral=True)
            return
        if member.id == VLAD_ID:
            await interaction.response.send_message("._.", ephemeral=True)
            return
        member_date = db.select("members", f"id == '{member.id}'")
        if not member_date["organizer"]:
            await interaction.response.send_message(embed=Embed(title="❌Данного пользователя не является Организатором❌", colour=0xBF1818), ephemeral=True)
            return

        orgs_count = self.__GetOrgsCount()
        if orgs_count < 6:
            orgs_count -= 1
        view = Voting(orgs_count, interaction.user, f"{interaction.user.mention} хочет снять участника {member.mention} с организатора. Нажмите на кнопку нижу, чтобы проголосовать **ЗА**.")
        m = await interaction.response.send_message(f"{interaction.user.mention} хочет снять участника {member.mention} с организатора. Нажмите на кнопку нижу, чтобы проголосовать **ЗА**. (1/{orgs_count if orgs_count <= 5 else 5})", view=view)
        await view.wait()
        for channel in interaction.guild.channels:
            if channel.id == CHANNELS["Organizers"]:
                if view.accept_count >= view.max:
                    await channel.send(embed=Embed(title=f"{member} снят с роли Организатора", colour=0x21F300))
                    await member.remove_roles(utils.get(member.guild.roles, id=ROLES["Organizer"]))
                    db.update("members", f"id == {member.id}", organizer=0)
                else:
                    await channel.send(embed=Embed(title=f"{member} НЕ снят с роли Организатора", description="Недостаточно голосов", colour=0xBF1818))
                break

    @slash_command(name="kick", description="Исключить участника с сервера", guild_ids=[GUILD_ID])
    async def kick(self, interaction: Interaction, mention):
        if interaction.channel_id != CHANNELS["Organizers"]:
            await interaction.response.send_message(embed=Embed(title="❌Wrong channel❌", colour=0xBF1818), ephemeral=True)
            return
        member = self.__getMember(mention)
        if not member:
            await interaction.response.send_message(embed=Embed(title="❌Данного пользователя не существует❌", colour=0xBF1818), ephemeral=True)
            return
        if member.id == MY_ID:
            await interaction.response.send_message(embed=Embed(title="❌🤖Бот не человек❌", colour=0xBF1818), ephemeral=True)
            return
        if member.id == VLAD_ID:
            await interaction.response.send_message("._.", ephemeral=True)
            return
        member_date = db.select("members", f"id == '{member.id}'")
        orgs_count = self.__GetOrgsCount()
        if orgs_count < 6:
            orgs_count -= 1
        view = Voting(orgs_count, interaction.user, f"{interaction.user.mention} хочет кикнуть участника {member.mention}. Нажмите на кнопку нижу, чтобы проголосовать **ЗА**.")
        m = await interaction.response.send_message(f"{interaction.user.mention} хочет кикнуть участника {member.mention}. Нажмите на кнопку нижу, чтобы проголосовать **ЗА**. (1/{orgs_count if orgs_count <= 5 else 5})", view=view)
        await view.wait()
        for channel in interaction.guild.channels:
            if channel.id == CHANNELS["Organizers"]:
                if view.accept_count >= view.max:
                    await channel.send(embed=Embed(title=f"{member} исключён с сервера", colour=0x21F300))
                    if member_date["kicked"] >= 2:
                        await member.ban(reason="Третий кик. Решение организаторов")
                    else:
                        await member.kick(reason="Решение организаторов")
                    db.update("members", f"id == {member.id}", kicked=member_date["kicked"] + 1)
                else:
                    await channel.send(embed=Embed(title=f"{member} остаётся на сервере", description="Недостаточно голосов", colour=0xBF1818))
                break

    def __getEventDetails(self, event) -> dict:
        schedule_event = {}
        for i in event:
            match event.index(i):
                case 0:
                    if i == "Sat":
                        schedule_event["day"] = "Субботу"
                    else:
                        schedule_event["day"] = "Воскресенье"
                case 1:
                    schedule_event["month"] = {"Jan": "Января", "Feb": "Февраля", "Mar": "Марта", "Apr": "Апреля", "May": "Мая", "Jun": "Июня", "Jul": "Июля", "Aug": "Августа", "Sep": "Сентября", "Oct": "Октября", "Nov": "Ноября", "Dec": "Декабря"}[i]
                case 2:
                    schedule_event["date"] = i
                case 3:
                    schedule_event["time"] = i[0:5]
        return schedule_event

    def __getMember(self, str_member) -> Member | None:
        if len(str_member) in [21, 22] and str_member[0:2] == "<@" and str_member[-1] == ">":
            try:
                return self.client.get_guild(GUILD_ID).get_member(int(str_member[-19:-1]))
            except ValueError:
                pass
        for user in self.client.get_guild(GUILD_ID).members:
            if user.nick:
                if user.nick.lower() == str_member.lower():
                    return user
            elif user.name.lower() == str_member.lower():
                return user
        return None

    def __GetOrgsCount(self) -> int:
        orgs_count = db.select("members", "organizer == 1")
        if type(orgs_count) is dict:
            return 1
        else:
            return len(orgs_count)


def setup(client):
    client.add_cog(CMD(client))
