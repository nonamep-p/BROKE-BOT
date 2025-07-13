import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Dict, Any
import logging

from config import COLORS, get_server_config, is_module_enabled
from utils.helpers import create_embed

logger = logging.getLogger(__name__)

class HelpView(discord.ui.View):
    """Interactive help view with category selection."""

    def __init__(self, bot, user: discord.Member):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.current_category = "main"

    @discord.ui.select(
        placeholder="Select a command category...",
        options=[
            discord.SelectOption(label="Main Commands", value="main", emoji="🏠"),
            discord.SelectOption(label="RPG Games", value="rpg", emoji="⚔️"),
            discord.SelectOption(label="Moderation", value="moderation", emoji="🛡️"),
            discord.SelectOption(label="AI Chatbot", value="ai", emoji="🤖"),
            discord.SelectOption(label="Admin", value="admin", emoji="⚙️")
        ]
    )
    async def category_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Change help category."""
        if interaction.user != self.user:
            await interaction.response.send_message("This help menu is not for you!", ephemeral=True)
            return

        self.current_category = select.values[0]
        embed = self.create_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def create_help_embed(self) -> discord.Embed:
        """Create help embed for current category."""
        embed = discord.Embed(
            title=f"📚 Help - {self.current_category.title()}",
            color=COLORS['primary']
        )

        if self.current_category == "main":
            embed.description = "Basic bot commands and information"
            embed.add_field(
                name="📋 General Commands",
                value="• `/help` - Show this help menu\n"
                      "• `/start` - Start your RPG adventure\n"
                      "• `/profile` - View your character profile\n"
                      "• `/config` - Server configuration (Admin only)",
                inline=False
            )

        elif self.current_category == "rpg":
            embed.description = "🎮 **Epic RPG System** - 6 classes, 30+ weapons, hidden mechanics & mythic content!"
            rpg_embed = embed
            embed.add_field(
                name="🎯 Getting Started",
                value="• `/start` - Begin your RPG adventure\n"
                      "• `/profile` - View detailed character stats\n"
                      "• `$class <name>` - Choose your class:\n"
                      "  ◦ **Warrior** (Cheese Guardian) - Tank & melee\n"
                      "  ◦ **Mage** (Kwami Sorcerer) - Magic & spells\n"
                      "  ◦ **Rogue** (Shadow Cat) - Stealth & crits\n"
                      "  ◦ **Archer** (Cheese Hunter) - Ranged combat\n"
                      "  ◦ **Healer** (Tikki Disciple) - Support & healing\n"
                      "  ◦ **Chrono Weave** (Hidden) - Time manipulation\n"
                      "• `$skills` - View your class abilities\n"
                      "• `$heal` - Restore health (50 coins)",
                inline=False
            )
            embed.add_field(
                name="⚔️ Weapons & Equipment System",
                value="**🗡️ Class-Specific Weapons (30+ total):**\n"
                      "• **Warrior:** Iron Petal, Stump Cleave, Wooden Round\n"
                      "• **Mage:** Sprintling, Ashen Quill, Tome of Flare\n"
                      "• **Rogue:** Shiny Slicer, Whispering Curve, Stinger Vial\n"
                      "• **Archer:** Sylvan Edge, Thunderpop, Ethereal Tip\n"
                      "• **Healer:** Elder's Pulse, Nectar of Lifespan, Eternal Glow\n"
                      "• **Chrono Weave:** Timekeeper's Edge, Chrono Tap, Echo of Eternity\n\n"
                      "**🌟 Mythic Weapons:**\n"
                      "• **The Last Echo** - Ultimate weapon (requires boss defeat)\n"
                      "• **The Paradox Core** - Reality-bending weapon\n"
                      "• **World Ender** - One-shot kill weapon (Omnipotent)\n"
                      "• **Reality Stone** - Grants any item except World Ender\n\n"
                      "**📋 Equipment Commands:**\n"
                      "• `$inventory` - View all items\n"
                      "• `$equip <item>` - Equip weapons/armor\n"
                      "• `$rarity <item>` - Check item details & rarity\n"
                      "• `$use <item>` - Use consumables\n"
                      "• `$buy <item>` - Purchase specific items",
                inline=False
            )
            embed.add_field(
                name="🗺️ Adventures & Combat",
                value="• `$adventure` - Interactive location explorer\n"
                      "• `$work` - Earn coins through jobs\n"
                      "• `$battle` - Fight monsters with strategy\n"
                      "• `$dungeon` - Multi-floor dungeon raids\n"
                      "• `$pvp <user> <arena>` - Player vs Player combat\n"
                      "• `$party create/invite/leave` - Form raid groups\n"
                      "• `$daily` - Claim daily streak rewards\n"
                      "• `$balance` - Check your coin balance\n"
                      "• `$pay <user> <amount>` - Transfer coins",
                inline=False
            )
            embed.add_field(
                name="🔨 Crafting & Professions",
                value="• `$profession <name>` - Unlock crafting:\n"
                      "  ◦ **Blacksmith** (Miraculous Forger)\n"
                      "  ◦ **Alchemist** (Potion Master)\n"
                      "  ◦ **Enchanter** (Kwami Enchanter)\n"
                      "• `$craft <recipe>` - Create powerful items\n"
                      "• `$gather <location>` - Collect materials\n"
                      "• `$materials` - View crafting resources\n"
                      "• **Recipes:** Cheese Sword, Camembert Armor, Kwami Potions",
                inline=False
            )
            rpg_embed.add_field(
                name="🛒 Economy & Items",
                value="`$shop` - View the shop\n"
                      "`$buy <item>` - Purchase an item\n"
                      "`$inventory` - View your items\n"
                      "`$sell <item>` - Sell an item\n"
                      "`$work` - Work for coins\n"
                      "`$reload_shop` - Reload shop data (Admin)",
                inline=False
            )
            embed.add_field(
                name="🏛️ Economy & Trading",
                value="• `$shop` - Browse comprehensive item marketplace\n"
                      "• `$shop <category>` - View weapons, armor, consumables\n"
                      "• `$shop <class>` - Class-specific weapon listings\n"
                      "• `$buy <item>` - Purchase specific items\n"
                      "• `$auction list/sell/bid` - Player-driven economy\n"
                      "• `$trade <user>` - Direct item trading\n"
                      "• `$lootbox` - Open for random rewards\n"
                      "• **Categories:** weapons, armor, consumables, mythic",
                inline=False
            )
            embed.add_field(
                name="📜 Quests & Progression",
                value="• `$quest new/abandon` - Dynamic quest system\n"
                      "• `$quests` - View active quest journal\n"
                      "• `$faction <name>` - Join factions:\n"
                      "  ◦ **Miraculous Order** (Good alignment)\n"
                      "  ◦ **Butterfly Syndicate** (Evil alignment)\n"
                      "  ◦ **Cheese Guild** (Neutral alignment)\n"
                      "• `$legacy` - View achievements & titles\n"
                      "• `$prestige` - Reset character for bonuses\n"
                      "• `$leaderboard <category>` - Server rankings",
                inline=False
            )
            embed.add_field(
                name="🎮 Mini-Games & Special Features",
                value="• `$fish` - Fish in magical cheese ponds for pets\n"
                      "• `$trivia` - Plagg's cheese knowledge challenges\n"
                      "• **Seasonal Events:** Cheese storms, kwami invasions\n"
                      "• **World Bosses:** Camembert Colossus (10+ players)\n"
                      "• **PvP Arenas:** Cheese Pit, Miraculous Colosseum\n"
                      "• **Time-Based:** In-game seasons affect gameplay",
                inline=False
            )
            embed.add_field(
                name="🌟 Hidden & Endgame Content",
                value="**🕐 Chrono Weave Class Unlock:**\n"
                      "• Defeat Time Rift Dragon while level ≤30\n"
                      "• Complete Chrono Whispers quest\n"
                      "• Collect 3 Ancient Relics (Past/Future/Present)\n\n"
                      "**⚡ Special Abilities:**\n"
                      "• Time Reversal (3-day cooldown)\n"
                      "• Temporal Surge (crit & XP boost)\n"
                      "• Chrono Immunity (debuff resistance)\n\n"
                      "**🎯 Mythic Weapon Unlocks:**\n"
                      "• The Last Echo: Defeat Paradox Boss at <25% HP\n"
                      "• Paradox Core: Complete 10-floor Paradox Chamber\n"
                      "• World Ender: Ultra-rare lootbox drop (0.01%)\n"
                      "• Reality Stone: Wish for any item",
                inline=False
            )
            embed.add_field(
                name="📊 Rarity System",
                value="⚪ **Common** (50%) → 🟢 **Uncommon** (25%) → 🔵 **Rare** (15%)\n"
                      "🟣 **Epic** (7%) → 🟠 **Legendary** (2.5%) → 🔴 **Mythic** (0.4%)\n"
                      "🟡 **Divine** (0.1%) → 💖 **Omnipotent** (0.01%)",
                inline=False
            )
            embed.set_footer(text="🚀 Start: /start → Choose class → $adventure → Unlock your destiny!")

        elif self.current_category == "moderation":
            embed.description = "Moderation tools for server management"
            embed.add_field(
                name="🛡️ Moderation Commands",
                value="• `/kick` - Kick a member\n"
                      "• `/ban` - Ban a member\n"
                      "• `/warn` - Warn a member\n"
                      "• `/warnings` - View user warnings\n"
                      "• `/purge` - Delete multiple messages\n"
                      "• `/timeout` - Timeout a member\n"
                      "• `/lock` - Lock a channel\n"
                      "• `/unlock` - Unlock a channel\n"
                      "• `/slowmode` - Set channel slowmode\n"
                      "• `/clear_warns` - Clear user warnings",
                inline=False
            )

        elif self.current_category == "ai":
            embed.description = "AI chatbot features for conversation"
            embed.add_field(
                name="🤖 AI Commands",
                value="• `/chat` - Chat with AI\n"
                      "• `/clear_chat` - Clear chat history\n"
                      "• `/ai_status` - Check AI system status\n"
                      "• **Auto-Response** - Just mention me!\n"
                      "• **Context Memory** - I remember our chats\n"
                      "• **Plagg Personality** - Sarcastic and fun responses\n"
                      "• **Natural Language** - Chat like with a friend",
                inline=False
            )

        elif self.current_category == "admin":
            embed.description = "Administrative commands for server owners"
            embed.add_field(
                name="⚙️ Admin Commands",
                value="• `/config` - Interactive server configuration\n"
                      "• `/stats` - View bot statistics\n"
                      "• `/reload` - Reload bot modules\n"
                      "• `/sync` - Sync slash commands\n"
                      "• `/backup` - Backup server data\n"
                      "• `/restore` - Restore server data\n"
                      "• `/reset_user` - Reset user progress\n"
                      "• `/announce` - Send announcements",
                inline=False
            )

        embed.set_footer(text="Use the dropdown menu to browse different categories")
        return embed

class HelpCog(commands.Cog):
    """Help system for the bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', help='Show help information')
    async def help_command(self, ctx, category: Optional[str] = None):
        """Show help information."""
        view = HelpView(self.bot, ctx.author)
        embed = view.create_help_embed()
        await ctx.send(embed=embed, view=view)

    @app_commands.command(name="help", description="Show help information")
    @app_commands.describe(category="Specific category to view (optional)")
    async def help_slash(self, interaction: discord.Interaction, category: Optional[str] = None):
        """Show help information (slash command)."""
        view = HelpView(self.bot, interaction.user)

        if category:
            valid_categories = ["main", "rpg", "moderation", "ai", "admin"]
            if category.lower() in valid_categories:
                view.current_category = category.lower()

        embed = view.create_help_embed()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="info", description="Show bot information")
    async def info_slash(self, interaction: discord.Interaction):
        """Show bot information."""
        embed = discord.Embed(
            title="🧀 Plagg - AI Chatbot with Game Features",
            description="A comprehensive Discord bot with AI chatbot as the main feature and game features!",
            color=COLORS['primary']
        )

        embed.add_field(
            name="🤖 Main Feature - AI Chat",
            value="• **Smart Conversations** - Just mention me!\n"
                  "• **Plagg's Personality** - Sarcastic and fun\n"
                  "• **Context Memory** - Remembers our chats\n"
                  "• **Google Gemini** - Advanced AI responses\n"
                  "• **Natural Language** - Chat like with a friend",
            inline=True
        )

        embed.add_field(
            name="🎮 Epic RPG Features",
            value="• **6 Classes** - Including hidden Chrono Weave\n"
                  "• **30+ Weapons** - Class-specific with rarities\n"
                  "• **Mythic Items** - The Last Echo, Paradox Core\n"
                  "• **Special Bosses** - Time dragons & void lords\n"
                  "• **Secret Dungeons** - Paradox chambers & rifts",
            inline=True
        )

        embed.add_field(
            name="📈 Statistics",
            value=f"• Guilds: {len(self.bot.guilds)}\n"
                  f"• Users: {len(self.bot.users)}\n"
                  f"• Commands: {len(self.bot.commands)}\n"
                  f"• Slash Commands: {len(self.bot.tree.get_commands())}\n"
                  f"• Latency: {round(self.bot.latency * 1000, 2)}ms",
            inline=True
        )

        embed.add_field(
            name="🔗 Links",
            value="• [Support Server](https://discord.gg/your-server)\n"
                  "• [Invite Bot](https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=8&scope=bot%20applications.commands)\n"
                  "• [GitHub](https://github.com/your-repo)",
            inline=False
        )

        embed.set_footer(text="Made by NoNameP_P | Use /help to see all available commands")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(HelpCog(bot))