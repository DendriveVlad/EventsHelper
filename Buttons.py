from nextcord import ButtonStyle, Embed, Interaction
from nextcord.ui import View, button


class ChoiceDay(View):
    def __init__(self):
        super().__init__()
        self.day = 0
        self.time = 0
        self.time_class = ChoiceTime()

    @button(label="Суббота", style=ButtonStyle.green)
    async def saturday(self, button, interaction):
        self.day = 6
        await interaction.response.send_message("Выберите время проведения (По МСК)", ephemeral=True, view=self.time_class)
        await self.time_class.wait()
        self.time = self.time_class.value
        self.stop()

    @button(label="Воскресенье", style=ButtonStyle.green)
    async def sunday(self, button, interaction):
        self.day = 7
        await interaction.response.send_message("Выберите время проведения (По МСК)", ephemeral=True, view=self.time_class)
        await self.time_class.wait()
        self.time = self.time_class.value
        self.stop()


class ChoiceTime(View):
    def __init__(self):
        super().__init__()
        self.value = 0

    @button(label="12:00", style=ButtonStyle.green)
    async def twelve(self, button, interaction):
        self.value = 12
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="12:30", style=ButtonStyle.green)
    async def half_thirteen(self, button, interaction):
        self.value = 125
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="13:00", style=ButtonStyle.green)
    async def thirteen(self, button, interaction):
        self.value = 13
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="13:30", style=ButtonStyle.green)
    async def half_fourteen(self, button, interaction):
        self.value = 135
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="14:00", style=ButtonStyle.green)
    async def fourteen(self, button, interaction):
        self.value = 14
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="14:30", style=ButtonStyle.green)
    async def half_fifteen(self, button, interaction):
        self.value = 145
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="15:00", style=ButtonStyle.green)
    async def fifteen(self, button, interaction):
        self.value = 15
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="15:30", style=ButtonStyle.green)
    async def half_sixteen(self, button, interaction):
        self.value = 155
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="16:00", style=ButtonStyle.green)
    async def sixteen(self, button, interaction):
        self.value = 16
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="16:30", style=ButtonStyle.green)
    async def half_seventeen(self, button, interaction):
        self.value = 165
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="17:00", style=ButtonStyle.green)
    async def seventeen(self, button, interaction):
        self.value = 17
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="17:30", style=ButtonStyle.green)
    async def half_eighteen(self, button, interaction):
        self.value = 175
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="18:00", style=ButtonStyle.green)
    async def eighteen(self, button, interaction):
        self.value = 18
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="18:30", style=ButtonStyle.green)
    async def half_nineteen(self, button, interaction):
        self.value = 185
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="19:00", style=ButtonStyle.green)
    async def nineteen(self, button, interaction):
        self.value = 19
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="19:30", style=ButtonStyle.green)
    async def half_twenty(self, button, interaction):
        self.value = 195
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="20:00", style=ButtonStyle.green)
    async def twenty(self, button, interaction):
        self.value = 20
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="20:30", style=ButtonStyle.green)
    async def half_twenty_one(self, button, interaction):
        self.value = 205
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="21:00", style=ButtonStyle.green)
    async def twenty_one(self, button, interaction):
        self.value = 21
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="21:30", style=ButtonStyle.green)
    async def half_twenty_two(self, button, interaction):
        self.value = 215
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="22:00", style=ButtonStyle.green)
    async def twenty_two(self, button, interaction):
        self.value = 22
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="22:30", style=ButtonStyle.green)
    async def half_twenty_three(self, button, interaction):
        self.value = 225
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="23:00", style=ButtonStyle.green)
    async def twenty_three(self, button, interaction):
        self.value = 23
        await interaction.response.send_message(embed=Embed(title="Ивент запланирован", colour=0x21F300), ephemeral=True)
        self.stop()


class EventRemoveAccept(View):
    def __init__(self):
        super().__init__()
        self.accept = None

    @button(label="Удалить", style=ButtonStyle.red)
    async def accept(self, button, interaction):
        self.accept = True
        await interaction.response.send_message(embed=Embed(title="Ивент отменён", colour=0x21F300), ephemeral=True)
        self.stop()

    @button(label="Отмена", style=ButtonStyle.grey)
    async def cancel(self, button, interaction):
        self.accept = False
        await interaction.response.send_message(embed=Embed(title="Команда отозвана"), ephemeral=True)
        self.stop()


class Voting(View):
    def __init__(self, need_accept, creator, message):
        super().__init__()
        self.message = message
        self.creator = creator
        self.accepted = [creator.id]
        self.max = need_accept if need_accept <= 5 else 5
        self.accept_count = 1

    @button(label="Проголосовать", style=ButtonStyle.green, emoji="✅")
    async def accept(self, button, interaction: Interaction):
        if interaction.user.id not in self.accepted:
            self.accepted.append(interaction.user.id)
            self.accept_count += 1
            await interaction.message.edit(content=f"{self.message} ({self.accept_count}/{self.max})")
            if self.accept_count >= self.max:
                await interaction.message.delete()
                self.stop()
