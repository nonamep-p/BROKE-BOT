import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

from config import COLORS, EMOJIS, get_server_config, is_module_enabled
from utils.helpers import create_embed, format_number, create_progress_bar
from utils.database import get_user_rpg_data, update_user_rpg_data, ensure_user_exists, create_user_profile, get_leaderboard
from utils.constants import RPG_CONSTANTS, WEAPONS, ARMOR, RARITY_COLORS, RARITY_WEIGHTS, PVP_ARENAS, OMNIPOTENT_ITEM
from utils.rng_system import roll_with_luck, check_rare_event, get_luck_status, generate_loot_with_luck, weighted_random_choice
from replit import db

logger = logging.getLogger(__name__)

def level_up_player(player_data):
    """Check and handle level ups."""
    current_level = player_data.get('level', 1)
    current_xp = player_data.get('xp', 0)

    # Calculate XP needed for next level
    base_xp = 100
    xp_needed = int(base_xp * (1.5 ** (current_level - 1)))

    if current_xp >= xp_needed:
        # Level up!
        new_level = current_level + 1
        remaining_xp = current_xp - xp_needed

        # Update stats
        player_data['level'] = new_level
        player_data['xp'] = remaining_xp
        player_data['max_xp'] = int(base_xp * (1.5 ** (new_level - 1)))

        # Increase stats
        player_data['max_hp'] = player_data.get('max_hp', 100) + 10
        player_data['hp'] = player_data.get('max_hp', 100)  # Full heal on level up
        player_data['attack'] = player_data.get('attack', 10) + 2
        player_data['defense'] = player_data.get('defense', 5) + 1

        return f"🎉 Level {new_level}! HP+10, ATK+2, DEF+1"

    player_data['max_xp'] = xp_needed
    return None

def get_random_adventure_outcome():
    """Get a random adventure outcome."""
    outcomes = [
        {
            'description': 'You discovered a hidden treasure chest!',
            'coins': (50, 150),
            'xp': (20, 50),
            'items': ['Health Potion', 'Iron Sword', 'Leather Armor']
        },
        {
            'description': 'You defeated a group of bandits!',
            'coins': (30, 100),
            'xp': (15, 40),
            'items': ['Health Potion', 'Lucky Charm']
        },
        {
            'description': 'You helped a merchant and received a reward!',
            'coins': (40, 120),
            'xp': (10, 30),
            'items': ['Health Potion', 'Iron Sword']
        },
        {
            'description': 'You found rare materials while exploring!',
            'coins': (20, 80),
            'xp': (25, 60),
            'items': ['Health Potion', 'Lucky Charm', 'Iron Sword']
        }
    ]
    return random.choice(outcomes)

def calculate_battle_damage(attack, defense):
    """Calculate battle damage."""
    base_damage = max(1, attack - defense)
    # Add some randomness
    damage = random.randint(int(base_damage * 0.8), int(base_damage * 1.2))
    return max(1, damage)

