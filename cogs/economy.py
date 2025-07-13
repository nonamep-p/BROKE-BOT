import discord
from discord.ext import commands
from discord import app_commands
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from config import COLORS, EMOJIS, get_server_config, is_module_enabled, user_has_permission
from utils.helpers import create_embed, format_number, get_random_work_job, format_time_remaining, get_time_until_next_use
from utils.database import get_user_rpg_data, update_user_rpg_data, ensure_user_exists
from utils.constants import RPG_CONSTANTS, SHOP_ITEMS, DAILY_REWARDS
from utils.rng_system import generate_loot_with_luck
from replit import db

logger = logging.getLogger(__name__)

class ShopView(discord.ui.View):
    """Interactive shop view."""

    def __init__(self, user_id: str):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.current_category = 'weapons'

    @discord.ui.select(
        placeholder="Select item category...",
        options=[
            discord.SelectOption(label="Weapons", value="weapons", emoji="⚔️"),
            discord.SelectOption(label="Armor", value="armor", emoji="🛡️"),
            discord.SelectOption(label="Consumables", value="consumables", emoji="🧪")
        ]
    )
    async def category_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Change shop category."""
        self.current_category = select.values[0]
        embed = self.create_shop_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def create_shop_embed(self) -> discord.Embed:
        """Create shop embed for current category."""
        embed = discord.Embed(
            title=f"🏪 Shop - {self.current_category.title()}",
            description="Buy items to enhance your adventure!",
            color=COLORS['warning']
        )

        items = SHOP_ITEMS.get(self.current_category, {})
        for name, data in list(items.items())[:10]:  # Show first 10 items
            price = data.get('price', 0)
            rarity = data.get('rarity', 'common')

            # Build stats text
            stats = []
            if 'attack' in data:
                stats.append(f"ATK: {data['attack']}")
            if 'defense' in data:
                stats.append(f"DEF: {data['defense']}")
            if 'heal' in data:
                stats.append(f"Heal: {data['heal']}")

            stats_text = " | ".join(stats) if stats else "No stats"

            embed.add_field(
                name=f"{name} ({rarity})",
                value=f"💰 {format_number(price)} coins\n{stats_text}",
                inline=True
            )

        return embed

class EconomyCog(commands.Cog):
    """Economy system for the bot."""

    def __init__(self, bot):
        self.bot = bot

    # Work command moved to RPG cog to avoid duplication

    @app_commands.command(name="work", description="Work to earn coins")
    async def work_slash(self, interaction: discord.Interaction):
        """Work to earn coins (slash command)."""
        if not is_module_enabled("economy", interaction.guild.id):
            await interaction.response.send_message("❌ Economy module is disabled!", ephemeral=True)
            return

        user_id = str(interaction.user.id)

        if not ensure_user_exists(user_id):
            await interaction.response.send_message("❌ You need to start your adventure first!", ephemeral=True)
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await interaction.response.send_message("❌ Could not retrieve your data. Please try again.", ephemeral=True)
            return

        # Get random job
        job = get_random_work_job()
        base_coins = random.randint(job["min_coins"], job["max_coins"])
        base_xp = random.randint(job["min_xp"], job["max_xp"])

        # Apply luck bonuses
        enhanced_loot = generate_loot_with_luck(user_id, {
            'coins': base_coins,
            'xp': base_xp
        })

        coins_earned = enhanced_loot['coins']
        xp_earned = enhanced_loot['xp']

        # Update player data
        player_data['coins'] = player_data.get('coins', 0) + coins_earned
        player_data['xp'] = player_data.get('xp', 0) + xp_earned
        player_data['work_count'] = player_data.get('work_count', 0) + 1

        update_user_rpg_data(user_id, player_data)

        embed = create_embed(
            f"💼 Work Complete - {job['name']}",
            f"You earned **{format_number(coins_earned)}** coins and **{xp_earned}** XP!",
            COLORS['success']
        )

        await interaction.response.send_message(embed=embed)

    @commands.command(name='daily', help='Claim your daily reward')
    @commands.cooldown(1, RPG_CONSTANTS['daily_cooldown'], commands.BucketType.user)
    async def daily_command(self, ctx):
        """Claim daily reward."""
        if not is_module_enabled("economy", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data. Please try again.")
            return

        # Calculate daily reward
        base_reward = DAILY_REWARDS['base']
        level_bonus = player_data.get('level', 1) * DAILY_REWARDS['level_multiplier']
        streak_bonus = min(player_data.get('daily_streak', 0), DAILY_REWARDS['max_streak']) * DAILY_REWARDS['streak_bonus']

        total_coins = base_reward + level_bonus + streak_bonus
        total_xp = int(total_coins * 0.5)  # XP is half of coins

        # Update player data
        player_data['coins'] = player_data.get('coins', 0) + total_coins
        player_data['xp'] = player_data.get('xp', 0) + total_xp
        player_data['daily_streak'] = player_data.get('daily_streak', 0) + 1

        update_user_rpg_data(user_id, player_data)

        embed = create_embed(
            "🎁 Daily Reward Claimed!",
            f"**Coins:** {format_number(total_coins)}\n"
            f"**XP:** {total_xp}\n"
            f"**Streak:** {player_data['daily_streak']} days",
            COLORS['success']
        )

        await ctx.send(embed=embed)

    @app_commands.command(name="daily", description="Claim your daily reward")
    async def daily_slash(self, interaction: discord.Interaction):
        """Claim daily reward (slash command)."""
        if not is_module_enabled("economy", interaction.guild.id):
            await interaction.response.send_message("❌ Economy module is disabled!", ephemeral=True)
            return

        user_id = str(interaction.user.id)

        if not ensure_user_exists(user_id):
            await interaction.response.send_message("❌ You need to start your adventure first!", ephemeral=True)
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await interaction.response.send_message("❌ Could not retrieve your data. Please try again.", ephemeral=True)
            return

        # Calculate daily reward
        base_reward = DAILY_REWARDS['base']
        level_bonus = player_data.get('level', 1) * DAILY_REWARDS['level_multiplier']
        streak_bonus = min(player_data.get('daily_streak', 0), DAILY_REWARDS['max_streak']) * DAILY_REWARDS['streak_bonus']

        total_coins = base_reward + level_bonus + streak_bonus
        total_xp = int(total_coins * 0.5)  # XP is half of coins

        # Update player data
        player_data['coins'] = player_data.get('coins', 0) + total_coins
        player_data['xp'] = player_data.get('xp', 0) + total_xp
        player_data['daily_streak'] = player_data.get('daily_streak', 0) + 1

        update_user_rpg_data(user_id, player_data)

        embed = create_embed(
            "🎁 Daily Reward Claimed!",
            f"**Coins:** {format_number(total_coins)}\n"
            f"**XP:** {total_xp}\n"
            f"**Streak:** {player_data['daily_streak']} days",
            COLORS['success']
        )

        await interaction.response.send_message(embed=embed)

    @commands.command(name='shop', help='Browse the item shop')
    async def shop_command(self, ctx):
        """Browse the item shop."""
        if not is_module_enabled("economy", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        view = ShopView(user_id)
        embed = view.create_shop_embed()

        await ctx.send(embed=embed, view=view)

    @app_commands.command(name="shop", description="Browse the item shop")
    async def shop_slash(self, interaction: discord.Interaction):
        """Browse the item shop (slash command)."""
        if not is_module_enabled("economy", interaction.guild.id):
            await interaction.response.send_message("❌ Economy module is disabled!", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        view = ShopView(user_id)
        embed = view.create_shop_embed()

        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name='balance', help='Check your coin balance')
    async def balance_command(self, ctx, member: Optional[discord.Member] = None):
        """Check coin balance."""
        if not is_module_enabled("economy", ctx.guild.id):
            return

        target = member or ctx.author
        user_id = str(target.id)

        if not ensure_user_exists(user_id):
            await ctx.send(f"❌ {target.display_name} hasn't started their adventure yet!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve data.")
            return

        coins = player_data.get('coins', 0)
        level = player_data.get('level', 1)

        embed = create_embed(
            f"💰 {target.display_name}'s Wallet",
            f"**Coins:** {format_number(coins)}\n"
            f"**Level:** {level}",
            COLORS['warning']
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        await ctx.send(embed=embed)

    @app_commands.command(name="balance", description="Check your coin balance")
    @app_commands.describe(member="User to check balance for (optional)")
    async def balance_slash(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """Check coin balance (slash command)."""
        if not is_module_enabled("economy", interaction.guild.id):
            await interaction.response.send_message("❌ Economy module is disabled!", ephemeral=True)
            return

        target = member or interaction.user
        user_id = str(target.id)

        if not ensure_user_exists(user_id):
            await interaction.response.send_message(f"❌ {target.display_name} hasn't started their adventure yet!", ephemeral=True)
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await interaction.response.send_message("❌ Could not retrieve data.", ephemeral=True)
            return

        coins = player_data.get('coins', 0)
        level = player_data.get('level', 1)

        embed = create_embed(
            f"💰 {target.display_name}'s Wallet",
            f"**Coins:** {format_number(coins)}\n"
            f"**Level:** {level}",
            COLORS['warning']
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(EconomyCog(bot))