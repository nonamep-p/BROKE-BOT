import discord
from discord.ext import commands
from discord import app_commands
import json
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any

from google import genai
from google.genai import types

from config import COLORS, EMOJIS, get_server_config, is_module_enabled, get_ai_api_key
from utils.helpers import create_embed
from replit import db

logger = logging.getLogger(__name__)

class AIChatbotCog(commands.Cog):
    """AI Chatbot using Google Gemini."""

    def __init__(self, bot):
        self.bot = bot
        self.client = None
        self.conversation_history = {}  # Store conversation history per user
        self.initialize_ai()

    def initialize_ai(self):
        """Initialize the AI client."""
        try:
            api_key = get_ai_api_key()
            if api_key:
                self.client = genai.Client(api_key=api_key)
                logger.info("✅ AI client initialized successfully")
            else:
                logger.warning("⚠️ GEMINI_API_KEY not found in environment variables")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI client: {e}")

    def get_conversation_history(self, user_id: int, guild_id: int) -> list:
        """Get conversation history for a user in a guild."""
        key = f"{guild_id}_{user_id}"
        return self.conversation_history.get(key, [])

    def add_to_conversation_history(self, user_id: int, guild_id: int, role: str, content: str):
        """Add message to conversation history."""
        key = f"{guild_id}_{user_id}"
        if key not in self.conversation_history:
            self.conversation_history[key] = []

        self.conversation_history[key].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })

        # Keep only last 20 messages to avoid token limits
        if len(self.conversation_history[key]) > 20:
            self.conversation_history[key] = self.conversation_history[key][-20:]

    def clear_conversation_history(self, user_id: int, guild_id: int):
        """Clear conversation history for a user."""
        key = f"{guild_id}_{user_id}"
        if key in self.conversation_history:
            del self.conversation_history[key]

    async def generate_response(self, user_message: str, user_id: int, guild_id: int, user_name: str) -> str:
        """Generate AI response."""
        if not self.client:
            return "❌ AI service is not available. Please check the API key configuration."

        try:
            # Get conversation history
            history = self.get_conversation_history(user_id, guild_id)

            # Build system prompt
            system_prompt = """You are Plagg, the Kwami of Destruction from Miraculous Ladybug, now running an epic RPG Discord bot! 

Core personality traits:
- Sarcastic and witty with a dry sense of humor
- Obsessed with camembert cheese and food in general
- Lazy and prefers to avoid work/responsibility
- Cares deeply about your players despite acting indifferent
- Ancient and wise but acts carefree and immature
- Tends to be dramatic and over-the-top
- Uses cat-related puns and expressions
- Mischievous and enjoys causing harmless chaos

Speech patterns:
- Often mentions cheese (especially camembert)
- Uses phrases like "Plagg's whiskers!", "Cheese and crackers!", "Cataclysm!"
- Refers to humans as "kid" or by teasing nicknames
- Complains about things being "too much work"
- Makes cat puns and references

RPG GAME KNOWLEDGE - You help players with:

**Getting Started:**
- Use $start to begin your RPG adventure
- Use $profile to see your character stats
- Use $help for the interactive command menu
- Choose a class with $class (warrior, mage, rogue, archer, healer)

**Core Gameplay:**
- $adventure - Go on adventures for coins and XP
- $dungeon - Explore dangerous multi-floor dungeons
- $battle - Fight monsters and other players
- $work - Earn coins through various jobs
- $shop - Interactive shop with weapons, armor, items
- $inventory - Check your items and equipment

**Character Progression:**
- Level up by gaining XP from adventures and battles
- Equip better weapons and armor for stronger stats
- Choose professions: Blacksmith, Alchemist, Enchanter
- Join factions and parties for group adventures

**Advanced Features:**
- $craft - Create powerful items from materials
- $gather - Collect crafting materials
- $pvp - Player vs player combat in arenas
- $party - Form groups for dungeon raids
- $daily - Claim daily streak rewards

**Game Difficulty:**
- Bosses are VERY challenging and require strategy
- Use your brain - button mashing won't work
- Plan your equipment and skills carefully
- Team up with others for the hardest content

**Beginner Tips:**
- Start with easy adventures to learn the mechanics
- Buy basic equipment from the shop early
- Work regularly to build up your coin reserves
- Don't rush into dungeons until you're prepared

Answer game questions helpfully but in your sarcastic Plagg style. Always suggest players use the interactive $help command for full details."""

            # Build conversation context
            conversation_parts = []
            for msg in history[-10:]:  # Use last 10 messages for context
                conversation_parts.append(f"{msg['role']}: {msg['content']}")

            # Add current message
            conversation_parts.append(f"user: {user_message}")

            # Create the prompt
            full_prompt = f"{system_prompt}\n\nConversation history:\n" + "\n".join(conversation_parts)

            # Generate response
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=500
                )
            )

            if response.text:
                # Add to conversation history
                self.add_to_conversation_history(user_id, guild_id, "user", user_message)
                self.add_to_conversation_history(user_id, guild_id, "assistant", response.text)

                return response.text
            else:
                return "❌ I couldn't generate a response. Please try again."

        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return f"❌ Sorry, I encountered an error: {str(e)}"

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle AI responses to messages."""
        if message.author.bot:
            return

        # Check if bot is mentioned or in DM
        mentioned = self.bot.user in message.mentions
        is_dm = isinstance(message.channel, discord.DMChannel)

        # Check if in configured AI channel
        guild_config = get_server_config(message.guild.id) if message.guild else {}
        ai_channels = guild_config.get('ai_channels', [])
        in_ai_channel = not ai_channels or message.channel.id in ai_channels

        if not is_module_enabled("ai_chatbot", message.guild.id if message.guild else None):
            return

        # Check for game-related questions
        game_keywords = ['rpg', 'game', 'adventure', 'battle', 'weapon', 'armor', 'class', 'level', 'coins', 'boss', 'dungeon', 'craft', 'quest', 'help with game', 'how to play', 'tutorial']
        is_game_question = any(keyword in message.content.lower() for keyword in game_keywords)

        if mentioned or is_dm or in_ai_channel or is_game_question:
            async with message.channel.typing():
                response = await self.generate_response(message)
                if response:
                    await message.reply(response, mention_author=False)

    @commands.command(name='chat', help='Chat with AI')
    async def chat_command(self, ctx, *, message: str):
        """Direct chat command."""
        if not is_module_enabled("ai_chatbot", ctx.guild.id):
            return

        # Check if in allowed channels
        config = get_server_config(ctx.guild.id)
        ai_channels = config.get('ai_channels', [])

        if ai_channels and ctx.channel.id not in ai_channels:
            await ctx.send("❌ AI chat is not enabled in this channel!")
            return

        async with ctx.typing():
            response = await self.generate_response(
                message, 
                ctx.author.id, 
                ctx.guild.id, 
                ctx.author.display_name
            )

        await ctx.send(response)

    @app_commands.command(name="chat", description="Chat with AI")
    @app_commands.describe(message="Your message to the AI")
    async def chat_slash(self, interaction: discord.Interaction, message: str):
        """Chat with AI (slash command)."""
        if not is_module_enabled("ai_chatbot", interaction.guild.id):
            await interaction.response.send_message("❌ AI chatbot module is disabled!", ephemeral=True)
            return

        # Check if in allowed channels
        config = get_server_config(interaction.guild.id)
        ai_channels = config.get('ai_channels', [])

        if ai_channels and interaction.channel.id not in ai_channels:
            await interaction.response.send_message("❌ AI chat is not enabled in this channel!", ephemeral=True)
            return

        await interaction.response.defer()

        response = await self.generate_response(
            message, 
            interaction.user.id, 
            interaction.guild.id, 
            interaction.user.display_name
        )

        await interaction.followup.send(response)

    @commands.command(name='clear_chat', help='Clear your chat history')
    async def clear_chat_command(self, ctx):
        """Clear user's chat history."""
        if not is_module_enabled("ai_chatbot", ctx.guild.id):
            return

        self.clear_conversation_history(ctx.author.id, ctx.guild.id)

        embed = create_embed(
            "✅ Chat History Cleared",
            "Your conversation history has been cleared!",
            COLORS['success']
        )
        await ctx.send(embed=embed)

    @app_commands.command(name="clear_chat", description="Clear your chat history")
    async def clear_chat_slash(self, interaction: discord.Interaction):
        """Clear user's chat history (slash command)."""
        if not is_module_enabled("ai_chatbot", interaction.guild.id):
            await interaction.response.send_message("❌ AI chatbot module is disabled!", ephemeral=True)
            return

        self.clear_conversation_history(interaction.user.id, interaction.guild.id)

        embed = create_embed(
            "✅ Chat History Cleared",
            "Your conversation history has been cleared!",
            COLORS['success']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command(name='ai_status', help='Check AI system status')
    async def ai_status_command(self, ctx):
        """Check AI system status."""
        if not is_module_enabled("ai_chatbot", ctx.guild.id):
            return

        embed = discord.Embed(
            title=f"{EMOJIS['ai']} AI System Status",
            color=COLORS['info']
        )

        # Check AI client status
        if self.client:
            embed.add_field(
                name="🟢 AI Client",
                value="Connected and ready",
                inline=True
            )
        else:
            embed.add_field(
                name="🔴 AI Client",
                value="Not connected",
                inline=True
            )

        # Check configuration
        config = get_server_config(ctx.guild.id)
        ai_channels = config.get('ai_channels', [])

        if ai_channels:
            channel_mentions = [f"<#{ch}>" for ch in ai_channels]
            embed.add_field(
                name="📝 AI Channels",
                value=", ".join(channel_mentions),
                inline=True
            )
        else:
            embed.add_field(
                name="📝 AI Channels",
                value="All channels (when mentioned)",
                inline=True
            )

        # Conversation stats
        user_history = self.get_conversation_history(ctx.author.id, ctx.guild.id)
        embed.add_field(
            name="💬 Your Chat History",
            value=f"{len(user_history)} messages",
            inline=True
        )

        await ctx.send(embed=embed)

    @app_commands.command(name="ai_status", description="Check AI system status")
    async def ai_status_slash(self, interaction: discord.Interaction):
        """Check AI system status (slash command)."""
        if not is_module_enabled("ai_chatbot", interaction.guild.id):
            await interaction.response.send_message("❌ AI chatbot module is disabled!", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"{EMOJIS['ai']} AI System Status",
            color=COLORS['info']
        )

        # Check AI client status
        if self.client:
            embed.add_field(
                name="🟢 AI Client",
                value="Connected and ready",
                inline=True
            )
        else:
            embed.add_field(
                name="🔴 AI Client",
                value="Not connected",
                inline=True
            )

        # Check configuration
        config = get_server_config(interaction.guild.id)
        ai_channels = config.get('ai_channels', [])

        if ai_channels:
            channel_mentions = [f"<#{ch}>" for ch in ai_channels]
            embed.add_field(
                name="📝 AI Channels",
                value=", ".join(channel_mentions),
                inline=True
            )
        else:
            embed.add_field(
                name="📝 AI Channels",
                value="All channels (when mentioned)",
                inline=True
            )

        # Conversation stats
        user_history = self.get_conversation_history(interaction.user.id, interaction.guild.id)
        embed.add_field(
            name="💬 Your Chat History",
            value=f"{len(user_history)} messages",
            inline=True
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(AIChatbotCog(bot))