class ProfileView(discord.ui.View):
    """Interactive profile view."""

    def __init__(self, user: discord.Member, player_data: Dict[str, Any]):
        super().__init__(timeout=300)
        self.user = user
        self.player_data = player_data
        self.current_page = "stats"

    @discord.ui.button(label="📊 Stats", style=discord.ButtonStyle.primary)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show player stats."""
        if interaction.user != self.user:
            await interaction.response.send_message("This is not your profile!", ephemeral=True)
            return

        embed = self.create_stats_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🎒 Inventory", style=discord.ButtonStyle.secondary)
    async def inventory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show player inventory."""
        if interaction.user != self.user:
            await interaction.response.send_message("This is not your profile!", ephemeral=True)
            return

        embed = self.create_inventory_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🍀 Luck", style=discord.ButtonStyle.success)
    async def luck_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show player luck status."""
        if interaction.user != self.user:
            await interaction.response.send_message("This is not your profile!", ephemeral=True)
            return

        embed = self.create_luck_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def create_stats_embed(self) -> discord.Embed:
        """Create stats embed."""
        level = self.player_data.get('level', 1)
        xp = self.player_data.get('xp', 0)
        max_xp = self.player_data.get('max_xp', 100)
        hp = self.player_data.get('hp', 100)
        max_hp = self.player_data.get('max_hp', 100)
        attack = self.player_data.get('attack', 10)
        defense = self.player_data.get('defense', 5)
        coins = self.player_data.get('coins', 0)

        # Calculate XP percentage
        xp_percent = (xp / max_xp) * 100 if max_xp > 0 else 0
        hp_percent = (hp / max_hp) * 100 if max_hp > 0 else 0

        embed = discord.Embed(
            title=f"📊 {self.user.display_name}'s Profile",
            color=COLORS['primary']
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)

        embed.add_field(
            name="📊 Level & Experience",
            value=f"**Level:** {level}\n"
                  f"**XP:** {xp:,}/{max_xp:,}\n"
                  f"{create_progress_bar(xp_percent)}",
            inline=True
        )

        embed.add_field(
            name="❤️ Health",
            value=f"**HP:** {hp}/{max_hp}\n"
                  f"{create_progress_bar(hp_percent)}",
            inline=True
        )

        embed.add_field(
            name="💰 Wealth",
            value=f"**Coins:** {format_number(coins)}",
            inline=True
        )

        embed.add_field(
            name="⚔️ Combat Stats",
            value=f"**Attack:** {attack}\n"
                  f"**Defense:** {defense}",
            inline=True
        )

        # Stats
        stats = self.player_data.get('stats', {})
        embed.add_field(
            name="📈 Statistics",
            value=f"**Battles Won:** {stats.get('battles_won', 0)}\n"
                  f"**Adventures:** {self.player_data.get('adventure_count', 0)}\n"
                  f"**Work Count:** {self.player_data.get('work_count', 0)}",
            inline=True
        )

        return embed

    def create_inventory_embed(self) -> discord.Embed:
        """Create inventory embed."""
        inventory = self.player_data.get('inventory', [])
        equipped = self.player_data.get('equipped', {})

        embed = discord.Embed(
            title=f"🎒 {self.user.display_name}'s Inventory",
            color=COLORS['secondary']
        )

        # Equipped items
        weapon = equipped.get('weapon', 'None')
        armor = equipped.get('armor', 'None')
        accessory = equipped.get('accessory', 'None')

        embed.add_field(
            name="🔧 Equipped",
            value=f"**Weapon:** {weapon}\n"
                  f"**Armor:** {armor}\n"
                  f"**Accessory:** {accessory}",
            inline=False
        )

        # Inventory items
        if inventory:
            items_text = ""
            for item in inventory[:10]:  # Show first 10 items
                items_text += f"• {item}\n"
            if len(inventory) > 10:
                items_text += f"... and {len(inventory) - 10} more items"
        else:
            items_text = "Your inventory is empty!"

        embed.add_field(
            name="📦 Items",
            value=items_text,
            inline=False
        )

        return embed

    def create_luck_embed(self) -> discord.Embed:
        """Create luck embed."""
        luck_status = get_luck_status(str(self.user.id))

        embed = discord.Embed(
            title=f"🍀 {self.user.display_name}'s Luck",
            color=COLORS['success']
        )

        embed.add_field(
            name="🎲 Luck Status",
            value=f"**Level:** {luck_status['emoji']} {luck_status['level']}\n"
                  f"**Points:** {luck_status['points']}\n"
                  f"**Bonus:** +{luck_status['bonus_percent']}%",
            inline=False
        )

        return embed

def generate_random_item():
    """Generate a random item with rarity."""
    # Choose item type
    item_type = random.choice(["weapon", "armor"])

    # Choose rarity based on weights
    rarity_list = []
    for rarity, weight in RARITY_WEIGHTS.items():
        rarity_list.extend([rarity] * int(weight * 100))

    chosen_rarity = random.choice(rarity_list)

    # Get items of chosen rarity
    if item_type == "weapon":
        items = {k: v for k, v in WEAPONS.items() if v["rarity"] == chosen_rarity}
    else:
        items = {k: v for k, v in ARMOR.items() if v["rarity"] == chosen_rarity}

    if not items:
        # Fallback to common items
        if item_type == "weapon":
            items = {k: v for k, v in WEAPONS.items() if v["rarity"] == "common"}
        else:
            items = {k: v for k, v in ARMOR.items() if v["rarity"] == "common"}

    item_name = random.choice(list(items.keys()))
    return item_name, items[item_name]

def get_rarity_emoji(rarity):
    """Get emoji for rarity."""
    emojis = {
        "common": "⚪",
        "uncommon": "🟢", 
        "rare": "🔵",
        "epic": "🟣",
        "legendary": "🟠",
        "mythic": "🔴",
        "divine": "🟡",
        "omnipotent": "💖"
    }
    return emojis.get(rarity, "⚪")

class AdventureView(discord.ui.View):
    """Interactive adventure view."""

    def __init__(self, user_id: str):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.select(
        placeholder="Choose your adventure location...",
        options=[
            discord.SelectOption(
                label="Forest",
                value="Forest",
                description="A peaceful forest with hidden treasures",
                emoji="🌲"
            ),
            discord.SelectOption(
                label="Mountains",
                value="Mountains", 
                description="Treacherous peaks with great rewards",
                emoji="⛰️"
            ),
            discord.SelectOption(
                label="Dungeon",
                value="Dungeon",
                description="Dark underground chambers",
                emoji="🏰"
            ),
            discord.SelectOption(
                label="Desert",
                value="Desert",
                description="Endless sands with ancient secrets",
                emoji="🏜️"
            )
        ]
    )
    async def adventure_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Start an adventure."""
        location = select.values[0]

        # Disable the select while processing
        select.disabled = True
        await interaction.response.edit_message(view=self)

        # Process adventure
        await self.process_adventure(interaction, location)

    async def process_adventure(self, interaction: discord.Interaction, location: str):
        """Process the adventure."""
        try:
            player_data = get_user_rpg_data(self.user_id)
            if not player_data:
                await interaction.followup.send("❌ Could not retrieve your data!", ephemeral=True)
                return

            # Get adventure outcome
            outcome = get_random_adventure_outcome()

            # Calculate rewards with luck
            base_coins = random.randint(*outcome['coins'])
            base_xp = random.randint(*outcome['xp'])

            enhanced_rewards = generate_loot_with_luck(self.user_id, {
                'coins': base_coins,
                'xp': base_xp
            })

            coins_earned = enhanced_rewards['coins']
            xp_earned = enhanced_rewards['xp']

            # Random item reward
            items_found = []
            if roll_with_luck(self.user_id, 0.3):  # 30% chance for item
                items_found = [random.choice(outcome['items'])]

            # Update player data
            player_data['coins'] = player_data.get('coins', 0) + coins_earned
            player_data['xp'] = player_data.get('xp', 0) + xp_earned
            player_data['adventure_count'] = player_data.get('adventure_count', 0) + 1

            # Add items to inventory
            if items_found:
                inventory = player_data.get('inventory', [])
                inventory.extend(items_found)
                player_data['inventory'] = inventory

            # Check for level up
            level_up_msg = level_up_player(player_data)

            update_user_rpg_data(self.user_id, player_data)

            # Create result embed
            embed = discord.Embed(
                title=f"🗺️ Adventure Complete - {location}",
                description=outcome['description'],
                color=COLORS['success']
            )

            embed.add_field(
                name="💰 Rewards",
                value=f"**Coins:** {format_number(coins_earned)}\n"
                      f"**XP:** {xp_earned}",
                inline=True
            )

            if items_found:
                embed.add_field(
                    name="📦 Items Found",
                    value="\n".join([f"• {item}" for item in items_found]),
                    inline=True
                )

            if level_up_msg:
                embed.add_field(
                    name="📊 Level Up!",
                    value=level_up_msg,
                    inline=False
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Adventure error: {e}")
            await interaction.followup.send("❌ Adventure failed! Please try again.", ephemeral=True)

class ShopView(discord.ui.View):
    """Comprehensive interactive shop with categories and detailed item views."""

    def __init__(self, user_id: str):
        super().__init__(timeout=600)
        self.user_id = user_id
        self.current_category = "weapons"
        self.current_page = 0
        self.selected_item = None
        self.update_shop_display()

    def update_shop_display(self):
        """Update the shop display based on current category and page."""
        self.clear_items()
        
        # Category selector
        category_options = [
            discord.SelectOption(
                label="Weapons",
                value="weapons",
                description="Swords, axes, and magical weapons",
                emoji="⚔️",
                default=self.current_category == "weapons"
            ),
            discord.SelectOption(
                label="Armor",
                value="armor", 
                description="Protective gear and clothing",
                emoji="🛡️",
                default=self.current_category == "armor"
            ),
            discord.SelectOption(
                label="Consumables",
                value="consumables",
                description="Potions, food, and temporary items",
                emoji="🧪",
                default=self.current_category == "consumables"
            ),
            discord.SelectOption(
                label="Accessories",
                value="accessories",
                description="Rings, amulets, and special items",
                emoji="💎",
                default=self.current_category == "accessories"
            )
        ]
        
        category_select = discord.ui.Select(
            placeholder="📂 Choose item category...",
            options=category_options,
            custom_id="category_select"
        )
        category_select.callback = self.category_callback
        self.add_item(category_select)

        # Get items for current category
        items = self.get_category_items()
        
        if items:
            # Item selector with pagination
            items_per_page = 10
            start_idx = self.current_page * items_per_page
            end_idx = start_idx + items_per_page
            page_items = list(items.items())[start_idx:end_idx]

            if page_items:
                item_options = []
                for item_id, item_data in page_items[:25]:  # Discord limit
                    rarity = item_data.get('rarity', 'common')
                    emoji = get_rarity_emoji(rarity)
                    price = item_data.get('price', 0)
                    
                    # Create description with key stats
                    desc_parts = [f"{format_number(price)} coins"]
                    if item_data.get('attack'):
                        desc_parts.append(f"⚔️{item_data['attack']}")
                    if item_data.get('defense'):
                        desc_parts.append(f"🛡️{item_data['defense']}")
                    if item_data.get('effect'):
                        effect = item_data['effect'].replace('_', ' ')[:20]
                        desc_parts.append(f"✨{effect}")
                    
                    description = " | ".join(desc_parts)
                    
                    item_options.append(discord.SelectOption(
                        label=item_data.get('name', 'Unknown Item')[:100],
                        value=item_id,
                        description=description[:100],
                        emoji=emoji
                    ))

                if item_options:
                    item_select = discord.ui.Select(
                        placeholder=f"🛍️ Select an item to view details...",
                        options=item_options,
                        custom_id="item_select"
                    )
                    item_select.callback = self.item_callback
                    self.add_item(item_select)

        # Navigation buttons
        nav_row = []
        
        # Previous page button
        if self.current_page > 0:
            prev_button = discord.ui.Button(
                label="◀ Previous",
                style=discord.ButtonStyle.secondary,
                custom_id="prev_page"
            )
            prev_button.callback = self.prev_page_callback
            nav_row.append(prev_button)

        # Next page button  
        total_items = len(self.get_category_items())
        items_per_page = 10
        max_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1
        
        if self.current_page < max_pages - 1:
            next_button = discord.ui.Button(
                label="Next ▶",
                style=discord.ButtonStyle.secondary,
                custom_id="next_page"
            )
            next_button.callback = self.next_page_callback
            nav_row.append(next_button)

        # Refresh button
        refresh_button = discord.ui.Button(
            label="🔄 Refresh",
            style=discord.ButtonStyle.secondary,
            custom_id="refresh"
        )
        refresh_button.callback = self.refresh_callback
        nav_row.append(refresh_button)

        # Add navigation buttons
        for button in nav_row:
            self.add_item(button)

        # Purchase button (only if item selected)
        if self.selected_item:
            purchase_button = discord.ui.Button(
                label="💰 Purchase Item",
                style=discord.ButtonStyle.success,
                custom_id="purchase"
            )
            purchase_button.callback = self.purchase_callback
            self.add_item(purchase_button)

    def get_category_items(self) -> Dict[str, Any]:
        """Get items for the current category."""
        from utils.constants import SHOP_ITEMS
        
        category_items = {}
        for item_id, item_data in SHOP_ITEMS.items():
            if item_data.get('category') == self.current_category:
                category_items[item_id] = item_data
        
        return category_items

    async def category_callback(self, interaction: discord.Interaction):
        """Handle category selection."""
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("❌ This isn't your shop!", ephemeral=True)
            return

        self.current_category = interaction.data['values'][0]
        self.current_page = 0
        self.selected_item = None
        self.update_shop_display()
        
        embed = self.create_shop_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def item_callback(self, interaction: discord.Interaction):
        """Handle item selection to show details."""
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("❌ This isn't your shop!", ephemeral=True)
            return

        self.selected_item = interaction.data['values'][0]
        self.update_shop_display()
        
        embed = self.create_item_detail_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def prev_page_callback(self, interaction: discord.Interaction):
        """Handle previous page navigation."""
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("❌ This isn't your shop!", ephemeral=True)
            return

        self.current_page = max(0, self.current_page - 1)
        self.selected_item = None
        self.update_shop_display()
        
        embed = self.create_shop_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def next_page_callback(self, interaction: discord.Interaction):
        """Handle next page navigation."""
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("❌ This isn't your shop!", ephemeral=True)
            return

        self.current_page += 1
        self.selected_item = None
        self.update_shop_display()
        
        embed = self.create_shop_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def refresh_callback(self, interaction: discord.Interaction):
        """Handle shop refresh."""
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("❌ This isn't your shop!", ephemeral=True)
            return

        self.selected_item = None
        self.update_shop_display()
        
        embed = self.create_shop_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def purchase_callback(self, interaction: discord.Interaction):
        """Handle item purchase."""
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("❌ This isn't your shop!", ephemeral=True)
            return

        if not self.selected_item:
            await interaction.response.send_message("❌ No item selected!", ephemeral=True)
            return

        await self.process_purchase(interaction)

    def create_shop_embed(self) -> discord.Embed:
        """Create the main shop embed."""
        player_data = get_user_rpg_data(self.user_id)
        coins = player_data.get('coins', 0) if player_data else 0
        
        embed = discord.Embed(
            title="🏪 Plagg's Chaos Shop",
            description=f"*\"Welcome to my shop! I've got everything a kwami needs... and some cheese!\"* 🧀\n\n"
                       f"💰 **Your Coins:** {format_number(coins)}",
            color=COLORS['warning']
        )

        # Category info
        category_info = {
            "weapons": {"emoji": "⚔️", "desc": "Swords, axes, staffs, and mystical weapons"},
            "armor": {"emoji": "🛡️", "desc": "Protective gear, robes, and defensive equipment"},
            "consumables": {"emoji": "🧪", "desc": "Potions, food, and temporary enhancement items"},
            "accessories": {"emoji": "💎", "desc": "Rings, amulets, charms, and special trinkets"}
        }

        current_info = category_info.get(self.current_category, {"emoji": "📦", "desc": "Various items"})
        embed.add_field(
            name=f"{current_info['emoji']} Current Category: {self.current_category.title()}",
            value=current_info['desc'],
            inline=False
        )

        # Items in category
        items = self.get_category_items()
        items_per_page = 10
        start_idx = self.current_page * items_per_page
        end_idx = start_idx + items_per_page
        page_items = list(items.items())[start_idx:end_idx]

        if page_items:
            items_text = ""
            for i, (item_id, item_data) in enumerate(page_items, 1):
                rarity = item_data.get('rarity', 'common')
                emoji = get_rarity_emoji(rarity)
                name = item_data.get('name', 'Unknown')
                price = item_data.get('price', 0)
                
                # Add quick stats preview
                stats = []
                if item_data.get('attack'):
                    stats.append(f"⚔️{item_data['attack']}")
                if item_data.get('defense'):
                    stats.append(f"🛡️{item_data['defense']}")
                if item_data.get('effect'):
                    stats.append("✨Special")
                    
                stats_text = f" [{'/'.join(stats)}]" if stats else ""
                items_text += f"`{start_idx + i:2d}.` {emoji} **{name}**{stats_text} - {format_number(price)} coins\n"

            embed.add_field(
                name="📋 Available Items",
                value=items_text,
                inline=False
            )

            # Page info
            total_pages = (len(items) - 1) // items_per_page + 1 if len(items) > 0 else 1
            embed.add_field(
                name="📄 Page Navigation",
                value=f"Page {self.current_page + 1} of {total_pages} | Total Items: {len(items)}",
                inline=True
            )
        else:
            embed.add_field(
                name="📋 Available Items",
                value="No items available in this category.",
                inline=False
            )

        embed.set_footer(text="💡 Select an item to view detailed information and purchase options!")
        return embed

    def create_item_detail_embed(self) -> discord.Embed:
        """Create detailed item view embed."""
        from utils.constants import SHOP_ITEMS
        
        if not self.selected_item or self.selected_item not in SHOP_ITEMS:
            return self.create_shop_embed()

        item_data = SHOP_ITEMS[self.selected_item]
        rarity = item_data.get('rarity', 'common')
        color = RARITY_COLORS.get(rarity, COLORS['primary'])
        emoji = get_rarity_emoji(rarity)
        
        embed = discord.Embed(
            title=f"{emoji} {item_data.get('name', 'Unknown Item')}",
            description=item_data.get('description', 'A mysterious item from Plagg\'s collection.'),
            color=color
        )

        # Item stats
        stats_text = ""
        if item_data.get('attack'):
            stats_text += f"⚔️ **Attack:** +{item_data['attack']}\n"
        if item_data.get('defense'):
            stats_text += f"🛡️ **Defense:** +{item_data['defense']}\n"
        if item_data.get('hp'):
            stats_text += f"❤️ **Health:** +{item_data['hp']}\n"
        if item_data.get('mana'):
            stats_text += f"💙 **Mana:** +{item_data['mana']}\n"

        if stats_text:
            embed.add_field(name="📊 Stats", value=stats_text, inline=True)

        # Special effects
        if item_data.get('effect'):
            effect_desc = self.format_effect_description(item_data['effect'])
            embed.add_field(name="✨ Special Effect", value=effect_desc, inline=True)

        # Price and rarity
        price = item_data.get('price', 0)
        embed.add_field(
            name="💰 Purchase Info",
            value=f"**Price:** {format_number(price)} coins\n"
                  f"**Rarity:** {rarity.title()}\n"
                  f"**Category:** {item_data.get('category', 'unknown').title()}",
            inline=True
        )

        # Player's current coins
        player_data = get_user_rpg_data(self.user_id)
        coins = player_data.get('coins', 0) if player_data else 0
        
        can_afford = coins >= price
        afford_status = "✅ You can afford this!" if can_afford else f"❌ Need {format_number(price - coins)} more coins"
        
        embed.add_field(
            name="💳 Your Wallet",
            value=f"**Your Coins:** {format_number(coins)}\n{afford_status}",
            inline=False
        )

        # Usage instructions
        if item_data.get('category') == 'consumables':
            embed.add_field(
                name="📖 Usage",
                value="This item can be used from your inventory with the `$use` command.",
                inline=False
            )
        elif item_data.get('category') in ['weapons', 'armor']:
            embed.add_field(
                name="📖 Equipment",
                value="This item can be equipped from your inventory with the `$equip` command.",
                inline=False
            )

        embed.set_footer(text="💡 Click 'Purchase Item' to buy this item!")
        return embed

    def format_effect_description(self, effect: str) -> str:
        """Format effect descriptions to be more readable."""
        effect_descriptions = {
            'heal_50': 'Restores 50 HP instantly',
            'heal_500': 'Restores 500 HP instantly',
            'mana_50': 'Restores 50 MP instantly',
            'luck_boost': 'Increases luck for next adventure',
            'xp_double': 'Doubles XP gain for next battle',
            'revive': 'Revives from defeat (one-time use)',
            'random_reward': 'Contains random valuable items'
        }
        
        return effect_descriptions.get(effect, effect.replace('_', ' ').title())

    async def process_purchase(self, interaction: discord.Interaction):
        """Process the item purchase."""
        from utils.constants import SHOP_ITEMS
        
        try:
            player_data = get_user_rpg_data(self.user_id)
            if not player_data:
                await interaction.response.send_message("❌ Could not retrieve your data!", ephemeral=True)
                return

            if self.selected_item not in SHOP_ITEMS:
                await interaction.response.send_message("❌ Invalid item selected!", ephemeral=True)
                return

            item_data = SHOP_ITEMS[self.selected_item]
            price = item_data.get('price', 0)
            coins = player_data.get('coins', 0)

            if coins < price:
                await interaction.response.send_message(
                    f"❌ **Insufficient funds!**\n"
                    f"You need **{format_number(price)}** coins but only have **{format_number(coins)}**.\n"
                    f"You need **{format_number(price - coins)}** more coins!",
                    ephemeral=True
                )
                return

            # Process purchase
            player_data['coins'] = coins - price
            inventory = player_data.get('inventory', [])
            inventory.append(item_data['name'])
            player_data['inventory'] = inventory

            # Update stats if needed
            stats = player_data.get('stats', {})
            stats['items_purchased'] = stats.get('items_purchased', 0) + 1
            player_data['stats'] = stats

            update_user_rpg_data(self.user_id, player_data)

            # Create purchase confirmation
            rarity = item_data.get('rarity', 'common')
            emoji = get_rarity_emoji(rarity)
            
            embed = discord.Embed(
                title="🎉 Purchase Successful!",
                description=f"You successfully purchased **{emoji} {item_data['name']}** for {format_number(price)} coins!",
                color=COLORS['success']
            )

            embed.add_field(
                name="💰 Transaction Details",
                value=f"**Item:** {item_data['name']}\n"
                      f"**Price:** {format_number(price)} coins\n"
                      f"**Remaining Coins:** {format_number(coins - price)}",
                inline=True
            )

            embed.add_field(
                name="📦 Next Steps",
                value="• Check your `$inventory` to see the item\n"
                      "• Use `$equip <item>` for weapons/armor\n"
                      "• Use `$use <item>` for consumables",
                inline=True
            )

            embed.set_footer(text="💡 Thanks for shopping at Plagg's Chaos Shop!")

            # Reset selection and update view
            self.selected_item = None
            self.update_shop_display()

            await interaction.response.edit_message(embed=embed, view=self)

        except Exception as e:
            logger.error(f"Purchase error: {e}")
            await interaction.response.send_message("❌ Purchase failed! Please try again.", ephemeral=True)

class LootboxView(discord.ui.View):
    """Lootbox opening view."""

    def __init__(self, user_id: str):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.button(label="📦 Open Lootbox", style=discord.ButtonStyle.primary, emoji="🎁")
    async def open_lootbox(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open a lootbox."""
        player_data = get_user_rpg_data(self.user_id)
        if not player_data:
            await interaction.response.send_message("❌ Could not retrieve your data!", ephemeral=True)
            return

        inventory = player_data.get('inventory', [])
        if "Lootbox" not in inventory:
            await interaction.response.send_message("❌ You don't have any lootboxes!", ephemeral=True)
            return

        # Remove lootbox from inventory
        inventory.remove("Lootbox")
        player_data['inventory'] = inventory

        # Generate loot
        rewards = []
        coins_reward = 0

        # Always get coins
        coins_reward = random.randint(100, 1000)

        # Chance for items
        for _ in range(3):  # 3 chances for items
            if roll_with_luck(self.user_id, 0.4):  # 40% chance per roll
                item_name, item_data = generate_random_item()
                rewards.append(item_name)
                inventory.append(item_name)

        # Super rare chance for omnipotent items
        if roll_with_luck(self.user_id, 0.001):  # 0.1% chance
            if random.choice([True, False]):
                rewards.append("World Ender")
                inventory.append("World Ender")
            else:
                rewards.append("Reality Stone")
                inventory.append("Reality Stone")

        player_data['coins'] = player_data.get('coins', 0) + coins_reward
        player_data['inventory'] = inventory
        update_user_rpg_data(self.user_id, player_data)

        # Create result embed
        embed = discord.Embed(
            title="🎁 Lootbox Opened!",
            description=f"**Coins:** {format_number(coins_reward)}",
            color=COLORS['success']
        )

        if rewards:
            items_text = ""
            for item in rewards:
                if item in WEAPONS:
                    rarity = WEAPONS[item]["rarity"]
                elif item in ARMOR:
                    rarity = ARMOR[item]["rarity"]
                elif item == "Reality Stone":
                    rarity = "omnipotent"
                else:
                    rarity = "common"

                emoji = get_rarity_emoji(rarity)
                items_text += f"{emoji} **{item}** ({rarity})\n"

            embed.add_field(name="🎯 Items Found", value=items_text, inline=False)

        button.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

class PvPView(discord.ui.View):
    """PvP battle view."""

    def __init__(self, challenger_id: str, target_id: str, arena: str):
        super().__init__(timeout=300)
        self.challenger_id = challenger_id
        self.target_id = target_id
        self.arena = arena
        self.accepted = False

    @discord.ui.button(label="⚔️ Accept Challenge", style=discord.ButtonStyle.success)
    async def accept_challenge(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Accept the PvP challenge."""
        if str(interaction.user.id) != self.target_id:
            await interaction.response.send_message("❌ This challenge is not for you!", ephemeral=True)
            return

        self.accepted = True
        await self.start_pvp_battle(interaction)

    @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger)
    async def decline_challenge(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Decline the PvP challenge."""
        if str(interaction.user.id) != self.target_id:
            await interaction.response.send_message("❌ This challenge is not for you!", ephemeral=True)
            return

        embed = discord.Embed(
            title="❌ Challenge Declined",
            description=f"<@{self.target_id}> declined the challenge.",
            color=COLORS['error']
        )

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    async def start_pvp_battle(self, interaction):
        """Start the actual PvP battle."""
        challenger_data = get_user_rpg_data(self.challenger_id)
        target_data = get_user_rpg_data(self.target_id)

        if not challenger_data or not target_data:
            await interaction.response.send_message("❌ Could not retrieve player data!", ephemeral=True)
            return

        # Calculate battle stats
        challenger_attack = challenger_data.get('attack', 10)
        challenger_hp = challenger_data.get('hp', 100)
        challenger_defense = challenger_data.get('defense', 5)

        target_attack = target_data.get('attack', 10)
        target_hp = target_data.get('hp', 100)
        target_defense = target_data.get('defense', 5)

        # Check for super rare weapons
        challenger_inventory = challenger_data.get('inventory', [])
        target_inventory = target_data.get('inventory', [])

        if "World Ender" in challenger_inventory:
            challenger_attack = 999999
        if "World Ender" in target_inventory:
            target_attack = 999999

        # Battle simulation
        battle_log = []
        turn = 1

        while challenger_hp > 0 and target_hp > 0 and turn <= 10:
            # Challenger attacks
            damage = calculate_battle_damage(challenger_attack, target_defense)
            target_hp -= damage
            battle_log.append(f"Round {turn}: Challenger deals {damage} damage!")

            if target_hp <= 0:
                break

            # Target attacks
            damage = calculate_battle_damage(target_attack, challenger_defense)
            challenger_hp -= damage
            battle_log.append(f"Round {turn}: Target deals {damage} damage!")

            turn += 1

        # Determine winner
        arena_data = PVP_ARENAS[self.arena]
        entry_fee = arena_data["entry_fee"]
        winner_reward = entry_fee * arena_data["winner_multiplier"]

        if challenger_hp > target_hp:
            winner = self.challenger_id
            loser = self.target_id
            winner_data = challenger_data
            loser_data = target_data
        else:
            winner = self.target_id
            loser = self.challenger_id
            winner_data = target_data
            loser_data = challenger_data

        # Update winner's data
        winner_data['coins'] = winner_data.get('coins', 0) + winner_reward
        winner_stats = winner_data.get('stats', {})
        winner_stats['pvp_wins'] = winner_stats.get('pvp_wins', 0) + 1
        winner_data['stats'] = winner_stats

        # Update loser's data
        loser_data['coins'] = max(0, loser_data.get('coins', 0) - entry_fee)
        loser_stats = loser_data.get('stats', {})
        loser_stats['pvp_losses'] = loser_stats.get('pvp_losses', 0) + 1
        loser_data['stats'] = loser_stats

        update_user_rpg_data(winner, winner_data)
        update_user_rpg_data(loser, loser_data)

        # Create result embed
        embed = discord.Embed(
            title=f"⚔️ PvP Battle Complete - {self.arena}",
            description=f"**Winner:** <@{winner}>\n**Reward:** {format_number(winner_reward)} coins",
            color=COLORS['success']
        )

        battle_text = "\n".join(battle_log[:6])  # Show first 6 rounds
        embed.add_field(name="🥊 Battle Log", value=battle_text, inline=False)

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

class TradeView(discord.ui.View):
    """Trading system view."""

    def __init__(self, trader1_id: str, trader2_id: str):
        super().__init__(timeout=600)
        self.trader1_id = trader1_id
        self.trader2_id = trader2_id
        self.trader1_items = []
        self.trader2_items = []
        self.trader1_coins = 0
        self.trader2_coins = 0
        self.trader1_ready = False
        self.trader2_ready = False

    @discord.ui.button(label="💎 Add Items", style=discord.ButtonStyle.primary)
    async def add_items(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add items to trade."""
        user_id = str(interaction.user.id)
        if user_id not in [self.trader1_id, self.trader2_id]:
            await interaction.response.send_message("❌ You're not part of this trade!", ephemeral=True)
            return

        await interaction.response.send_message("📝 Please type the item name you want to add to the trade:", ephemeral=True)

    @discord.ui.button(label="💰 Add Coins", style=discord.ButtonStyle.secondary)
    async def add_coins(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add coins to trade."""
        user_id = str(interaction.user.id)
        if user_id not in [self.trader1_id, self.trader2_id]:
            await interaction.response.send_message("❌ You're not part of this trade!", ephemeral=True)
            return

        await interaction.response.send_message("💰 Please type the amount of coins you want to add:", ephemeral=True)

    @discord.ui.button(label="✅ Ready", style=discord.ButtonStyle.success)
    async def ready_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Mark as ready for trade."""
        user_id = str(interaction.user.id)

        if user_id == self.trader1_id:
            self.trader1_ready = True
        elif user_id == self.trader2_id:
            self.trader2_ready = True
        else:
            await interaction.response.send_message("❌ You're not part of this trade!", ephemeral=True)
            return

        if self.trader1_ready and self.trader2_ready:
            await self.execute_trade(interaction)
        else:
            await interaction.response.send_message("✅ You are ready! Waiting for the other trader...", ephemeral=True)

    @discord.ui.button(label="❌ Cancel Trade", style=discord.ButtonStyle.danger)
    async def cancel_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancel the trade."""
        embed = discord.Embed(
            title="❌ Trade Cancelled",
            description="The trade has been cancelled.",
            color=COLORS['error']
        )

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

    async def execute_trade(self, interaction):
        """Execute the trade between players."""
        trader1_data = get_user_rpg_data(self.trader1_id)
        trader2_data = get_user_rpg_data(self.trader2_id)

        if not trader1_data or not trader2_data:
            await interaction.response.send_message("❌ Could not retrieve trader data!", ephemeral=True)
            return

        # Execute the trade
        # This is a simplified version - in practice you'd want more validation

        embed = discord.Embed(
            title="✅ Trade Completed!",
            description="The trade has been successfully completed!",
            color=COLORS['success']
        )

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

class BattleView(discord.ui.View):
    """Interactive battle view."""

    def __init__(self, user_id: str, enemy_data: Dict[str, Any]):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.enemy_data = enemy_data

    @discord.ui.button(label="⚔️ Attack", style=discord.ButtonStyle.danger)
    async def attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Attack the enemy."""
        await self.process_battle_action(interaction, "attack")

    @discord.ui.button(label="🛡️ Defend", style=discord.ButtonStyle.secondary)
    async def defend_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Defend against enemy attack."""
        await self.process_battle_action(interaction, "defend")

    @discord.ui.button(label="🧪 Use Item", style=discord.ButtonStyle.success)
    async def item_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Use an item."""
        await self.process_battle_action(interaction, "item")

    async def process_battle_action(self, interaction: discord.Interaction, action: str):
        """Process battle action."""
        try:
            player_data = get_user_rpg_data(self.user_id)
            if not player_data:
                await interaction.response.send_message("❌ Could not retrieve your data!", ephemeral=True)
                return

            player_hp = player_data.get('hp', 100)
            player_attack = player_data.get('attack', 10)
            player_defense = player_data.get('defense', 5)

            enemy_hp = self.enemy_data.get('hp', 50)
            enemy_attack = self.enemy_data.get('attack', 8)

            battle_result = ""

            if action == "attack":
                # Player attacks
                damage = calculate_battle_damage(player_attack, 0)
                enemy_hp -= damage
                battle_result += f"You dealt {damage} damage to {self.enemy_data['name']}!\n"

                # Enemy attacks back if still alive
                if enemy_hp > 0:
                    enemy_damage = calculate_battle_damage(enemy_attack, player_defense)
                    player_hp -= enemy_damage
                    battle_result += f"{self.enemy_data['name']} dealt {enemy_damage} damage to you!\n"

            elif action == "defend":
                # Reduced damage when defending
                enemy_damage = calculate_battle_damage(enemy_attack, player_defense * 2)
                player_hp -= enemy_damage
                battle_result += f"You defended! {self.enemy_data['name']} dealt {enemy_damage} damage!\n"

            # Check battle outcome
            if enemy_hp <= 0:
                # Victory
                coins_reward = random.randint(50, 150)
                xp_reward = random.randint(20, 50)

                player_data['coins'] = player_data.get('coins', 0) + coins_reward
                player_data['xp'] = player_data.get('xp', 0) + xp_reward

                stats = player_data.get('stats', {})
                stats['battles_won'] = stats.get('battles_won', 0) + 1
                player_data['stats'] = stats

                embed = discord.Embed(
                    title="🎉 Victory!",
                    description=f"{battle_result}\n**You defeated {self.enemy_data['name']}!**\n\n"
                               f"**Rewards:**\n"
                               f"Coins: {format_number(coins_reward)}\n"
                               f"XP: {xp_reward}",
                    color=COLORS['success']
                )

                # Disable all buttons
                for item in self.children:
                    item.disabled = True

            elif player_hp <= 0:
                # Defeat
                player_data['hp'] = 0
                stats = player_data.get('stats', {})
                stats['battles_lost'] = stats.get('battles_lost', 0) + 1
                player_data['stats'] = stats

                embed = discord.Embed(
                    title="💀 Defeat!",
                    description=f"{battle_result}\n**You were defeated by {self.enemy_data['name']}!**\n\n"
                               f"You need to heal before your next battle.",
                    color=COLORS['error']
                )

                # Disable all buttons
                for item in self.children:
                    item.disabled = True

            else:
                # Battle continues
                self.enemy_data['hp'] = enemy_hp
                player_data['hp'] = player_hp

                embed = discord.Embed(
                    title=f"⚔️ Battle vs {self.enemy_data['name']}",
                    description=f"{battle_result}\n\n"
                               f"**Your HP:** {player_hp}/{player_data.get('max_hp', 100)}\n"
                               f"**{self.enemy_data['name']} HP:** {enemy_hp}/{self.enemy_data.get('max_hp', enemy_hp)}",
                    color=COLORS['warning']
                )

            # Update player data
            update_user_rpg_data(self.user_id, player_data)

            await interaction.response.edit_message(embed=embed, view=self)

        except Exception as e:
            logger.error(f"Battle error: {e}")
            await interaction.response.send_message("❌ Battle error! Please try again.", ephemeral=True)

class RPGGamesCog(commands.Cog):
    """RPG Games system for the bot."""

    def __init__(self, bot):
        self.bot = bot

    # Slash command versions
    @app_commands.command(name="profile", description="View your character profile")
    @app_commands.describe(member="The member to view (optional)")
    async def profile_slash(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """View character profile (slash command)."""
        if not is_module_enabled("rpg", interaction.guild_id):
            await interaction.response.send_message("❌ RPG module is disabled!", ephemeral=True)
            return

        target = member or interaction.user
        user_id = str(target.id)

        if not ensure_user_exists(user_id):
            await interaction.response.send_message(f"❌ {target.display_name} hasn't started their adventure yet!", ephemeral=True)
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await interaction.response.send_message("❌ Could not retrieve profile data.", ephemeral=True)
            return

        view = ProfileView(target, player_data)
        embed = view.create_stats_embed()

        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="start", description="Start your RPG adventure")
    async def start_slash(self, interaction: discord.Interaction):
        """Start RPG adventure (slash command)."""
        if not is_module_enabled("rpg", interaction.guild_id):
            await interaction.response.send_message("❌ RPG module is disabled!", ephemeral=True)
            return

        user_id = str(interaction.user.id)

        # Check if user already exists
        if get_user_rpg_data(user_id):
            await interaction.response.send_message("❌ You've already started your adventure! Use `/profile` to see your stats.", ephemeral=True)
            return

        # Create new user profile
        if create_user_profile(user_id):
            embed = create_embed(
                "🎉 Adventure Started!",
                f"Welcome to your RPG adventure, {interaction.user.mention}!\n\n"
                f"**Starting Stats:**\n"
                f"• Level: 1\n"
                f"• HP: 100/100\n"
                f"• Attack: 10\n"
                f"• Defense: 5\n"
                f"• Coins: 100\n\n"
                f"Use `/profile` to view your character\n"
                f"Use `$adventure` to start exploring\n"
                f"Use `$work` to earn coins\n"
                f"Use `$shop` to buy equipment",
                COLORS['success']
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to start your adventure. Please try again.", ephemeral=True)

    @commands.command(name='start', help='Start your RPG adventure')
    async def start_command(self, ctx):
        """Start RPG adventure."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        # Check if user already exists


    # ============= CLASS SYSTEM =============

    @commands.command(name='class', help='Choose or view your character class')
    async def class_command(self, ctx, class_name: str = None):
        """Choose or view character class."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        from utils.constants import PLAYER_CLASSES

        if not class_name:
            # Show available classes
            embed = discord.Embed(
                title="🎭 Character Classes",
                description="Choose your path in the world of Miraculous!",
                color=COLORS['primary']
            )

            for class_key, class_data in PLAYER_CLASSES.items():
                stats = class_data['base_stats']
                embed.add_field(
                    name=f"{class_data['name']} ({class_key})",
                    value=f"{class_data['description']}\n"
                          f"HP: {stats['hp']} | ATK: {stats['attack']} | DEF: {stats['defense']} | MP: {stats['mana']}",
                    inline=False
                )

            embed.set_footer(text="Use $class <class_name> to choose your class!")
            await ctx.send(embed=embed)
            return

        class_name = class_name.lower()
        if class_name not in PLAYER_CLASSES:
            await ctx.send(f"❌ Invalid class! Use `$class` to see available classes.")
            return

        if player_data.get('player_class'):
            await ctx.send("❌ You already have a class! You cannot change classes.")
            return

        # Assign class
        class_data = PLAYER_CLASSES[class_name]
        player_data['player_class'] = class_name

        # Update base stats
        base_stats = class_data['base_stats']
        player_data['max_hp'] = base_stats['hp']
        player_data['hp'] = base_stats['hp']
        player_data['attack'] = base_stats['attack']
        player_data['defense'] = base_stats['defense']
        player_data['max_mana'] = base_stats['mana']
        player_data['mana'] = base_stats['mana']

        update_user_rpg_data(user_id, player_data)

        embed = create_embed(
            f"🎭 Class Selected: {class_data['name']}",
            f"{class_data['description']}\n\n"
            f"**Your new stats:**\n"
            f"HP: {base_stats['hp']}\n"
            f"Attack: {base_stats['attack']}\n"
            f"Defense: {base_stats['defense']}\n"
            f"Mana: {base_stats['mana']}",
            COLORS['success']
        )

        await ctx.send(embed=embed)

    @commands.command(name='skills', help='View your class skills')
    async def skills_command(self, ctx):
        """View class skills."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        player_class = player_data.get('player_class')
        if not player_class:
            await ctx.send("❌ You haven't chosen a class yet! Use `$class` to choose one.")
            return

        from utils.constants import PLAYER_CLASSES
        class_data = PLAYER_CLASSES[player_class]

        embed = discord.Embed(
            title=f"⚡ {class_data['name']} Skills",
            description=f"Skills available to {class_data['name']}:",
            color=COLORS['primary']
        )

        for skill_name, skill_data in class_data['skills'].items():
            cooldown_text = format_time_remaining(skill_data['cooldown'])

            embed.add_field(
                name=skill_name.replace('_', ' ').title(),
                value=f"Mana Cost: {skill_data['mana_cost']}\n"
                      f"Cooldown: {cooldown_text}\n"
                      f"Effect: {self._format_skill_effect(skill_data)}",
                inline=True
            )

        await ctx.send(embed=embed)

    def _format_skill_effect(self, skill_data):
        """Format skill effect for display."""
        effects = []
        if 'damage' in skill_data:
            effects.append(f"Damage: {skill_data['damage']}")
        if 'heal' in skill_data:
            effects.append(f"Heal: {skill_data['heal']}")
        if 'defense_boost' in skill_data:
            effects.append(f"+{skill_data['defense_boost']} Defense")
        if 'attack_boost' in skill_data:
            effects.append(f"+{skill_data['attack_boost']} Attack")
        return ", ".join(effects) if effects else "Special Effect"

    # ============= PROFESSION SYSTEM =============

    @commands.command(name='profession', help='Choose or view your profession')
    async def profession_command(self, ctx, profession_name: str = None):
        """Choose or view profession."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        from utils.constants import PROFESSIONS, RPG_CONSTANTS

        if not profession_name:
            # Show available professions
            embed = discord.Embed(
                title="🔨 Professions",
                description="Master a craft to create powerful items!",
                color=COLORS['secondary']
            )

            for prof_key, prof_data in PROFESSIONS.items():
                embed.add_field(
                    name=f"{prof_data['name']} ({prof_key})",
                    value=f"{prof_data['description']}\n"
                          f"Max Level: {prof_data['max_level']}\n"
                          f"Cost: {RPG_CONSTANTS['profession_unlock_cost']} coins",
                    inline=False
                )

            current_prof = player_data.get('profession')
            if current_prof:
                prof_level = player_data.get('profession_level', 0)
                embed.add_field(
                    name="Current Profession",
                    value=f"{PROFESSIONS[current_prof]['name']} (Level {prof_level})",
                    inline=False
                )

            await ctx.send(embed=embed)
            return

        profession_name = profession_name.lower()
        if profession_name not in PROFESSIONS:
            await ctx.send(f"❌ Invalid profession! Use `$profession` to see available professions.")
            return

        if player_data.get('profession'):
            await ctx.send("❌ You already have a profession! You cannot change professions.")
            return

        coins = player_data.get('coins', 0)
        cost = RPG_CONSTANTS['profession_unlock_cost']

        if coins < cost:
            await ctx.send(f"❌ You need {cost} coins to unlock a profession! You have {coins} coins.")
            return

        # Unlock profession
        prof_data = PROFESSIONS[profession_name]
        player_data['profession'] = profession_name
        player_data['profession_level'] = 1
        player_data['profession_xp'] = 0
        player_data['coins'] = coins - cost

        update_user_rpg_data(user_id, player_data)

        embed = create_embed(
            f"🔨 Profession Unlocked: {prof_data['name']}",
            f"{prof_data['description']}\n\n"
            f"You can now craft items and gather materials!\n"
            f"Use `$craft` and `$gather` to start your journey.",
            COLORS['success']
        )

        await ctx.send(embed=embed)

    @commands.command(name='craft', help='Craft items using materials')
    @commands.cooldown(1, RPG_CONSTANTS['craft_cooldown'], commands.BucketType.user)
    async def craft_command(self, ctx, *, recipe_name: str = None):
        """Craft items."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        profession = player_data.get('profession')
        if not profession:
            await ctx.send("❌ You need a profession to craft! Use `$profession` to choose one.")
            return

        from utils.constants import CRAFTING_RECIPES
        from utils.helpers import calculate_craft_success_rate, level_up_profession

        if not recipe_name:
            # Show available recipes
            available_recipes = {k: v for k, v in CRAFTING_RECIPES.items() 
                               if v['profession'] == profession and v['level_required'] <= player_data.get('profession_level', 0)}

            if not available_recipes:
                await ctx.send("❌ No recipes available for your profession level!")
                return

            embed = discord.Embed(
                title="📜 Available Recipes",
                description=f"Recipes for {profession}:",
                color=COLORS['secondary']
            )

            for recipe_key, recipe_data in available_recipes.items():
                materials_text = ", ".join([f"{count} {name}" for name, count in recipe_data['materials'].items()])
                embed.add_field(
                    name=recipe_key.replace('_', ' ').title(),
                    value=f"Level: {recipe_data['level_required']}\n"
                          f"Materials: {materials_text}\n"
                          f"Success Rate: {recipe_data['success_rate']*100:.0f}%",
                    inline=False
                )

            await ctx.send(embed=embed)
            return

        recipe_key = recipe_name.lower().replace(' ', '_')
        if recipe_key not in CRAFTING_RECIPES:
            await ctx.send(f"❌ Unknown recipe: {recipe_name}")
            return

        recipe = CRAFTING_RECIPES[recipe_key]

        if recipe['profession'] != profession:
            await ctx.send(f"❌ This recipe requires the {recipe['profession']} profession!")
            return

        if recipe['level_required'] > player_data.get('profession_level', 0):
            await ctx.send(f"❌ You need profession level {recipe['level_required']} to craft this!")
            return

        # Check materials
        player_materials = player_data.get('materials', {})
        missing_materials = []

        for material, needed in recipe['materials'].items():
            if player_materials.get(material, 0) < needed:
                missing_materials.append(f"{needed - player_materials.get(material, 0)} {material}")

        if missing_materials:
            await ctx.send(f"❌ Missing materials: {', '.join(missing_materials)}")
            return

        # Calculate success rate
        success_rate = calculate_craft_success_rate(player_data, recipe)

        # Attempt crafting
        if random.random() < success_rate:
            # Success!
            for material, needed in recipe['materials'].items():
                player_materials[material] = player_materials.get(material, 0) - needed

            # Add crafted item to inventory
            inventory = player_data.get('inventory', [])
            inventory.append(recipe['result']['name'])
            player_data['inventory'] = inventory
            player_data['materials'] = player_materials

            # Add profession XP
            prof_xp_gained = recipe['level_required'] * 20  # XP based on recipe difficulty
            level_up_msg = level_up_profession(player_data, profession, prof_xp_gained)

            # Update stats
            stats = player_data.get('stats', {})
            stats['items_crafted'] = stats.get('items_crafted', 0) + 1
            player_data['stats'] = stats

            update_user_rpg_data(user_id, player_data)

            embed = create_embed(
                "🔨 Crafting Successful!",
                f"You crafted **{recipe['result']['name']}**!\n"
                f"Profession XP gained: {prof_xp_gained}",
                COLORS['success']
            )

            if level_up_msg:
                embed.add_field(name="Level Up!", value=level_up_msg, inline=False)

        else:
            # Failure - materials still consumed but no item
            for material, needed in recipe['materials'].items():
                player_materials[material] = player_materials.get(material, 0) - needed

            player_data['materials'] = player_materials
            update_user_rpg_data(user_id, player_data)

            embed = create_embed(
                "💥 Crafting Failed!",
                f"Your attempt to craft **{recipe['result']['name']}** failed!\n"
                f"Materials were consumed in the process.",
                COLORS['error']
            )

        await ctx.send(embed=embed)

    @commands.command(name='gather', help='Gather crafting materials')
    @commands.cooldown(1, RPG_CONSTANTS['gather_cooldown'], commands.BucketType.user)
    async def gather_command(self, ctx, location: str = None):
        """Gather materials from locations."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        profession = player_data.get('profession')
        if not profession:
            await ctx.send("❌ You need a profession to gather materials! Use `$profession` to choose one.")
            return

        from utils.constants import GATHERING_MATERIALS, PROFESSIONS
        from utils.rng_system import roll_with_luck

        available_locations = PROFESSIONS[profession]['gathering_spots']

        if not location:
            embed = discord.Embed(
                title="🌍 Gathering Locations",
                description=f"Available locations for {profession}:",
                color=COLORS['primary']
            )

            for loc in available_locations:
                materials = [name for name, data in GATHERING_MATERIALS.items() if loc in data['locations']]
                embed.add_field(
                    name=loc.replace('_', ' ').title(),
                    value=f"Materials: {', '.join(materials)}",
                    inline=False
                )

            await ctx.send(embed=embed)
            return

        location = location.lower().replace(' ', '_')
        if location not in available_locations:
            await ctx.send(f"❌ Invalid location! Use `$gather` to see available locations.")
            return

        # Gather materials
        materials_found = []
        player_materials = player_data.get('materials', {})

        for material_name, material_data in GATHERING_MATERIALS.items():
            if location in material_data['locations']:
                if roll_with_luck(user_id, material_data['base_chance']):
                    amount = random.randint(1, 3)
                    materials_found.append((material_name, amount))
                    player_materials[material_name] = player_materials.get(material_name, 0) + amount

        # Add profession XP
        prof_xp_gained = len(materials_found) * 10
        if prof_xp_gained > 0:
            level_up_msg = level_up_profession(player_data, profession, prof_xp_gained)
        else:
            level_up_msg = None

        player_data['materials'] = player_materials

        # Update stats
        stats = player_data.get('stats', {})
        stats['materials_gathered'] = stats.get('materials_gathered', 0) + len(materials_found)
        player_data['stats'] = stats

        update_user_rpg_data(user_id, player_data)

        if materials_found:
            materials_text = "\n".join([f"• {amount}x {name.replace('_', ' ').title()}" for name, amount in materials_found])
            embed = create_embed(
                f"🌾 Gathering Complete - {location.replace('_', ' ').title()}",
                f"Materials found:\n{materials_text}\n\n"
                f"Profession XP gained: {prof_xp_gained}",
                COLORS['success']
            )

            if level_up_msg:
                embed.add_field(name="Level Up!", value=level_up_msg, inline=False)
        else:
            embed = create_embed(
                f"🌾 Gathering Complete - {location.replace('_', ' ').title()}",
                "You didn't find any materials this time. Try again later!",
                COLORS['warning']
            )

        await ctx.send(embed=embed)

    @commands.command(name='materials', help='View your crafting materials')
    async def materials_command(self, ctx):
        """View player's materials."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        materials = player_data.get('materials', {})

        if not materials:
            await ctx.send("❌ You have no materials! Use `$gather` to collect some.")
            return

        embed = discord.Embed(
            title="🧰 Your Materials",
            description="Crafting materials in your storage:",
            color=COLORS['secondary']
        )

        materials_text = ""
        for material, amount in materials.items():
            materials_text += f"• {amount}x {material.replace('_', ' ').title()}\n"

        embed.add_field(name="Materials", value=materials_text, inline=False)

        await ctx.send(embed=embed)

    # ============= QUEST SYSTEM =============

    @commands.command(name='quests', help='View available and active quests')
    async def quests_command(self, ctx):
        """View quest information."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        active_quests = player_data.get('active_quests', [])
        completed_quests = player_data.get('completed_quests', [])

        embed = discord.Embed(
            title="📜 Quest Journal",
            description=f"Active Quests: {len(active_quests)}/5\nCompleted: {len(completed_quests)}",
            color=COLORS['primary']
        )

        if active_quests:
            from utils.helpers import format_quest_progress
            for quest in active_quests[:3]:  # Show first 3 active quests
                progress = format_quest_progress(quest)
                embed.add_field(
                    name=f"🔥 {quest['title']}",
                    value=f"{quest['description']}\n\n{progress}",
                    inline=False
                )
        else:
            embed.add_field(
                name="No Active Quests",
                value="Use `$quest new` to get a new quest!",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='quest', help='Quest management (new, abandon, complete)')
    @commands.cooldown(1, RPG_CONSTANTS['quest_cooldown'], commands.BucketType.user)
    async def quest_command(self, ctx, action: str = None, *, quest_name: str = None):
        """Quest management."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        if not action:
            await ctx.send("❌ Specify an action: `new`, `abandon`, or `complete`")
            return

        if action.lower() == 'new':
            active_quests = player_data.get('active_quests', [])
            if len(active_quests) >= 5:
                await ctx.send("❌ You can only have 5 active quests! Abandon some first.")
                return

            from utils.helpers import generate_dynamic_quest
            from utils.constants import QUEST_TYPES

            # Generate a random quest
            quest_type = random.choice(list(QUEST_TYPES.keys()))
            new_quest = generate_dynamic_quest(user_id, quest_type)

            if new_quest:
                active_quests.append(new_quest)
                player_data['active_quests'] = active_quests
                update_user_rpg_data(user_id, player_data)

                embed = create_embed(
                    "📜 New Quest Acquired!",
                    f"**{new_quest['title']}**\n"
                    f"{new_quest['description']}\n\n"
                    f"Location: {new_quest['location'].replace('_', ' ').title()}\n"
                    f"Type: {new_quest['type'].title()}",
                    COLORS['success']
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Failed to generate quest. Try again later.")

        elif action.lower() == 'abandon':
            if not quest_name:
                await ctx.send("❌ Specify which quest to abandon!")
                return

            active_quests = player_data.get('active_quests', [])
            quest_to_remove = None

            for quest in active_quests:
                if quest_name.lower() in quest['title'].lower():
                    quest_to_remove = quest
                    break

            if quest_to_remove:
                active_quests.remove(quest_to_remove)
                player_data['active_quests'] = active_quests
                update_user_rpg_data(user_id, player_data)
                await ctx.send(f"✅ Abandoned quest: {quest_to_remove['title']}")
            else:
                await ctx.send("❌ Quest not found!")

        else:
            await ctx.send("❌ Invalid action! Use `new`, `abandon`, or `complete`.")

    # ============= FACTION SYSTEM =============

    @commands.command(name='faction', help='Join or view faction information')
    async def faction_command(self, ctx, faction_name: str = None):
        """Faction system."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        from utils.constants import FACTIONS
        from utils.helpers import format_faction_info

        if not faction_name:
            # Show all factions
            embed = discord.Embed(
                title="⚔️ Factions",
                description="Choose your allegiance wisely!",
                color=COLORS['primary']
            )

            for faction_key, faction_data in FACTIONS.items():
                embed.add_field(
                    name=f"{faction_data['name']} ({faction_key})",
                    value=f"{faction_data['description']}\n"
                          f"Alignment: {faction_data['alignment'].title()}",
                    inline=False
                )

            current_faction = player_data.get('faction')
            if current_faction:
                embed.add_field(
                    name="Current Faction",
                    value=FACTIONS[current_faction]['name'],
                    inline=False
                )
            else:
                embed.set_footer(text="Use $faction <name> to join a faction!")

            await ctx.send(embed=embed)
            return

        faction_name = faction_name.lower().replace(' ', '_')
        if faction_name not in FACTIONS:
            await ctx.send(f"❌ Invalid faction! Use `$faction` to see available factions.")
            return

        current_faction = player_data.get('faction')
        if current_faction:
            await ctx.send(f"❌ You're already in a faction: {FACTIONS[current_faction]['name']}")
            return

        # Join faction
        player_data['faction'] = faction_name
        update_user_rpg_data(user_id, player_data)

        faction_info = format_faction_info(faction_name)
        embed = create_embed(
            f"⚔️ Joined {FACTIONS[faction_name]['name']}!",
            f"{faction_info}\n\n"
            f"You now have access to faction perks and special quests!",
            COLORS['success']
        )

        await ctx.send(embed=embed)

    # ============= PARTY SYSTEM =============

    @commands.command(name='party', help='Party management (create, invite, leave, disband)')
    async def party_command(self, ctx, action: str = None, member: discord.Member = None):
        """Party system for multiplayer adventures."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        from utils.database import get_party_data, update_party_data, create_party

        if not action:
            # Show party info
            party_id = player_data.get('party_id')
            if not party_id:
                await ctx.send("❌ You're not in a party! Use `$party create` to create one.")
                return

            party_data = get_party_data(party_id)
            if not party_data:
                await ctx.send("❌ Party data not found!")
                return

            embed = discord.Embed(
                title=f"👥 {party_data['name']}",
                description=f"Party Leader: <@{party_data['leader_id']}>",
                color=COLORS['primary']
            )

            members_text = ""
            for member_id in party_data['members']:
                try:
                    user = self.bot.get_user(int(member_id))
                    name = user.display_name if user else "Unknown User"
                    members_text += f"• {name}\n"
                except:
                    members_text += f"• Unknown User\n"

            embed.add_field(
                name=f"Members ({len(party_data['members'])}/{party_data['max_members']})",
                value=members_text,
                inline=False
            )

            await ctx.send(embed=embed)
            return

        if action.lower() == 'create':
            if player_data.get('party_id'):
                await ctx.send("❌ You're already in a party!")
                return

            party_id = create_party(user_id, f"{ctx.author.display_name}'s Party")
            if party_id:
                player_data['party_id'] = party_id
                update_user_rpg_data(user_id, player_data)
                await ctx.send(f"✅ Created party: {ctx.author.display_name}'s Party")
            else:
                await ctx.send("❌ Failed to create party!")

        elif action.lower() == 'invite':
            if not member:
                await ctx.send("❌ Mention a user to invite!")
                return

            party_id = player_data.get('party_id')
            if not party_id:
                await ctx.send("❌ You're not in a party!")
                return

            party_data = get_party_data(party_id)
            if party_data['leader_id'] != user_id:
                await ctx.send("❌ Only the party leader can invite members!")
                return

            target_data = get_user_rpg_data(str(member.id))
            if not target_data:
                await ctx.send("❌ Target user hasn't started their adventure!")
                return

            if target_data.get('party_id'):
                await ctx.send("❌ That user is already in a party!")
                return

            if len(party_data['members']) >= party_data['max_members']:
                await ctx.send("❌ Party is full!")
                return

            # Simple invite system - just add to party
            party_data['members'].append(str(member.id))
            target_data['party_id'] = party_id

            update_party_data(party_id, party_data)
            update_user_rpg_data(str(member.id), target_data)

            await ctx.send(f"✅ {member.mention} has been invited to the party!")

        elif action.lower() == 'leave':
            party_id = player_data.get('party_id')
            if not party_id:
                await ctx.send("❌ You're not in a party!")
                return

            party_data = get_party_data(party_id)

            if party_data['leader_id'] == user_id:
                await ctx.send("❌ You're the party leader! Use `$party disband` to disband the party.")
                return

            party_data['members'].remove(user_id)
            player_data['party_id'] = None

            update_party_data(party_id, party_data)
            update_user_rpg_data(user_id, player_data)

            await ctx.send("✅ You left the party!")

        else:
            await ctx.send("❌ Invalid action! Use: create, invite, leave, disband")

    # ============= LEGACY SYSTEM =============

    @commands.command(name='legacy', help='View your legacy modifiers and achievements')
    async def legacy_command(self, ctx):
        """View legacy system."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        legacy_modifiers = player_data.get('legacy_modifiers', [])
        achievements = player_data.get('achievements', [])
        titles = player_data.get('titles', [])
        active_title = player_data.get('active_title')

        embed = discord.Embed(
            title="🌟 Your Legacy",
            description="Your journey through the ages has left its mark...",
            color=COLORS['warning']
        )

        if legacy_modifiers:
            from utils.constants import LEGACY_MODIFIERS
            legacy_text = ""
            for modifier in legacy_modifiers:
                if modifier in LEGACY_MODIFIERS:
                    data = LEGACY_MODIFIERS[modifier]
                    legacy_text += f"✨ **{data['name']}** - {data['description']}\n"

            embed.add_field(name="Legacy Modifiers", value=legacy_text, inline=False)

        if achievements:
            achievements_text = "\n".join([f"🏆 {achievement}" for achievement in achievements[:5]])
            if len(achievements) > 5:
                achievements_text += f"\n... and {len(achievements) - 5} more"
            embed.add_field(name="Achievements", value=achievements_text, inline=False)

        if titles:
            titles_text = "\n".join([f"🎖️ {title}" for title in titles])
            if active_title:
                titles_text += f"\n\n**Active Title:** {active_title}"
            embed.add_field(name="Titles", value=titles_text, inline=False)

        if not legacy_modifiers and not achievements and not titles:
            embed.add_field(
                name="No Legacy Yet",
                value="Complete achievements and unlock your legacy!",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='prestige', help='Reset your character for exclusive bonuses')
    async def prestige_command(self, ctx):
        """Prestige system."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        level = player_data.get('level', 1)
        prestige_level = player_data.get('prestige_level', 0)

        from utils.helpers import calculate_prestige_cost

        if level < RPG_CONSTANTS['prestige_level']:
            await ctx.send(f"❌ You need to reach level {RPG_CONSTANTS['prestige_level']} to prestige!")
            return

        cost = calculate_prestige_cost(level)
        coins = player_data.get('coins', 0)

        if coins < cost:
            await ctx.send(f"❌ Prestige costs {format_number(cost)} coins! You have {format_number(coins)}.")
            return

        embed = discord.Embed(
            title="⭐ Prestige Warning",
            description=f"Prestiging will reset your character to level 1 but grant you:\n\n"
                       f"• **Prestige Level:** {prestige_level + 1}\n"
                       f"• **Legacy Modifier:** Random powerful bonus\n"
                       f"• **Prestige Title:** Exclusive title\n"
                       f"• **Stat Bonus:** +5 to all base stats\n\n"
                       f"**Cost:** {format_number(cost)} coins\n\n"
                       f"Are you sure you want to prestige?",
            color=COLORS['warning']
        )

        # Add confirmation buttons here (simplified for now)
        await ctx.send(embed=embed)
        await ctx.send("Type `yes` to confirm prestige or `no` to cancel.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
            if response.content.lower() == 'yes':
                # Perform prestige
                from utils.constants import LEGACY_MODIFIERS

                # Reset character but keep certain things
                legacy_modifiers = player_data.get('legacy_modifiers', [])
                achievements = player_data.get('achievements', [])
                titles = player_data.get('titles', [])

                # Add prestige benefits
                prestige_level += 1
                legacy_modifiers.append('descendant_of_heroes')  # Example legacy modifier
                titles.append(f'Prestige {prestige_level}')

                # Reset stats with prestige bonus
                base_stats = 10 + (prestige_level * 5)  # +5 per prestige level

                player_data.update({
                    'level': 1,
                    'xp': 0,
                    'max_xp': 100,
                    'hp': 100 + (prestige_level * 20),
                    'max_hp': 100 + (prestige_level * 20),
                    'attack': base_stats,
                    'defense': base_stats // 2,
                    'mana': 50 + (prestige_level * 10),
                    'max_mana': 50 + (prestige_level * 10),
                    'coins': coins - cost,
                    'prestige_level': prestige_level,
                    'legacy_modifiers': legacy_modifiers,
                    'achievements': achievements,
                    'titles': titles
                })

                update_user_rpg_data(user_id, player_data)

                embed = create_embed(
                    f"⭐ Prestige {prestige_level} Achieved!",
                    f"Your character has been reborn with greater power!\n\n"
                    f"**New Stats:**\n"
                    f"• Base Attack/Defense: {base_stats}/{base_stats//2}\n"
                    f"• HP: {100 + (prestige_level * 20)}\n"
                    f"• Mana: {50 + (prestige_level * 10)}\n"
                    f"• New Title: Prestige {prestige_level}",
                    COLORS['success']
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Prestige cancelled.")
        except asyncio.TimeoutError:
            await ctx.send("❌ Prestige timed out.")

    # ============= MINI-GAMES =============

    @commands.command(name='fish', help='Fish in cheese ponds for rare aquatic pets')
    async def fish_command(self, ctx):
        """Cheese pond fishing mini-game."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        from utils.constants import MINI_GAMES
        game_data = MINI_GAMES['cheese_fishing']
        cost = game_data['cost']
        coins = player_data.get('coins', 0)

        if coins < cost:
            await ctx.send(f"❌ Fishing costs {cost} coins! You have {coins} coins.")
            return

        # Simple fishing simulation
        from utils.rng_system import roll_with_luck

        player_data['coins'] = coins - cost

        results = []

        # Multiple fishing attempts
        for _ in range(3):
            if roll_with_luck(user_id, 0.3):  # 30% base chance
                fish_types = ['cheese_trout', 'camembert_bass', 'gouda_goldfish', 'rare_brie_shark']
                caught_fish = random.choice(fish_types)
                results.append(caught_fish)

                inventory = player_data.get('inventory', [])
                inventory.append(caught_fish)
                player_data['inventory'] = inventory

        # Rare pet chance
        if roll_with_luck(user_id, 0.05):  # 5% chance for pet
            pet_types = ['aquatic_kwami', 'cheese_dolphin', 'miraculous_seahorse']
            caught_pet = random.choice(pet_types)
            results.append(f"🐾 {caught_pet} (Pet!)")

            pets = player_data.get('pets', [])
            pets.append(caught_pet)
            player_data['pets'] = pets

        update_user_rpg_data(user_id, player_data)

        if results:
            results_text = "\n".join([f"🐟 {result}" for result in results])
            embed = create_embed(
                "🎣 Fishing Complete!",
                f"You cast your line into the magical cheese pond...\n\n"
                f"**Caught:**\n{results_text}",
                COLORS['success']
            )
        else:
            embed = create_embed(
                "🎣 Fishing Complete!",
                "The fish weren't biting today. Better luck next time!",
                COLORS['warning']
            )

        await ctx.send(embed=embed)

    @commands.command(name='trivia', help="Test your knowledge with Plagg's cheese trivia")
    async def trivia_command(self, ctx):
        """Plagg's cheese trivia mini-game."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        from utils.constants import MINI_GAMES
        game_data = MINI_GAMES['plagg_trivia']
        cost = game_data['cost']
        coins = player_data.get('coins', 0)

        if coins < cost:
            await ctx.send(f"❌ Trivia costs {cost} coins! You have {coins} coins.")
            return

        # Cheese/Miraculous trivia questions
        questions = [
            {"q": "What is Plagg's favorite type of cheese?", "a": "camembert", "options": ["cheddar", "camembert", "gouda", "brie"]},
            {"q": "Which kwami represents destruction?", "a": "plagg", "options": ["tikki", "plagg", "wayzz", "nooroo"]},
            {"q": "What miraculous does Adrien use?", "a": "cat", "options": ["ladybug", "cat", "turtle", "butterfly"]},
            {"q": "What country is famous for camembert?", "a": "france", "options": ["italy", "france", "germany", "spain"]},
            {"q": "What is Tikki's favorite food?", "a": "cookies", "options": ["cheese", "cookies", "bread", "cake"]}
        ]

        question = random.choice(questions)

        embed = discord.Embed(
            title="🧀 Plagg's Cheese Trivia",
            description=f"**Question:** {question['q']}\n\n" +
                       "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(question['options'])]),
            color=COLORS['warning']
        )

        await ctx.send(embed=embed)
        await ctx.send("Type the number of your answer (1-4):")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

        try:
            response = await self.bot.wait_for('message', check=check, timeout=15.0)
            answer_index = int(response.content) - 1

            if 0 <= answer_index < len(question['options']):
                chosen_answer = question['options'][answer_index]

                player_data['coins'] = coins - cost

                if chosen_answer.lower() == question['a']:
                    # Correct answer
                    reward_coins = random.randint(50, 150)
                    reward_xp = random.randint(10, 30)

                    player_data['coins'] += reward_coins
                    player_data['xp'] = player_data.get('xp', 0) + reward_xp

                    embed = create_embed(
                        "🎉 Correct Answer!",
                        f"Plagg is impressed with your cheese knowledge!\n\n"
                        f"**Rewards:**\n"
                        f"• {reward_coins} coins\n"
                        f"• {reward_xp} XP",
                        COLORS['success']
                    )
                else:
                    # Wrong answer
                    embed = create_embed(
                        "❌ Wrong Answer!",
                        f"The correct answer was: **{question['a']}**\n\n"
                        f"Plagg says: 'You need to study more about cheese!'",
                        COLORS['error']
                    )

                update_user_rpg_data(user_id, player_data)
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Invalid answer number!")

        except asyncio.TimeoutError:
            await ctx.send("❌ Time's up! The trivia has ended.")
        except ValueError:
            await ctx.send("❌ Please enter a valid number!")

    # ============= AUCTION HOUSE =============

    @commands.command(name='auction', help='Access the auction house (list, bid, sell)')
    async def auction_command(self, ctx, action: str = None, *, args: str = None):
        """Auction house system."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        from utils.database import get_auction_listings, add_auction_listing

        if not action or action.lower() == 'list':
            # Show current listings
            listings = get_auction_listings()
            active_listings = [l for l in listings if l['status'] == 'active']

            if not active_listings:
                await ctx.send("🏛️ The auction house is empty! Use `$auction sell <item> <price>` to list items.")
                return

            embed = discord.Embed(
                title="🏛️ Auction House",
                description="Current listings (use $auction bid <listing_id> to bid):",
                color=COLORS['warning']
            )

            for listing in active_listings[:5]:  # Show first 5 listings
                try:
                    seller = self.bot.get_user(int(listing['seller_id']))
                    seller_name = seller.display_name if seller else "Unknown"

                    embed.add_field(
                        name=f"ID: {listing['listing_id']} - {listing['item_name']}",
                        value=f"Price: {format_number(listing['price'])} coins\n"
                              f"Seller: {seller_name}\n"
                              f"Bids: {len(listing['bids'])}",
                        inline=True
                    )
                except:
                    continue

            await ctx.send(embed=embed)

        elif action.lower() == 'sell':
            if not args:
                await ctx.send("❌ Usage: `$auction sell <item_name> <price>`")
                return

            try:
                parts = args.rsplit(' ', 1)
                if len(parts) != 2:
                    raise ValueError()

                item_name, price_str = parts
                price = int(price_str)

                if price <= 0:
                    raise ValueError()

            except ValueError:
                await ctx.send("❌ Invalid format! Use: `$auction sell <item_name> <price>`")
                return

            player_data = get_user_rpg_data(user_id)
            inventory = player_data.get('inventory', [])

            if item_name not in inventory:
                await ctx.send(f"❌ You don't have **{item_name}** in your inventory!")
                return

            # Remove item from inventory and add to auction
            inventory.remove(item_name)
            player_data['inventory'] = inventory
            update_user_rpg_data(user_id, player_data)

            if add_auction_listing(user_id, item_name, price):
                await ctx.send(f"✅ Listed **{item_name}** for {format_number(price)} coins!")
            else:
                # Return item if listing failed
                inventory.append(item_name)
                player_data['inventory'] = inventory
                update_user_rpg_data(user_id, player_data)
                await ctx.send("❌ Failed to list item!")

        else:
            await ctx.send("❌ Invalid action! Use: list, sell, bid")

        if get_user_rpg_data(user_id):
            await ctx.send("❌ You've already started your adventure! Use `$profile` to see your stats.")
            return

        # Create new user profile
        if create_user_profile(user_id):
            embed = create_embed(
                "🎉 Adventure Started!",
                f"Welcome to your RPG adventure, {ctx.author.mention}!\n\n"
                f"**Starting Stats:**\n"
                f"• Level: 1\n"
                f"• HP: 100/100\n"
                f"• Attack: 10\n"
                f"• Defense: 5\n"
                f"• Coins: 100\n\n"
                f"Use `$profile` to view your character\n"
                f"Use `$adventure` to start exploring\n"
                f"Use `$work` to earn coins\n"
                f"Use `$shop` to buy equipment",
                COLORS['success']
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to start your adventure. Please try again.")

    @commands.command(name='inventory', help='View your inventory')
    async def inventory_command(self, ctx):
        """View player inventory."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        inventory = player_data.get('inventory', [])
        equipped = player_data.get('equipped', {})

        embed = create_embed(
            f"🎒 {ctx.author.display_name}'s Inventory",
            f"Items: {len(inventory)}/50",
            COLORS['secondary']
        )

        # Show equipped items
        weapon = equipped.get('weapon', 'None')
        armor = equipped.get('armor', 'None')
        accessory = equipped.get('accessory', 'None')

        embed.add_field(
            name="🔧 Equipped",
            value=f"**Weapon:** {weapon}\n**Armor:** {armor}\n**Accessory:** {accessory}",
            inline=False
        )

        # Show inventory items
        if inventory:
            items_text = ""
            for i, item in enumerate(inventory[:20]):  # Show first 20 items
                items_text += f"• {item}\n"
            if len(inventory) > 20:
                items_text += f"... and {len(inventory) - 20} more items"
        else:
            items_text = "Your inventory is empty!"

        embed.add_field(
            name="📦 Items",
            value=items_text,
            inline=False
        )

        await ctx.send(embed=embed)

    @commands.command(name='battle', help='Battle a monster')
    async def battle_command(self, ctx, *, target: str = None):
        """Battle a monster or player."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        if player_data.get('hp', 100) <= 0:
            await ctx.send("❌ You are defeated! Use `$heal` to recover.")
            return

        # Generate random enemy
        enemies = [
            {"name": "Goblin", "hp": 50, "attack": 8, "defense": 3},
            {"name": "Orc", "hp": 80, "attack": 12, "defense": 5},
            {"name": "Dragon", "hp": 150, "attack": 20, "defense": 10}
        ]

        enemy = random.choice(enemies)
        enemy["max_hp"] = enemy["hp"]

        view = BattleView(user_id, enemy)
        embed = discord.Embed(
            title=f"⚔️ Battle vs {enemy['name']}",
            description=f"A wild {enemy['name']} appears!",
            color=COLORS['warning']
        )

        embed.add_field(
            name="Your Stats",
            value=f"HP: {player_data.get('hp', 100)}/{player_data.get('max_hp', 100)}\n"
                  f"Attack: {player_data.get('attack', 10)}\n"
                  f"Defense: {player_data.get('defense', 5)}",
            inline=True
        )

        embed.add_field(
            name=f"{enemy['name']} Stats",
            value=f"HP: {enemy['hp']}/{enemy['max_hp']}\n"
                  f"Attack: {enemy['attack']}\n"
                  f"Defense: {enemy['defense']}",
            inline=True
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(name='profile', help='View your character profile')
    async def profile_command(self, ctx, member: Optional[discord.Member] = None):
        """View character profile."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        target = member or ctx.author
        user_id = str(target.id)

        if not ensure_user_exists(user_id):
            await ctx.send(f"❌ {target.display_name} hasn't started their adventure yet!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve profile data.")
            return

        view = ProfileView(target, player_data)
        embed = view.create_stats_embed()

        await ctx.send(embed=embed, view=view)

    @commands.command(name='adventure', help='Go on an adventure')
    @commands.cooldown(1, RPG_CONSTANTS['adventure_cooldown'], commands.BucketType.user)
    async def adventure_command(self, ctx):
        """Go on an adventure."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first! Use `$start` command.")
            return

        view = AdventureView(user_id)
        embed = create_embed(
            "🗺️ Choose Your Adventure",
            "Select a location to explore!\n\n"
            "Each location offers different rewards and challenges.",
            COLORS['primary']
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(name='work', help='Work to earn coins')
    @commands.cooldown(1, RPG_CONSTANTS['work_cooldown'], commands.BucketType.user)
    async def work_command(self, ctx):
        """Work to earn coins."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first! Use `$start` command.")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        # Work jobs
        jobs = [
            {"name": "Mining", "coins": (50, 100), "xp": (5, 15)},
            {"name": "Farming", "coins": (30, 80), "xp": (3, 10)},
            {"name": "Trading", "coins": (70, 120), "xp": (8, 20)},
            {"name": "Blacksmithing", "coins": (60, 110), "xp": (6, 18)}
        ]

        job = random.choice(jobs)
        coins_earned = random.randint(*job['coins'])
        xp_earned = random.randint(*job['xp'])

        # Apply luck bonus
        enhanced_rewards = generate_loot_with_luck(user_id, {
            'coins': coins_earned,
            'xp': xp_earned
        })

        player_data['coins'] = player_data.get('coins', 0) + enhanced_rewards['coins']
        player_data['xp'] = player_data.get('xp', 0) + enhanced_rewards['xp']
        player_data['work_count'] = player_data.get('work_count', 0) + 1

        # Check for level up
        level_up_msg = level_up_player(player_data)

        update_user_rpg_data(user_id, player_data)

        embed = create_embed(
            f"💼 Work Complete - {job['name']}",
            f"You worked hard and earned rewards!\n\n"
            f"**Rewards:**\n"
            f"Coins: {format_number(enhanced_rewards['coins'])}\n"
            f"XP: {enhanced_rewards['xp']}",
            COLORS['success']
        )

        if level_up_msg:
            embed.add_field(name="📊 Level Up!", value=level_up_msg, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='shop', help='Browse the interactive shop')
    async def shop_command(self, ctx):
        """Browse the interactive shop."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first! Use `$start` command.")
            return

        view = ShopView(user_id)
        embed = view.create_shop_embed()

        await ctx.send(embed=embed, view=view)

    @commands.command(name='reload_shop', help='Reload shop data (Admin only)')
    @commands.has_permissions(administrator=True)
    async def reload_shop_command(self, ctx):
        """Reload shop data to fix duplicates."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        from utils.helpers import clear_item_cache, validate_shop_data
        from utils.constants import get_all_shop_items

        # Clear cache
        clear_item_cache()

        # Validate data
        validation = validate_shop_data()

        # Get fresh data count
        all_items = get_all_shop_items()

        embed = create_embed(
            "🔄 Shop Data Reloaded",
            f"**Status:** {'✅ Valid' if validation['valid'] else '❌ Issues Found'}\n"
            f"**Total Items:** {validation['total_items']}\n"
            f"**Unique Items Loaded:** {len(all_items)}",
            COLORS['success'] if validation['valid'] else COLORS['warning']
        )

        if validation['missing_data']:
            embed.add_field(
                name="⚠️ Issues Found",
                value="\n".join(validation['missing_data'][:5]),
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='profile', help='View your character profile')
    async def profile_command(self, ctx, member: Optional[discord.Member] = None):
        """View character profile."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        target = member or ctx.author
        user_id = str(target.id)

        if not ensure_user_exists(user_id):
            await ctx.send(f"❌ {target.display_name} hasn't started their adventure yet!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve profile data.")
            return

        view = ProfileView(target, player_data)
        embed = view.create_stats_embed()

        await ctx.send(embed=embed, view=view)

    @commands.command(name='adventure', help='Go on an adventure')
    @commands.cooldown(1, RPG_CONSTANTS['adventure_cooldown'], commands.BucketType.user)
    async def adventure_command(self, ctx):
        """Go on an adventure."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first! Use `$start` command.")
            return

        view = AdventureView(user_id)
        embed = create_embed(
            "🗺️ Choose Your Adventure",
            "Select a location to explore!\n\n"
            "Each location offers different rewards and challenges.",
            COLORS['primary']
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(name='work', help='Work to earn coins')
    @commands.cooldown(1, RPG_CONSTANTS['work_cooldown'], commands.BucketType.user)
    async def work_command(self, ctx):
        """Work to earn coins."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first! Use `$start` command.")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        # Work jobs
        jobs = [
            {"name": "Mining", "coins": (50, 100), "xp": (5, 15)},
            {"name": "Farming", "coins": (30, 80), "xp": (3, 10)},
            {"name": "Trading", "coins": (70, 120), "xp": (8, 20)},
            {"name": "Blacksmithing", "coins": (60, 110), "xp": (6, 18)}
        ]

        job = random.choice(jobs)
        coins_earned = random.randint(*job['coins'])
        xp_earned = random.randint(*job['xp'])

        # Apply luck bonus
        enhanced_rewards = generate_loot_with_luck(user_id, {
            'coins': coins_earned,
            'xp': xp_earned
        })

        player_data['coins'] = player_data.get('coins', 0) + enhanced_rewards['coins']
        player_data['xp'] = player_data.get('xp', 0) + enhanced_rewards['xp']
        player_data['work_count'] = player_data.get('work_count', 0) + 1

        # Check for level up
        level_up_msg = level_up_player(player_data)

        update_user_rpg_data(user_id, player_data)

        embed = create_embed(
            f"💼 Work Complete - {job['name']}",
            f"You worked hard and earned rewards!\n\n"
            f"**Rewards:**\n"
            f"Coins: {format_number(enhanced_rewards['coins'])}\n"
            f"XP: {enhanced_rewards['xp']}",
            COLORS['success']
        )

        if level_up_msg:
            embed.add_field(name="📊 Level Up!", value=level_up_msg, inline=False)

        await ctx.send(embed=embed)

    

    @commands.command(name='buy', help='Buy an item from the shop by name')
    async def buy_command(self, ctx, *, item_name: str):
        """Buy an item directly by name."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        from utils.constants import SHOP_ITEMS

        # Find item in shop
        item_data = None
        item_id = None
        for shop_id, shop_item in SHOP_ITEMS.items():
            if shop_item.get('name', '').lower() == item_name.lower():
                item_data = shop_item
                item_id = shop_id
                break

        if not item_data:
            # Show available items with similar names
            similar_items = []
            for shop_item in SHOP_ITEMS.values():
                if item_name.lower() in shop_item.get('name', '').lower():
                    similar_items.append(shop_item['name'])
            
            error_msg = f"❌ **{item_name}** is not available in the shop!"
            if similar_items:
                error_msg += f"\n\n**Did you mean:**\n" + "\n".join([f"• {item}" for item in similar_items[:5]])
            error_msg += f"\n\n💡 Use `$shop` for the interactive shop interface!"
            
            await ctx.send(error_msg)
            return

        price = item_data.get('price', 0)
        coins = player_data.get('coins', 0)

        if coins < price:
            await ctx.send(f"❌ **Insufficient funds!**\n"
                          f"You need **{format_number(price)}** coins but only have **{format_number(coins)}**.\n"
                          f"You need **{format_number(price - coins)}** more coins!")
            return

        # Purchase item
        player_data['coins'] = coins - price
        inventory = player_data.get('inventory', [])
        inventory.append(item_data['name'])
        player_data['inventory'] = inventory

        # Update stats
        stats = player_data.get('stats', {})
        stats['items_purchased'] = stats.get('items_purchased', 0) + 1
        player_data['stats'] = stats

        update_user_rpg_data(user_id, player_data)

        # Create detailed purchase confirmation
        rarity = item_data.get('rarity', 'common')
        emoji = get_rarity_emoji(rarity)
        color = RARITY_COLORS.get(rarity, COLORS['success'])

        embed = discord.Embed(
            title="🛒 Purchase Successful!",
            description=f"You bought **{emoji} {item_data['name']}** for {format_number(price)} coins!",
            color=color
        )

        embed.add_field(
            name="💰 Transaction Summary",
            value=f"**Item:** {item_data['name']}\n"
                  f"**Price:** {format_number(price)} coins\n"
                  f"**Remaining Coins:** {format_number(coins - price)}",
            inline=True
        )

        # Show item stats if available
        stats_text = ""
        if item_data.get('attack'):
            stats_text += f"⚔️ Attack: +{item_data['attack']}\n"
        if item_data.get('defense'):
            stats_text += f"🛡️ Defense: +{item_data['defense']}\n"
        if item_data.get('effect'):
            effect_desc = item_data['effect'].replace('_', ' ').title()
            stats_text += f"✨ Effect: {effect_desc}\n"

        if stats_text:
            embed.add_field(name="📊 Item Properties", value=stats_text, inline=True)

        embed.add_field(
            name="📦 Next Steps",
            value="• Check `$inventory` to see your new item\n"
                  "• Use `$equip <item>` for weapons/armor\n"
                  "• Use `$use <item>` for consumables",
            inline=False
        )

        embed.set_footer(text="💡 Use $shop for the interactive shopping experience!")
        await ctx.send(embed=embed)

    @commands.command(name='use', help='Use a consumable item')
    async def use_command(self, ctx, *, item_name: str):
        """Use a consumable item."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        inventory = player_data.get('inventory', [])

        if item_name not in inventory:
            await ctx.send(f"❌ You don't have **{item_name}** in your inventory!")
            return

        # Define item effects
        item_effects = {
            "Health Potion": {"type": "heal", "amount": 50},
            "Golden Elixir": {"type": "heal", "amount": 500},
            "Mana Potion": {"type": "mana", "amount": 50},
            "Lucky Charm": {"type": "luck", "amount": 100, "duration": 3600},
            "XP Boost": {"type": "xp_boost", "multiplier": 2, "duration": 1800},
            "Phoenix Feather": {"type": "revive", "amount": 100}
        }

        if item_name not in item_effects:
            # Check if it's equipment
            from utils.constants import SHOP_ITEMS
            item_data = None
            for shop_item in SHOP_ITEMS.values():
                if shop_item.get('name') == item_name:
                    item_data = shop_item
                    break
            
            if item_data and item_data.get('category') in ['weapons', 'armor']:
                await ctx.send(f"❌ **{item_name}** is equipment! Use `$equip {item_name}` instead.")
                return
            
            await ctx.send(f"❌ **{item_name}** cannot be used!")
            return

        effect = item_effects[item_name]
        
        # Apply effects
        if effect["type"] == "heal":
            hp = player_data.get('hp', 100)
            max_hp = player_data.get('max_hp', 100)

            if hp >= max_hp:
                await ctx.send("❌ You're already at full health!")
                return

            heal_amount = min(effect["amount"], max_hp - hp)
            player_data['hp'] = hp + heal_amount

            await ctx.send(f"❤️ You used **{item_name}** and restored {heal_amount} HP!")

        elif effect["type"] == "mana":
            mana = player_data.get('mana', 50)
            max_mana = player_data.get('max_mana', 50)

            if mana >= max_mana:
                await ctx.send("❌ Your mana is already full!")
                return

            mana_amount = min(effect["amount"], max_mana - mana)
            player_data['mana'] = mana + mana_amount

            await ctx.send(f"💙 You used **{item_name}** and restored {mana_amount} mana!")

        elif effect["type"] == "revive":
            hp = player_data.get('hp', 100)
            if hp > 0:
                await ctx.send("❌ You don't need to be revived!")
                return

            player_data['hp'] = effect["amount"]
            await ctx.send(f"🔥 **{item_name}** brought you back to life with {effect['amount']} HP!")

        elif effect["type"] == "luck":
            luck_points = player_data.get('luck_points', 0)
            player_data['luck_points'] = luck_points + effect["amount"]
            await ctx.send(f"🍀 You used **{item_name}** and gained {effect['amount']} luck points!")

        elif effect["type"] == "xp_boost":
            # Add temporary boost (would need a separate system to track)
            await ctx.send(f"✨ You used **{item_name}**! XP gain doubled for the next 30 minutes!")

        # Remove item from inventory
        inventory.remove(item_name)
        player_data['inventory'] = inventory

        # Update stats
        stats = player_data.get('stats', {})
        stats['items_used'] = stats.get('items_used', 0) + 1
        player_data['stats'] = stats

        update_user_rpg_data(user_id, player_data)

    @commands.command(name='equip', help='Equip weapons, armor, or accessories')
    async def equip_command(self, ctx, *, item_name: str):
        """Equip weapons, armor, or accessories."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        if not player_data:
            await ctx.send("❌ Could not retrieve your data.")
            return

        inventory = player_data.get('inventory', [])

        if item_name not in inventory:
            await ctx.send(f"❌ You don't have **{item_name}** in your inventory!")
            return

        # Find item data
        from utils.constants import SHOP_ITEMS, WEAPONS, ARMOR
        item_data = None
        item_type = None

        # Check shop items first
        for shop_item in SHOP_ITEMS.values():
            if shop_item.get('name') == item_name:
                item_data = shop_item
                item_type = shop_item.get('category')
                break

        # Check weapons
        if not item_data and item_name in WEAPONS:
            item_data = WEAPONS[item_name]
            item_type = 'weapons'

        # Check armor
        if not item_data and item_name in ARMOR:
            item_data = ARMOR[item_name]
            item_type = 'armor'

        if not item_data:
            await ctx.send(f"❌ **{item_name}** cannot be equipped!")
            return

        if item_type not in ['weapons', 'armor', 'accessories']:
            await ctx.send(f"❌ **{item_name}** is not equipment!")
            return

        # Get current equipment
        equipped = player_data.get('equipped', {})
        
        # Map categories to equipment slots
        slot_mapping = {
            'weapons': 'weapon',
            'armor': 'armor', 
            'accessories': 'accessory'
        }
        
        slot = slot_mapping.get(item_type, item_type.rstrip('s'))

        # Unequip current item if any
        old_item = equipped.get(slot)
        if old_item and old_item != 'None':
            inventory.append(old_item)

        # Equip new item
        equipped[slot] = item_name
        inventory.remove(item_name)

        # Apply stat bonuses
        old_attack = player_data.get('attack', 10)
        old_defense = player_data.get('defense', 5)

        if item_data.get('attack'):
            player_data['attack'] = player_data.get('attack', 10) + item_data['attack']
        if item_data.get('defense'):
            player_data['defense'] = player_data.get('defense', 5) + item_data['defense']

        player_data['equipped'] = equipped
        player_data['inventory'] = inventory

        update_user_rpg_data(user_id, player_data)

        # Create equipment confirmation
        rarity = item_data.get('rarity', 'common')
        emoji = get_rarity_emoji(rarity)
        color = RARITY_COLORS.get(rarity, COLORS['success'])

        embed = discord.Embed(
            title="⚔️ Equipment Updated!",
            description=f"You equipped **{emoji} {item_name}**!",
            color=color
        )

        if old_item and old_item != 'None':
            embed.add_field(
                name="🔄 Equipment Change",
                value=f"**Unequipped:** {old_item}\n**Equipped:** {item_name}",
                inline=True
            )

        # Show stat changes
        stat_changes = []
        if item_data.get('attack'):
            stat_changes.append(f"⚔️ Attack: {old_attack} → {player_data.get('attack', 10)} (+{item_data['attack']})")
        if item_data.get('defense'):
            stat_changes.append(f"🛡️ Defense: {old_defense} → {player_data.get('defense', 5)} (+{item_data['defense']})")

        if stat_changes:
            embed.add_field(
                name="📊 Stat Changes",
                value="\n".join(stat_changes),
                inline=False
            )

        if item_data.get('effect'):
            embed.add_field(
                name="✨ Special Effect",
                value=item_data['effect'].replace('_', ' ').title(),
                inline=True
            )

        embed.set_footer(text="💡 Use $inventory to see your current equipment!")
        await ctx.send(embed=embed)

    @app_commands.command(name="pay", description="Pay coins to another user")
    @app_commands.describe(user="The user to pay", amount="Amount of coins to pay")
    async def pay_slash(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Pay coins to another user (slash command)."""
        if not is_module_enabled("rpg", interaction.guild_id):
            await interaction.response.send_message("❌ RPG module is disabled!", ephemeral=True)
            return

        if amount <= 0:
            await interaction.response.send_message("❌ Amount must be positive!", ephemeral=True)
            return

        if user.id == interaction.user.id:
            await interaction.response.send_message("❌ You can't pay yourself!", ephemeral=True)
            return

        sender_id = str(interaction.user.id)
        receiver_id = str(user.id)

        if not ensure_user_exists(sender_id):
            await interaction.response.send_message("❌ You need to start your adventure first!", ephemeral=True)
            return

        if not ensure_user_exists(receiver_id):
            await interaction.response.send_message("❌ The target user needs to start their adventure first!", ephemeral=True)
            return

        sender_data = get_user_rpg_data(sender_id)
        receiver_data = get_user_rpg_data(receiver_id)

        if not sender_data or not receiver_data:
            await interaction.response.send_message("❌ Could not retrieve user data!", ephemeral=True)
            return

        sender_coins = sender_data.get('coins', 0)
        if sender_coins < amount:
            await interaction.response.send_message(f"❌ You don't have enough coins! You have {format_number(sender_coins)} coins.", ephemeral=True)
            return

        # Transfer coins
        sender_data['coins'] = sender_coins - amount
        receiver_data['coins'] = receiver_data.get('coins', 0) + amount

        update_user_rpg_data(sender_id, sender_data)
        update_user_rpg_data(receiver_id, receiver_data)

        embed = create_embed(
            "💸 Payment Successful!",
            f"{interaction.user.mention} paid {format_number(amount)} coins to {user.mention}!",
            COLORS['success']
        )

        await interaction.response.send_message(embed=embed)

    @commands.command(name='pay', help='Pay coins to another user')
    async def pay_command(self, ctx, user: discord.Member, amount: int):
        """Pay coins to another user."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        if amount <= 0:
            await ctx.send("❌ Amount must be positive!")
            return

        if user.id == ctx.author.id:
            await ctx.send("❌ You can't pay yourself!")
            return

        sender_id = str(ctx.author.id)

    @commands.command(name='weapon', help='View detailed weapon information')
    async def weapon_command(self, ctx, *, weapon_name: str = None):
        """View weapon information and unlock conditions."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        if not weapon_name:
            # Show weapon categories
            embed = discord.Embed(
                title="⚔️ Weapon Categories",
                description="Available weapon types and rarities:",
                color=COLORS['primary']
            )

            from utils.constants import WEAPONS

            # Group by rarity
            rarity_groups = {}
            for name, data in WEAPONS.items():
                rarity = data.get('rarity', 'common')
                if rarity not in rarity_groups:
                    rarity_groups[rarity] = []
                rarity_groups[rarity].append(name)

            for rarity, weapons in rarity_groups.items():
                emoji = get_rarity_emoji(rarity)
                embed.add_field(
                    name=f"{emoji} {rarity.title()} Weapons",
                    value="\n".join([f"• {w}" for w in weapons[:5]]) + 
                          (f"\n... and {len(weapons)-5} more" if len(weapons) > 5 else ""),
                    inline=True
                )

            embed.set_footer(text="Use $weapon <name> to see detailed info about a specific weapon")
            await ctx.send(embed=embed)
            return

        # Show specific weapon info
        from utils.constants import WEAPONS, WEAPON_UNLOCK_CONDITIONS
        from utils.helpers import check_weapon_unlock_conditions, format_weapon_info

        if weapon_name not in WEAPONS:
            await ctx.send(f"❌ Weapon '{weapon_name}' not found! Use `$weapon` to see all weapons.")
            return

        weapon = WEAPONS[weapon_name]
        user_id = str(ctx.author.id)

        # Check unlock conditions
        can_unlock, unlock_msg = check_weapon_unlock_conditions(user_id, weapon_name)

        # Create embed
        rarity = weapon.get('rarity', 'common')
        color = RARITY_COLORS.get(rarity, COLORS['primary'])
        emoji = get_rarity_emoji(rarity)

        embed = discord.Embed(
            title=f"{emoji} {weapon_name}",
            description=format_weapon_info(weapon_name),
            color=color
        )

        # Add unlock conditions if any
        if weapon_name in WEAPON_UNLOCK_CONDITIONS:
            condition_info = WEAPON_UNLOCK_CONDITIONS[weapon_name]
            status_emoji = "✅" if can_unlock else "❌"
            embed.add_field(
                name=f"{status_emoji} Unlock Conditions",
                value=condition_info["description"],
                inline=False
            )

            if not can_unlock:
                embed.add_field(
                    name="❗ Missing Requirements",
                    value=unlock_msg,
                    inline=False
                )

        # Add special abilities
        if weapon.get('special'):
            special_text = weapon['special'].replace('_', ' ').title()
            if weapon.get('boss_damage'):
                special_text += f" (+{weapon['boss_damage']}% boss damage)"
            elif weapon.get('crit_chance'):
                special_text += f" (+{weapon['crit_chance']}% crit chance)"
            elif weapon.get('healing_power'):
                special_text += f" (+{weapon['healing_power']}% healing)"

            embed.add_field(
                name="✨ Special Effects",
                value=special_text,
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='chrono_unlock', help='Check Chrono Weave class unlock progress')
    async def chrono_unlock_command(self, ctx):
        """Check progress towards unlocking Chrono Weave class."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        from utils.helpers import check_chrono_weave_unlock

        can_unlock, status_msg = check_chrono_weave_unlock(user_id)

        embed = discord.Embed(
            title="⏰ Chrono Weave Class Unlock",
            description="Master of time manipulation and temporal magic",
            color=COLORS['warning']
        )

        # Requirements
        embed.add_field(
            name="📋 Requirements",
            value="1. Defeat Time Rift Dragon while level ≤30\n"
                  "2. Complete 'Chrono Whispers' quest\n"
                  "3. Collect all 3 Ancient Relics",
            inline=False
        )

        # Status
        status_emoji = "✅" if can_unlock else "❌"
        embed.add_field(
            name=f"{status_emoji} Current Status",
            value=status_msg,
            inline=False
        )

        if can_unlock:
            embed.add_field(
                name="🎉 Ready to Unlock!",
                value="Use `$class chrono_weave` to unlock this hidden class!",
                inline=False
            )

        await ctx.send(embed=embed)

        receiver_id = str(user.id)

        if not ensure_user_exists(sender_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        if not ensure_user_exists(receiver_id):
            await ctx.send("❌ The target user needs to start their adventure first!")
            return

        sender_data = get_user_rpg_data(sender_id)
        receiver_data = get_user_rpg_data(receiver_id)

        if not sender_data or not receiver_data:
            await ctx.send("❌ Could not retrieve user data!")
            return

        sender_coins = sender_data.get('coins', 0)
        if sender_coins < amount:
            await ctx.send(f"❌ You don't have enough coins! You have {format_number(sender_coins)} coins.")
            return

        # Transfer coins
        sender_data['coins'] = sender_coins - amount
        receiver_data['coins'] = receiver_data.get('coins', 0) + amount

        update_user_rpg_data(sender_id, sender_data)
        update_user_rpg_data(receiver_id, receiver_data)

        embed = create_embed(
            "💸 Payment Successful!",
            f"{ctx.author.mention} paid {format_number(amount)} coins to {user.mention}!",
            COLORS['success']
        )

        await ctx.send(embed=embed)

    @commands.command(name='pay', help='Pay coins to another user')
    async def pay_command(self, ctx, member: discord.Member, amount: int):
        """Pay coins to another user."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        target_id = str(member.id)

        if not ensure_user_exists(user_id) or not ensure_user_exists(target_id):
            await ctx.send("❌ Both users need to start their adventure first!")
            return

        player_data = get_user_rpg_data(user_id)
        target_data = get_user_rpg_data(target_id)

        if not player_data or not target_data:
            await ctx.send("❌ Could not retrieve user data.")
            return

        coins = player_data.get('coins', 0)

        if amount <= 0:
            await ctx.send("❌ Amount must be positive!")
            return

        if coins < amount:
            await ctx.send(f"❌ You don't have enough coins! You have {coins} coins.")
            return

        # Perform the transaction
        player_data['coins'] = coins - amount
        target_data['coins'] = target_data.get('coins', 0) + amount

        update_user_rpg_data(user_id, player_data)
        update_user_rpg_data(target_id, target_data)

        embed = create_embed(
            "💰 Payment Sent!",
            f"You paid {member.mention} {amount} coins!",
            COLORS['success']
        )

        await ctx.send(embed=embed)

    @commands.command(name='lootbox', help='Open a lootbox for random rewards')
    async def lootbox_command(self, ctx):
        """Open a lootbox."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)

        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        view = LootboxView(user_id)
        embed = discord.Embed(
            title="🎁 Lootbox System",
            description="Open lootboxes to get random rewards!\n\n"
                       "**Possible Rewards:**\n"
                       "• Coins (100-1000)\n"
                       "• Random weapons and armor\n"
                       "• Super rare items (0.1% chance)\n\n"
                       "Buy lootboxes from the shop for 1000 coins!",
            color=COLORS['warning']
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(name='pvp', help='Challenge another player to PvP')
    async def pvp_command(self, ctx, member: discord.Member, arena: str = "Colosseum"):
        """Challenge another player to PvP."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        target_id = str(member.id)

        if user_id == target_id:
            await ctx.send("❌ You can't fight yourself!")
            return

        if arena not in PVP_ARENAS:
            await ctx.send(f"❌ Invalid arena! Choose from: {', '.join(PVP_ARENAS.keys())}")
            return

        if not ensure_user_exists(user_id) or not ensure_user_exists(target_id):
            await ctx.send("❌ Both players need to start their adventure first!")
            return

        challenger_data = get_user_rpg_data(user_id)
        target_data = get_user_rpg_data(target_id)

        if not challenger_data or not target_data:
            await ctx.send("❌ Could not retrieve player data.")
            return

        entry_fee = PVP_ARENAS[arena]["entry_fee"]

        if challenger_data.get('coins', 0) < entry_fee:
            await ctx.send(f"❌ You need {entry_fee} coins to enter {arena}!")
            return

        if target_data.get('coins', 0) < entry_fee:
            await ctx.send(f"❌ {member.mention} needs {entry_fee} coins to enter {arena}!")
            return

        view = PvPView(user_id, target_id, arena)
        embed = discord.Embed(
            title=f"⚔️ PvP Challenge - {arena}",
            description=f"{ctx.author.mention} challenges {member.mention} to battle!\n\n"
                       f"**Arena:** {arena}\n"
                       f"**Entry Fee:** {format_number(entry_fee)} coins\n"
                       f"**Winner Gets:** {format_number(entry_fee * PVP_ARENAS[arena]['winner_multiplier'])} coins",
            color=COLORS['warning']
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(name='trade', help='Trade items with another player')
    async def trade_command(self, ctx, member: discord.Member):
        """Start a trade with another player."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        target_id = str(member.id)

        if user_id == target_id:
            await ctx.send("❌ You can't trade with yourself!")
            return

        if not ensure_user_exists(user_id) or not ensure_user_exists(target_id):
            await ctx.send("❌ Both players need to start their adventure first!")
            return

        view = TradeView(user_id, target_id)
        embed = discord.Embed(
            title="🤝 Trade System",
            description=f"Trade between {ctx.author.mention} and {member.mention}\n\n"
                       f"**Instructions:**\n"
                       f"1. Add items and coins you want to trade\n"
                       f"2. Both players click Ready when satisfied\n"
                       f"3. Trade will be executed automatically\n\n"
                       f"**Current Trade:**\nEmpty",
            color=COLORS['primary']
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(name='rarity', help='Check item rarity information')
    async def rarity_command(self, ctx, *, item_name: str = None):
        """Check item rarity information."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        if not item_name:
            embed = discord.Embed(
                title="🌟 Rarity System",
                description="Items have different rarities that affect their power:",
                color=COLORS['primary']
            )

            rarity_info = ""
            for rarity, color in RARITY_COLORS.items():
                emoji = get_rarity_emoji(rarity)
                weight = RARITY_WEIGHTS.get(rarity, 0)
                rarity_info += f"{emoji} **{rarity.title()}** - {weight}% chance\n"

            embed.add_field(name="🎲 Rarity Levels", value=rarity_info, inline=False)
            embed.add_field(
                name="✨ Special Items",
                value="🔥 **World Ender** - Omnipotent weapon that can one-shot anything\n"
                     "💎 **Reality Stone** - Grants power to have any item (except World Ender)",
                inline=False
            )

            await ctx.send(embed=embed)
            return

        # Check specific item
        item_found = False
        item_data = None
        item_type = None

        if item_name in WEAPONS:
            item_data = WEAPONS[item_name]
            item_type = "weapon"
            item_found = True
        elif item_name in ARMOR:
            item_data = ARMOR[item_name]
            item_type = "armor"
            item_found = True
        elif item_name == "Reality Stone":
            item_data = OMNIPOTENT_ITEM["Reality Stone"]
            item_type = "accessory"
            item_found = True

        if not item_found:
            await ctx.send(f"❌ Item '{item_name}' not found!")
            return

        rarity = item_data["rarity"]
        emoji = get_rarity_emoji(rarity)
        color = RARITY_COLORS.get(rarity, COLORS['primary'])

        embed = discord.Embed(
            title=f"{emoji} {item_name}",
            description=f"**Type:** {item_type.title()}\n**Rarity:** {rarity.title()}",
            color=color
        )

        if item_type == "weapon":
            embed.add_field(name="⚔️ Attack", value=str(item_data["attack"]), inline=True)
        elif item_type == "armor":
            embed.add_field(name="🛡️ Defense", value=str(item_data["defense"]), inline=True)

        if item_data.get("special"):
            embed.add_field(name="✨ Special", value=item_data["special"], inline=True)

        await ctx.send(embed=embed)

    @commands.command(name='chrono_unlock', help='Check Chrono Weave class unlock progress')
    async def chrono_unlock_command(self, ctx):
        """Check progress towards unlocking Chrono Weave class."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        user_id = str(ctx.author.id)
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to start your adventure first!")
            return

        from utils.helpers import check_chrono_weave_unlock

        can_unlock, status_msg = check_chrono_weave_unlock(user_id)

        embed = discord.Embed(
            title="⏰ Chrono Weave Class Unlock",
            description="Master of time manipulation and temporal magic",
            color=COLORS['warning']
        )

        # Requirements
        embed.add_field(
            name="📋 Requirements",
            value="1. Defeat Time Rift Dragon while level ≤30\n"
                  "2. Complete 'Chrono Whispers' quest\n"
                  "3. Collect all 3 Ancient Relics",
            inline=False
        )

        # Status
        status_emoji = "✅" if can_unlock else "❌"
        embed.add_field(
            name=f"{status_emoji} Current Status",
            value=status_msg,
            inline=False
        )

        if can_unlock:
            embed.add_field(
                name="🎉 Ready to Unlock!",
                value="Use `$class chrono_weave` to unlock this hidden class!",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(RPGGamesCog(bot))