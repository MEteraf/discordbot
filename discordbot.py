import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
from aiohttp import web
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")



# ----------------------
# Intents
# ----------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# ----------------------
# ایجاد بات
# ----------------------
bot = commands.Bot(command_prefix="/", intents=intents)


# ----------------------
# وب‌سرور برای روشن ماندن
# ----------------------
async def handle(request):
    return web.Response(text="✅ Bot is alive and running!")


async def run_webserver():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Web server running on port {port}")


# ----------------------
# رویداد آماده شدن بات
# ----------------------
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online and ready!")
    await bot.change_presence(
        activity=discord.Game(name="Iran Line Role Play | /serverinfo"),
        status=discord.Status.online)

    # Sync Slash Commands
    try:
        guild = discord.Object(id=1277539538977423481)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print(f"✅ Slash commands synced to guild {guild.id}!")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

    # شروع پینگ خودکار بعد از آماده شدن بات
    bot.loop.create_task(ping_self())


# ----------------------
# پینگ خودکار (برای بیدار نگه داشتن)
# ----------------------
async def ping_self():
    await asyncio.sleep(10)  # کمی صبر تا وب‌سرور بالا بیاد
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get("http://localhost:8080/") as resp:
                    if resp.status == 200:
                        print("🔁 Self-ping OK")
            except Exception as e:
                print(f"⚠️ Ping failed: {e}")
            await asyncio.sleep(300)  # هر 5 دقیقه


# ----------------------
# دستور serverinfo
# ----------------------
@bot.tree.command(name="serverinfo", description="اطلاعات سرور را نمایش بده")
@app_commands.guild_only()
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    owner = guild.owner
    created_at = guild.created_at.strftime("%Y-%m-%d")

    embed = discord.Embed(title=f"اطلاعات سرور {guild.name}",
                          description="Server Information",
                          color=discord.Color.blue())

    embed.set_author(name=guild.name,
                     icon_url=guild.icon.url if guild.icon else None)
    embed.add_field(name="🟡 نام سرور", value=f"**{guild.name}**", inline=False)
    embed.add_field(name="🟢 بنیانگذار سرور",
                    value=owner.mention if owner else "نامشخص",
                    inline=True)
    embed.add_field(name="🔵 تعداد اعضا",
                    value=str(guild.member_count),
                    inline=True)
    embed.add_field(name="📅 تاریخ ایجاد", value=created_at, inline=True)
    embed.add_field(name="🟣 آیپی سرور VMP",
                    value="**5.57.35.181**",
                    inline=False)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.set_image(
        url=
        "https://cdn.discordapp.com/attachments/992344550683201607/1427254991374254162/f174038a6a413a80.png"
    )
    embed.set_footer(text="Iran Line Support Team")

    await interaction.response.send_message(embed=embed)


# ----------------------
# دستور status
# ----------------------
@bot.tree.command(name="status", description="تغییر استتوس بات")
@app_commands.describe(text="متن استتوس جدید")
async def status(interaction: discord.Interaction, text: str = None):
    if text:
        await bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name=text),
                                  status=discord.Status.online)
        await interaction.response.send_message(
            f"✅ استتوس بات به **{text}** تغییر یافت!", ephemeral=True)
    else:
        await bot.change_presence(
            activity=discord.Game(name="Iran Line Role Play | /serverinfo"),
            status=discord.Status.online)
        await interaction.response.send_message(
            "✅ استتوس بات به حالت پیش‌فرض تغییر یافت!", ephemeral=True)


# ----------------------
# اجرای همزمان وب‌سرور و بات
# ----------------------
async def main():
    await run_webserver()
    await bot.start(os.getenv("Discord_Token"))


asyncio.run(main())
