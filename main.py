import discord
import os # We added this to read secure variables
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class SignupView(discord.ui.View):
    def __init__(self, qty_needed):
        super().__init__(timeout=None)
        self.qty_needed = qty_needed
        self.participants = []

    async def update_message(self, interaction: discord.Interaction):
        lines = []
        for i in range(1, self.qty_needed + 1):
            if i <= len(self.participants):
                user, ign = self.participants[i-1]
                lines.append(f"{i}. {user} | IGN: {ign}")
            else:
                lines.append(f"{i}. ---")
        
        embed = discord.Embed(title="Alpha Tester Sign-up", description="\n".join(lines), color=discord.Color.green())
        
        if len(self.participants) >= self.qty_needed:
            self.children[0].disabled = True
            embed.add_field(name="Status", value="Registration Closed!")
        
        await interaction.message.edit(embed=embed, view=self)

    @discord.ui.button(label="Sign Up!", style=discord.ButtonStyle.green)
    async def signup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if any(p[0] == interaction.user.mention for p in self.participants):
            await interaction.response.send_message("You are already signed up!", ephemeral=True)
            return

        class IGNModal(discord.ui.Modal, title='Enter your IGN'):
            ign = discord.ui.TextInput(label='Minecraft IGN', required=True)
            
            def __init__(self, view):
                super().__init__()
                self.view = view

            async def on_submit(self, i: discord.Interaction):
                self.view.participants.append((i.user.mention, self.ign.value))
                await self.view.update_message(i)
                await i.response.send_message("Registered!", ephemeral=True)

        await interaction.response.send_modal(IGNModal(self))

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user.name} and synced commands!')

@bot.tree.command(name="alphatestsignup", description="Start an alpha test signup sheet")
@app_commands.checks.has_permissions(administrator=True)
async def alphatestsignup(interaction: discord.Interaction, qty: int):
    embed = discord.Embed(title="Alpha Tester Sign-up", description="\n".join([f"{i}. ---" for i in range(1, qty + 1)]), color=discord.Color.blue())
    view = SignupView(qty)
    await interaction.response.send_message(embed=embed, view=view)

# THIS IS THE SECURE PART:
# It will look for a variable named 'TOKEN' in your hosting dashboard
bot.run(os.environ['TOKEN'])