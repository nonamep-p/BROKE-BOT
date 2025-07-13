import discord
from discord.ext import commands
import os
import logging
import asyncio
from datetime import datetime
import threading
from web_server import run_web_server
from config import COLORS, EMOJIS, get_server_config
from utils.database import initialize_database
from cogs.help import HelpView
from utils import create_embed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix='$',
    intents=intents,
    help_command=None,  # We'll implement our own
    case_insensitive=True,
    owner_id=1297013439125917766  # NoNameP_P's user ID
)

@bot.event
async def on_ready():
    """Called when the bot is ready."""
    logger.info(f'{bot.user.name} (Kwami of Destruction) has awakened! 🧀')
    logger.info(f'{bot.user.name} is causing chaos in {len(bot.guilds)} guilds')

    # Initialize database
    try:
        await initialize_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    # Set bot start time for uptime calculation
    bot.start_time = datetime.now()

    # Set bot status
    await bot.change_presence(
        activity=discord.Game(name="AI Chat & RPG Adventures | $help")
    )

    # Start reminder checking task
    bot.loop.create_task(check_reminders_task())

async def check_reminders_task():
    """Background task to check and send reminders."""
    while True:
        try:
            from replit import db
            from datetime import datetime

            reminders = db.get("scheduled_reminders", [])
            current_time = datetime.now()

            sent_reminders = []
            remaining_reminders = []

            for reminder in reminders:
                reminder_time = datetime.fromisoformat(reminder["time"])
                if current_time >= reminder_time:
                    # Send reminder
                    embed = create_embed(
                        "⏰ Scheduled Reminder",
                        reminder["message"],
                        COLORS['info']
                    )

                    # Send to all guilds
                    for guild in bot.guilds:
                        try:
                            channel = guild.system_channel or guild.text_channels[0] if guild.text_channels else None
                            if channel:
                                await channel.send(embed=embed)
                        except:
                            continue

                    sent_reminders.append(reminder)
                else:
                    remaining_reminders.append(reminder)

            # Update reminders
            if sent_reminders:
                db["scheduled_reminders"] = remaining_reminders
                logger.info(f"Sent {len(sent_reminders)} scheduled reminders")

        except Exception as e:
            logger.error(f"Error in reminder task: {e}")

        # Check every 5 minutes
        await asyncio.sleep(300)

@bot.event
async def on_guild_join(guild):
    """Called when the bot joins a new guild."""
    logger.info(f"Joined new guild: {guild.name} ({guild.id})")

    # Try to send welcome message
    try:
        # Find a suitable channel to send welcome message
        channel = None

        # Try to find general or welcome channel
        for ch in guild.text_channels:
            if ch.name.lower() in ['general', 'welcome', 'bot-commands']:
                if ch.permissions_for(guild.me).send_messages:
                    channel = ch
                    break

        # If no suitable channel found, try the first channel we can send to
        if not channel:
            for ch in guild.text_channels:
                if ch.permissions_for(guild.me).send_messages:
                    channel = ch
                    break

        if channel:
            embed = discord.Embed(
                title="🧀 Thanks for adding Plagg - AI Chatbot!",
                description=(
                    "I'm Plagg, your AI companion with gaming features!\n\n"
                    "**🤖 Main Feature - AI Chat:**\n"
                    "• Advanced AI chatbot powered by Google Gemini\n"
                    "• Natural conversations with Plagg's personality\n"
                    "• Context-aware responses and memory\n"
                    "• Just mention me or reply to chat!\n\n"
                    "**🎮 Bonus Features:**\n"
                    "• Complete RPG system with adventures and battles\n"
                    "• Moderation and admin tools\n\n"
                    "**🚀 Getting Started:**\n"
                    "Mention me `@Plagg` to start chatting!\n"
                    "Use `$help` for all commands\n"
                    "Use `$start` for RPG features\n\n"
                    "**Credits:** Created by NoNameP_P"
                ),
                color=COLORS['success']
            )
            embed.set_thumbnail(url=bot.user.display_avatar.url)
            embed.set_footer(text="Plagg AI Chatbot | Made by NoNameP_P | Ready to chat!")

            await channel.send(embed=embed)
    except Exception as e:
        logger.error(f"Error sending welcome message to {guild.name}: {e}")

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands."""
    if isinstance(error, commands.CommandNotFound):
        # Don't respond to unknown commands
        return

    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Missing Permissions",
            description="You don't have the required permissions to use this command.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)

    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            title="❌ Bot Missing Permissions",
            description="I don't have the required permissions to execute this command.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="⏰ Command on Cooldown",
            description=f"This command is on cooldown. Try again in {error.retry_after:.1f} seconds.",
            color=COLORS['warning']
        )
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Missing Required Argument",
            description=f"Missing required argument: `{error.param.name}`\n\nUse `$help {ctx.command.name}` for more info.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)

    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="❌ Invalid Argument",
            description=f"Invalid argument provided. Use `$help {ctx.command.name}` for correct usage.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)

    else:
        logger.error(f"Unhandled error in command {ctx.command}: {error}")
        embed = discord.Embed(
            title="❌ An Error Occurred",
            description="An unexpected error occurred. Please try again later.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)

@bot.event
async def on_error(event, *args, **kwargs):
    """Global error handler for events."""
    logger.error(f"Error in event {event}: {args}")

@bot.event
async def on_member_join(member):
    """Handle new member joins."""
    try:
        # Get server config
        config = get_server_config(member.guild.id)
        welcome_channel_id = config.get('welcome_channel')

        # Get custom welcome message
        from replit import db
        custom_welcome = db.get("welcome_message", None)

        if welcome_channel_id:
            welcome_channel = member.guild.get_channel(welcome_channel_id)
            if welcome_channel:
                if custom_welcome:
                    description = custom_welcome.replace("{mention}", member.mention).replace("{guild}", member.guild.name)
                else:
                    description = (f"Hey {member.mention}! Welcome to {member.guild.name}! 🧀\n\n"
                                 f"🎮 Try `{config.get('prefix', '$')}help` to see what I can do!\n"
                                 f"🗺️ Use `{config.get('prefix', '$')}start` to begin your RPG adventure!\n"
                                 f"🧀 I'm Plagg, and I'm here to cause some fun chaos!\n\n"
                                 f"💡 *Ask me any questions about the game by mentioning @Plagg!*")

                embed = create_embed(
                    f"Welcome to {member.guild.name}!",
                    description,
                    COLORS['success']
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text="Ready to explore? The cheese awaits! 🧀")
                await welcome_channel.send(embed=embed)
    except Exception as e:
        logger.error(f"Error handling member join: {e}")

async def load_cogs():
    """Load all cogs."""
    cogs = [
        'cogs.admin',
        'cogs.moderation',
        'cogs.rpg_games',
        'cogs.ai_chatbot',
        'cogs.help'
    ]

    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logger.info(f"Loaded cog: {cog}")
        except Exception as e:
            logger.error(f"Failed to load cog {cog}: {e}")

async def main():
    """Main function to run the bot."""
    # Start web server in a separate thread
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # Load cogs
    await load_cogs()

    # Get token from environment
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        return

    # Run the bot
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())