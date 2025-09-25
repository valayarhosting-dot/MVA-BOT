import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# === CONFIG ===
GUILD_ID = 123456789012345678  # Your guild/server ID
APPLICATION_CHANNEL_ID = None  # Bot auto-creates if None
STAFF_CHANNEL_ID = 123456789012345679  # Staff review channel
MEMBER_ROLE_ID = 123456789012345680  # Approved role

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ====== Application Modal ======
class ApplicationForm(discord.ui.Modal, title="Gang Application Form"):
    name = discord.ui.TextInput(label="Your Name", placeholder="Enter your full name")
    age = discord.ui.TextInput(label="Age", placeholder="Enter your age", min_length=1, max_length=3)
    reason = discord.ui.TextInput(label="Why do you want to join?", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        # Send application to staff channel
        staff_channel = interaction.client.get_channel(STAFF_CHANNEL_ID)
        if staff_channel:
            embed = discord.Embed(title="📩 New Application", color=discord.Color.blurple())
            embed.add_field(name="Applicant", value=interaction.user.mention, inline=False)
            embed.add_field(name="Name", value=self.name.value, inline=True)
            embed.add_field(name="Age", value=self.age.value, inline=True)
            embed.add_field(name="Reason", value=self.reason.value, inline=False)

            view = ReviewButtons(applicant=interaction.user)
            await staff_channel.send(embed=embed, view=view)

        await interaction.response.send_message("✅ Application submitted! Staff will review soon.", ephemeral=True)

# ====== Approve/Reject Buttons ======
class ReviewButtons(discord.ui.View):
    def __init__(self, applicant: discord.Member):
        super().__init__(timeout=None)
        self.applicant = applicant

    @discord.ui.button(label="✅ Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(MEMBER_ROLE_ID)
        if role:
            await self.applicant.add_roles(role, reason="Application approved")
        try:
            await self.applicant.send(f"🎉 Your application was **accepted** in {interaction.guild.name}!")
        except:
            pass
        await interaction.response.send_message(f"✅ Approved {self.applicant.mention}", ephemeral=True)

    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.applicant.send(f"❌ Sorry, your application in {interaction.guild.name} was rejected.")
        except:
            pass
        await interaction.response.send_message(f"❌ Rejected {self.applicant.mention}", ephemeral=True)

# ====== Setup Command ======
@bot.tree.command(name="setup_applications", description="Create application channel", guild=discord.Object(id=GUILD_ID))
async def setup_applications(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("🚫 Only admins can run this.", ephemeral=True)

    guild = interaction.guild
    channel = await guild.create_text_channel("📋applications")

    embed = discord.Embed(
        title="Gang Applications",
        description="Click the button below to apply for membership.",
        color=discord.Color.blue()
    )
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="📝 Apply", style=discord.ButtonStyle.primary, custom_id="apply_button"))

    await channel.send(embed=embed, view=view)
    await interaction.response.send_message(f"✅ Application channel created: {channel.mention}", ephemeral=True)

# ====== Button Listener ======
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data.get("custom_id") == "apply_button":
            await interaction.response.send_modal(ApplicationForm())

bot.run(TOKEN)