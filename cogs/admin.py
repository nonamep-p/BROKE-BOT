
import discord
from discord.ext import commands
from discord import app_commands
import psutil
import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import traceback
import json

from config import COLORS, EMOJIS, get_server_config, update_server_config, user_has_permission, is_module_enabled
from utils.helpers import create_embed, format_duration, format_number
from utils.database import get_user_rpg_data, update_user_rpg_data, get_guild_data, update_guild_data, get_user_data, update_user_data
from utils.constants import WEAPONS, ARMOR, SHOP_ITEMS, PLAYER_CLASSES, SPECIAL_BOSSES

logger = logging.getLogger(__name__)

# Bot Owner ID
BOT_OWNER_ID = 1297013439125917766

class OwnerControlPanel(discord.ui.View):
    """Master control panel for bot owner."""
    
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="👑 Player Management", style=discord.ButtonStyle.primary, custom_id="owner_player_mgmt")
    async def player_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != BOT_OWNER_ID:
            await interaction.response.send_message("❌ Owner only!", ephemeral=True)
            return
            
        view = PlayerManagementView()
        embed = create_embed(
            "👑 Player Management Panel",
            "Manage any player's stats, inventory, and progression:",
            COLORS['warning']
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
    @discord.ui.button(label="🎮 Game Content", style=discord.ButtonStyle.success, custom_id="owner_content_mgmt")
    async def content_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != BOT_OWNER_ID:
            await interaction.response.send_message("❌ Owner only!", ephemeral=True)
            return
            
        view = ContentManagementView()
        embed = create_embed(
            "🎮 Game Content Management",
            "Create and manage weapons, items, bosses, and classes:",
            COLORS['success']
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
    @discord.ui.button(label="📢 Announcements", style=discord.ButtonStyle.secondary, custom_id="owner_announcements")
    async def announcements(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != BOT_OWNER_ID:
            await interaction.response.send_message("❌ Owner only!", ephemeral=True)
            return
            
        view = AnnouncementView()
        embed = create_embed(
            "📢 Announcement System",
            "Send announcements and manage automated messages:",
            COLORS['info']
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
    @discord.ui.button(label="⚙️ System Settings", style=discord.ButtonStyle.danger, custom_id="owner_system")
    async def system_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != BOT_OWNER_ID:
            await interaction.response.send_message("❌ Owner only!", ephemeral=True)
            return
            
        view = SystemSettingsView()
        embed = create_embed(
            "⚙️ System Settings",
            "Configure global settings, difficulty, and bot behavior:",
            COLORS['error']
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class PlayerManagementView(discord.ui.View):
    """Player management interface for owner."""
    
    def __init__(self):
        super().__init__(timeout=300)
        
    @discord.ui.button(label="👤 Edit Player", style=discord.ButtonStyle.primary)
    async def edit_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = PlayerEditModal()
        await interaction.response.send_modal(modal)
        
    @discord.ui.button(label="💰 Give Coins", style=discord.ButtonStyle.success)
    async def give_coins(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = GiveCoinsModal()
        await interaction.response.send_modal(modal)
        
    @discord.ui.button(label="🎁 Give Items", style=discord.ButtonStyle.secondary)
    async def give_items(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = GiveItemsModal()
        await interaction.response.send_modal(modal)
        
    @discord.ui.button(label="📊 View Stats", style=discord.ButtonStyle.primary)
    async def view_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ViewPlayerModal()
        await interaction.response.send_modal(modal)

class PlayerEditModal(discord.ui.Modal):
    """Modal for editing player stats."""
    
    def __init__(self):
        super().__init__(title="Edit Player Stats")
        
        self.user_input = discord.ui.TextInput(
            label="User ID or @mention",
            placeholder="Enter user ID or mention the user",
            required=True
        )
        self.add_item(self.user_input)
        
        self.stat_input = discord.ui.TextInput(
            label="Stat to Edit",
            placeholder="level, hp, attack, defense, coins, xp, etc.",
            required=True
        )
        self.add_item(self.stat_input)
        
        self.value_input = discord.ui.TextInput(
            label="New Value",
            placeholder="Enter the new value",
            required=True
        )
        self.add_item(self.value_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Extract user ID
            user_input = self.user_input.value.strip()
            if user_input.startswith('<@') and user_input.endswith('>'):
                user_id = user_input[2:-1]
                if user_id.startswith('!'):
                    user_id = user_id[1:]
            else:
                user_id = user_input
                
            # Get player data
            player_data = get_user_rpg_data(user_id)
            if not player_data:
                await interaction.response.send_message("❌ Player not found!", ephemeral=True)
                return
                
            stat = self.stat_input.value.lower()
            try:
                value = int(self.value_input.value)
            except ValueError:
                value = self.value_input.value
                
            # Update stat
            if stat in player_data:
                old_value = player_data[stat]
                player_data[stat] = value
                update_user_rpg_data(user_id, player_data)
                
                embed = create_embed(
                    "✅ Player Stats Updated",
                    f"**Player:** <@{user_id}>\n"
                    f"**Stat:** {stat}\n"
                    f"**Old Value:** {old_value}\n"
                    f"**New Value:** {value}",
                    COLORS['success']
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ Stat '{stat}' not found!", ephemeral=True)
                
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

class GiveCoinsModal(discord.ui.Modal):
    """Modal for giving coins to players."""
    
    def __init__(self):
        super().__init__(title="Give Coins to Player")
        
        self.user_input = discord.ui.TextInput(
            label="User ID or @mention",
            placeholder="Enter user ID or mention the user",
            required=True
        )
        self.add_item(self.user_input)
        
        self.amount_input = discord.ui.TextInput(
            label="Amount",
            placeholder="Enter amount of coins to give",
            required=True
        )
        self.add_item(self.amount_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Extract user ID
            user_input = self.user_input.value.strip()
            if user_input.startswith('<@') and user_input.endswith('>'):
                user_id = user_input[2:-1]
                if user_id.startswith('!'):
                    user_id = user_id[1:]
            else:
                user_id = user_input
                
            amount = int(self.amount_input.value)
            
            # Get player data
            player_data = get_user_rpg_data(user_id)
            if not player_data:
                await interaction.response.send_message("❌ Player not found!", ephemeral=True)
                return
                
            # Give coins
            old_coins = player_data.get('coins', 0)
            player_data['coins'] = old_coins + amount
            update_user_rpg_data(user_id, player_data)
            
            embed = create_embed(
                "💰 Coins Given Successfully",
                f"**Player:** <@{user_id}>\n"
                f"**Amount Given:** {format_number(amount)}\n"
                f"**Previous Balance:** {format_number(old_coins)}\n"
                f"**New Balance:** {format_number(player_data['coins'])}",
                COLORS['success']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Invalid amount!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

class GiveItemsModal(discord.ui.Modal):
    """Modal for giving items to players."""
    
    def __init__(self):
        super().__init__(title="Give Items to Player")
        
        self.user_input = discord.ui.TextInput(
            label="User ID or @mention",
            placeholder="Enter user ID or mention the user",
            required=True
        )
        self.add_item(self.user_input)
        
        self.item_input = discord.ui.TextInput(
            label="Item Name",
            placeholder="Enter the item name",
            required=True
        )
        self.add_item(self.item_input)
        
        self.quantity_input = discord.ui.TextInput(
            label="Quantity",
            placeholder="Enter quantity (default: 1)",
            required=False,
            default="1"
        )
        self.add_item(self.quantity_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Extract user ID
            user_input = self.user_input.value.strip()
            if user_input.startswith('<@') and user_input.endswith('>'):
                user_id = user_input[2:-1]
                if user_id.startswith('!'):
                    user_id = user_id[1:]
            else:
                user_id = user_input
                
            item_name = self.item_input.value
            quantity = int(self.quantity_input.value or "1")
            
            # Get player data
            player_data = get_user_rpg_data(user_id)
            if not player_data:
                await interaction.response.send_message("❌ Player not found!", ephemeral=True)
                return
                
            # Give items
            inventory = player_data.get('inventory', [])
            for _ in range(quantity):
                inventory.append(item_name)
            player_data['inventory'] = inventory
            update_user_rpg_data(user_id, player_data)
            
            embed = create_embed(
                "🎁 Items Given Successfully",
                f"**Player:** <@{user_id}>\n"
                f"**Item:** {item_name}\n"
                f"**Quantity:** {quantity}",
                COLORS['success']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Invalid quantity!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

class ViewPlayerModal(discord.ui.Modal):
    """Modal for viewing player stats."""
    
    def __init__(self):
        super().__init__(title="View Player Stats")
        
        self.user_input = discord.ui.TextInput(
            label="User ID or @mention",
            placeholder="Enter user ID or mention the user",
            required=True
        )
        self.add_item(self.user_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Extract user ID
            user_input = self.user_input.value.strip()
            if user_input.startswith('<@') and user_input.endswith('>'):
                user_id = user_input[2:-1]
                if user_id.startswith('!'):
                    user_id = user_id[1:]
            else:
                user_id = user_input
                
            # Get player data
            player_data = get_user_rpg_data(user_id)
            if not player_data:
                await interaction.response.send_message("❌ Player not found!", ephemeral=True)
                return
                
            embed = create_embed(
                f"👤 Player Stats: <@{user_id}>",
                "Complete player information:",
                COLORS['info']
            )
            
            embed.add_field(
                name="📊 Basic Stats",
                value=f"**Level:** {player_data.get('level', 1)}\n"
                      f"**XP:** {player_data.get('xp', 0)}/{player_data.get('max_xp', 100)}\n"
                      f"**HP:** {player_data.get('hp', 100)}/{player_data.get('max_hp', 100)}\n"
                      f"**Attack:** {player_data.get('attack', 10)}\n"
                      f"**Defense:** {player_data.get('defense', 5)}",
                inline=True
            )
            
            embed.add_field(
                name="💰 Economy",
                value=f"**Coins:** {format_number(player_data.get('coins', 0))}\n"
                      f"**Items:** {len(player_data.get('inventory', []))}\n"
                      f"**Class:** {player_data.get('player_class', 'None')}\n"
                      f"**Profession:** {player_data.get('profession', 'None')}",
                inline=True
            )
            
            stats = player_data.get('stats', {})
            embed.add_field(
                name="🏆 Achievements",
                value=f"**Battles Won:** {stats.get('battles_won', 0)}\n"
                      f"**Bosses Defeated:** {stats.get('bosses_defeated', 0)}\n"
                      f"**Adventures:** {player_data.get('adventure_count', 0)}\n"
                      f"**Work Count:** {player_data.get('work_count', 0)}",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

class ContentManagementView(discord.ui.View):
    """Content creation and management interface."""
    
    def __init__(self):
        super().__init__(timeout=300)
        
    @discord.ui.button(label="⚔️ Create Weapon", style=discord.ButtonStyle.primary)
    async def create_weapon(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CreateWeaponModal()
        await interaction.response.send_modal(modal)
        
    @discord.ui.button(label="🛡️ Create Armor", style=discord.ButtonStyle.secondary)
    async def create_armor(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CreateArmorModal()
        await interaction.response.send_modal(modal)
        
    @discord.ui.button(label="🐲 Create Boss", style=discord.ButtonStyle.danger)
    async def create_boss(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CreateBossModal()
        await interaction.response.send_modal(modal)
        
    @discord.ui.button(label="🎭 Create Class", style=discord.ButtonStyle.success)
    async def create_class(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CreateClassModal()
        await interaction.response.send_modal(modal)

class CreateWeaponModal(discord.ui.Modal):
    """Modal for creating new weapons."""
    
    def __init__(self):
        super().__init__(title="Create New Weapon")
        
        self.name_input = discord.ui.TextInput(
            label="Weapon Name",
            placeholder="Enter weapon name",
            required=True
        )
        self.add_item(self.name_input)
        
        self.attack_input = discord.ui.TextInput(
            label="Attack Power",
            placeholder="Enter attack value",
            required=True
        )
        self.add_item(self.attack_input)
        
        self.defense_input = discord.ui.TextInput(
            label="Defense (optional)",
            placeholder="Enter defense value",
            required=False
        )
        self.add_item(self.defense_input)
        
        self.rarity_input = discord.ui.TextInput(
            label="Rarity",
            placeholder="common, uncommon, rare, epic, legendary, mythic",
            required=True
        )
        self.add_item(self.rarity_input)
        
        self.special_input = discord.ui.TextInput(
            label="Special Ability (optional)",
            placeholder="Enter special ability description",
            required=False,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.special_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        try:
            weapon_name = self.name_input.value
            attack = int(self.attack_input.value)
            defense = int(self.defense_input.value) if self.defense_input.value else 0
            rarity = self.rarity_input.value.lower()
            special = self.special_input.value or None
            
            # Add to constants (this would be saved to database in production)
            weapon_data = {
                "attack": attack,
                "defense": defense,
                "rarity": rarity,
                "class_req": "any",
                "special": special
            }
            
            # Save to dynamic weapons storage
            from replit import db
            dynamic_weapons = db.get("dynamic_weapons", {})
            dynamic_weapons[weapon_name] = weapon_data
            db["dynamic_weapons"] = dynamic_weapons
            
            embed = create_embed(
                "⚔️ Weapon Created Successfully",
                f"**Name:** {weapon_name}\n"
                f"**Attack:** {attack}\n"
                f"**Defense:** {defense}\n"
                f"**Rarity:** {rarity}\n"
                f"**Special:** {special or 'None'}",
                COLORS['success']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Invalid numeric values!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

class CreateArmorModal(discord.ui.Modal):
    """Modal for creating new armor."""
    
    def __init__(self):
        super().__init__(title="Create New Armor")
        
        self.name_input = discord.ui.TextInput(
            label="Armor Name",
            placeholder="Enter armor name",
            required=True
        )
        self.add_item(self.name_input)
        
        self.defense_input = discord.ui.TextInput(
            label="Defense Power",
            placeholder="Enter defense value",
            required=True
        )
        self.add_item(self.defense_input)
        
        self.rarity_input = discord.ui.TextInput(
            label="Rarity",
            placeholder="common, uncommon, rare, epic, legendary, mythic",
            required=True
        )
        self.add_item(self.rarity_input)
        
        self.special_input = discord.ui.TextInput(
            label="Special Ability (optional)",
            placeholder="Enter special ability description",
            required=False,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.special_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        try:
            armor_name = self.name_input.value
            defense = int(self.defense_input.value)
            rarity = self.rarity_input.value.lower()
            special = self.special_input.value or None
            
            # Add to dynamic storage
            armor_data = {
                "defense": defense,
                "rarity": rarity,
                "class_req": "any",
                "special": special
            }
            
            from replit import db
            dynamic_armor = db.get("dynamic_armor", {})
            dynamic_armor[armor_name] = armor_data
            db["dynamic_armor"] = dynamic_armor
            
            embed = create_embed(
                "🛡️ Armor Created Successfully",
                f"**Name:** {armor_name}\n"
                f"**Defense:** {defense}\n"
                f"**Rarity:** {rarity}\n"
                f"**Special:** {special or 'None'}",
                COLORS['success']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Invalid numeric values!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

class CreateBossModal(discord.ui.Modal):
    """Modal for creating new bosses."""
    
    def __init__(self):
        super().__init__(title="Create New Boss")
        
        self.name_input = discord.ui.TextInput(
            label="Boss Name",
            placeholder="Enter boss name",
            required=True
        )
        self.add_item(self.name_input)
        
        self.level_input = discord.ui.TextInput(
            label="Boss Level",
            placeholder="Enter boss level",
            required=True
        )
        self.add_item(self.level_input)
        
        self.hp_input = discord.ui.TextInput(
            label="Boss HP",
            placeholder="Enter boss HP",
            required=True
        )
        self.add_item(self.hp_input)
        
        self.attack_input = discord.ui.TextInput(
            label="Boss Attack",
            placeholder="Enter boss attack power",
            required=True
        )
        self.add_item(self.attack_input)
        
        self.rewards_input = discord.ui.TextInput(
            label="Rewards (comma separated)",
            placeholder="Enter reward items",
            required=True,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.rewards_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        try:
            boss_name = self.name_input.value
            level = int(self.level_input.value)
            hp = int(self.hp_input.value)
            attack = int(self.attack_input.value)
            rewards = [r.strip() for r in self.rewards_input.value.split(",")]
            
            # Create boss data
            boss_data = {
                "name": boss_name,
                "level": level,
                "hp": hp,
                "attack": attack,
                "defense": max(10, attack // 4),
                "special_abilities": ["boss_rage", "heavy_strike"],
                "drops": rewards,
                "location": "custom_arena"
            }
            
            from replit import db
            dynamic_bosses = db.get("dynamic_bosses", {})
            dynamic_bosses[boss_name.lower().replace(" ", "_")] = boss_data
            db["dynamic_bosses"] = dynamic_bosses
            
            embed = create_embed(
                "🐲 Boss Created Successfully",
                f"**Name:** {boss_name}\n"
                f"**Level:** {level}\n"
                f"**HP:** {format_number(hp)}\n"
                f"**Attack:** {attack}\n"
                f"**Rewards:** {', '.join(rewards)}",
                COLORS['success']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Invalid numeric values!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

class CreateClassModal(discord.ui.Modal):
    """Modal for creating new player classes."""
    
    def __init__(self):
        super().__init__(title="Create New Player Class")
        
        self.name_input = discord.ui.TextInput(
            label="Class Name",
            placeholder="Enter class name",
            required=True
        )
        self.add_item(self.name_input)
        
        self.description_input = discord.ui.TextInput(
            label="Description",
            placeholder="Enter class description",
            required=True,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.description_input)
        
        self.stats_input = discord.ui.TextInput(
            label="Base Stats (hp,attack,defense,mana)",
            placeholder="100,15,10,50",
            required=True
        )
        self.add_item(self.stats_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        try:
            class_name = self.name_input.value
            description = self.description_input.value
            stats = [int(s.strip()) for s in self.stats_input.value.split(",")]
            
            if len(stats) != 4:
                await interaction.response.send_message("❌ Please provide exactly 4 stats: hp,attack,defense,mana", ephemeral=True)
                return
                
            class_data = {
                "name": class_name,
                "description": description,
                "base_stats": {
                    "hp": stats[0],
                    "attack": stats[1], 
                    "defense": stats[2],
                    "mana": stats[3]
                },
                "skills": {
                    "basic_attack": {"damage": stats[1], "mana_cost": 10, "cooldown": 300},
                    "power_strike": {"damage": stats[1] * 2, "mana_cost": 25, "cooldown": 600}
                }
            }
            
            from replit import db
            dynamic_classes = db.get("dynamic_classes", {})
            dynamic_classes[class_name.lower().replace(" ", "_")] = class_data
            db["dynamic_classes"] = dynamic_classes
            
            embed = create_embed(
                "🎭 Class Created Successfully",
                f"**Name:** {class_name}\n"
                f"**Description:** {description}\n"
                f"**HP:** {stats[0]} | **ATK:** {stats[1]} | **DEF:** {stats[2]} | **MP:** {stats[3]}",
                COLORS['success']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Invalid stats format!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

class AnnouncementView(discord.ui.View):
    """Announcement management interface."""
    
    def __init__(self):
        super().__init__(timeout=300)
        
    @discord.ui.button(label="📢 Send Announcement", style=discord.ButtonStyle.primary)
    async def send_announcement(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AnnouncementModal()
        await interaction.response.send_modal(modal)
        
    @discord.ui.button(label="⏰ Schedule Reminder", style=discord.ButtonStyle.secondary)
    async def schedule_reminder(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ReminderModal()
        await interaction.response.send_modal(modal)

class AnnouncementModal(discord.ui.Modal):
    """Modal for sending announcements."""
    
    def __init__(self):
        super().__init__(title="Send Global Announcement")
        
        self.title_input = discord.ui.TextInput(
            label="Announcement Title",
            placeholder="Enter announcement title",
            required=True
        )
        self.add_item(self.title_input)
        
        self.message_input = discord.ui.TextInput(
            label="Announcement Message",
            placeholder="Enter announcement content",
            required=True,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.message_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        try:
            title = self.title_input.value
            message = self.message_input.value
            
            embed = create_embed(
                f"📢 {title}",
                message,
                COLORS['warning']
            )
            embed.set_footer(text="Official Plagg Bot Announcement")
            
            # Send to all guilds
            sent_count = 0
            for guild in interaction.client.guilds:
                try:
                    # Find a suitable channel
                    channel = guild.system_channel or guild.text_channels[0] if guild.text_channels else None
                    if channel:
                        await channel.send(embed=embed)
                        sent_count += 1
                except:
                    continue
                    
            await interaction.response.send_message(f"✅ Announcement sent to {sent_count} servers!", ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

class ReminderModal(discord.ui.Modal):
    """Modal for scheduling reminders."""
    
    def __init__(self):
        super().__init__(title="Schedule Reminder")
        
        self.message_input = discord.ui.TextInput(
            label="Reminder Message",
            placeholder="Enter reminder content",
            required=True,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.message_input)
        
        self.time_input = discord.ui.TextInput(
            label="Time (minutes from now)",
            placeholder="Enter minutes",
            required=True
        )
        self.add_item(self.time_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        try:
            message = self.message_input.value
            minutes = int(self.time_input.value)
            
            # Store reminder in database
            from replit import db
            reminders = db.get("scheduled_reminders", [])
            reminder_time = datetime.now() + timedelta(minutes=minutes)
            
            reminders.append({
                "message": message,
                "time": reminder_time.isoformat(),
                "created_by": interaction.user.id
            })
            db["scheduled_reminders"] = reminders
            
            await interaction.response.send_message(f"✅ Reminder scheduled for {minutes} minutes from now!", ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Invalid time format!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

class SystemSettingsView(discord.ui.View):
    """System settings management interface."""
    
    def __init__(self):
        super().__init__(timeout=300)
        
    @discord.ui.button(label="⚙️ Game Settings", style=discord.ButtonStyle.primary)
    async def game_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = GameSettingsModal()
        await interaction.response.send_modal(modal)
        
    @discord.ui.button(label="💬 Welcome Message", style=discord.ButtonStyle.secondary)
    async def welcome_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = WelcomeMessageModal()
        await interaction.response.send_modal(modal)

class GameSettingsModal(discord.ui.Modal):
    """Modal for game settings."""
    
    def __init__(self):
        super().__init__(title="Game Settings")
        
        self.difficulty_input = discord.ui.TextInput(
            label="Game Difficulty (1-10)",
            placeholder="Enter difficulty level",
            required=True
        )
        self.add_item(self.difficulty_input)
        
        self.xp_multiplier_input = discord.ui.TextInput(
            label="XP Multiplier",
            placeholder="Enter XP multiplier (e.g., 1.5)",
            required=True
        )
        self.add_item(self.xp_multiplier_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        try:
            difficulty = int(self.difficulty_input.value)
            xp_multiplier = float(self.xp_multiplier_input.value)
            
            from replit import db
            game_settings = db.get("game_settings", {})
            game_settings.update({
                "difficulty": difficulty,
                "xp_multiplier": xp_multiplier,
                "updated_by": interaction.user.id,
                "updated_at": datetime.now().isoformat()
            })
            db["game_settings"] = game_settings
            
            embed = create_embed(
                "⚙️ Game Settings Updated",
                f"**Difficulty:** {difficulty}/10\n"
                f"**XP Multiplier:** {xp_multiplier}x",
                COLORS['success']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Invalid values!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

class WelcomeMessageModal(discord.ui.Modal):
    """Modal for setting welcome message."""
    
    def __init__(self):
        super().__init__(title="Set Welcome Message")
        
        self.message_input = discord.ui.TextInput(
            label="Welcome Message",
            placeholder="Enter the welcome message for new players",
            required=True,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.message_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        try:
            message = self.message_input.value
            
            from replit import db
            db["welcome_message"] = message
            
            await interaction.response.send_message("✅ Welcome message updated!", ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

class ConfigView(discord.ui.View):
    """Interactive configuration view for server settings."""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.config = get_server_config(guild_id)
        
    @discord.ui.button(label="📝 Change Prefix", style=discord.ButtonStyle.primary)
    async def change_prefix(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Change server prefix."""
        if not user_has_permission(interaction.user, 'admin'):
            await interaction.response.send_message("❌ You need admin permissions!", ephemeral=True)
            return
            
        modal = PrefixModal(self.guild_id, self.config)
        await interaction.response.send_modal(modal)
        
    @discord.ui.button(label="🔧 Module Settings", style=discord.ButtonStyle.secondary)
    async def module_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configure modules."""
        if not user_has_permission(interaction.user, 'admin'):
            await interaction.response.send_message("❌ You need admin permissions!", ephemeral=True)
            return
            
        view = ModuleConfigView(self.guild_id)
        embed = create_embed(
            "🔧 Module Configuration",
            "Select which modules to enable or disable:",
            COLORS['info']
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class PrefixModal(discord.ui.Modal):
    """Modal for changing server prefix."""
    
    def __init__(self, guild_id: int, config: Dict[str, Any]):
        super().__init__(title="Change Server Prefix")
        self.guild_id = guild_id
        self.config = config
        
        self.prefix_input = discord.ui.TextInput(
            label="New Prefix",
            placeholder="Enter new prefix (e.g., !, ?, $)",
            max_length=5,
            default=config.get('prefix', '$')
        )
        self.add_item(self.prefix_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        """Handle prefix change."""
        new_prefix = self.prefix_input.value.strip()
        
        if not new_prefix:
            await interaction.response.send_message("❌ Prefix cannot be empty!", ephemeral=True)
            return
            
        self.config['prefix'] = new_prefix
        update_server_config(self.guild_id, self.config)
        
        embed = create_embed(
            "✅ Prefix Changed",
            f"Server prefix changed to: `{new_prefix}`",
            COLORS['success']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ModuleConfigView(discord.ui.View):
    """View for configuring modules."""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.config = get_server_config(guild_id)
        
    @discord.ui.button(label="🎮 RPG Games", style=discord.ButtonStyle.primary)
    async def toggle_rpg(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle RPG module."""
        self.config['enabled_modules']['rpg'] = not self.config['enabled_modules']['rpg']
        update_server_config(self.guild_id, self.config)
        
        status = "enabled" if self.config['enabled_modules']['rpg'] else "disabled"
        await interaction.response.send_message(f"✅ RPG module {status}!", ephemeral=True)

class AdminCog(commands.Cog):
    """Admin commands and server management."""
    
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(OwnerControlPanel())  # Add persistent view
        
    @commands.command(name='owner', help='Owner control panel')
    async def owner_panel(self, ctx):
        """Open the owner control panel."""
        if ctx.author.id != BOT_OWNER_ID:
            await ctx.send("❌ This command is restricted to the bot owner!")
            return
            
        view = OwnerControlPanel()
        embed = create_embed(
            "👑 Owner Control Panel",
            "Welcome to the master control panel. You have full control over the game:",
            COLORS['warning']
        )
        embed.add_field(
            name="🎮 Available Controls",
            value="• **Player Management** - Edit any player's stats, give items/coins\n"
                  "• **Game Content** - Create weapons, armor, bosses, classes\n"
                  "• **Announcements** - Send global messages and reminders\n"
                  "• **System Settings** - Configure game difficulty and settings",
            inline=False
        )
        await ctx.send(embed=embed, view=view)
        
    @commands.command(name='reminder_check', help='Check scheduled reminders (Owner only)')
    async def check_reminders(self, ctx):
        """Check and send scheduled reminders."""
        if ctx.author.id != BOT_OWNER_ID:
            return
            
        from replit import db
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
                for guild in self.bot.guilds:
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
        db["scheduled_reminders"] = remaining_reminders
        
        if sent_reminders:
            await ctx.send(f"✅ Sent {len(sent_reminders)} scheduled reminders!")
        
    @commands.command(name='config', help='Interactive server configuration')
    @commands.has_permissions(administrator=True)
    async def config_command(self, ctx):
        """Interactive server configuration."""
        if not is_module_enabled("admin", ctx.guild.id):
            return
            
        view = ConfigView(ctx.guild.id)
        config = get_server_config(ctx.guild.id)
        
        embed = create_embed(
            f"{EMOJIS['admin']} Server Configuration",
            f"**Current Settings:**\n"
            f"• Prefix: `{config.get('prefix', '$')}`\n"
            f"• Currency: {config.get('currency_name', 'coins')}\n"
            f"• AI Channels: {len(config.get('ai_channels', []))} configured\n"
            f"• Auto-Moderation: {'✅' if config.get('auto_moderation', {}).get('enabled', True) else '❌'}\n\n"
            f"Use the buttons below to configure your server:",
            COLORS['info']
        )
        
        await ctx.send(embed=embed, view=view)
        
    @commands.command(name='stats', help='View bot statistics')
    async def stats_command(self, ctx):
        """View bot statistics."""
        if not is_module_enabled("admin", ctx.guild.id):
            return
            
        embed = await self.create_stats_embed()
        await ctx.send(embed=embed)
        
    async def create_stats_embed(self) -> discord.Embed:
        """Create bot statistics embed."""
        try:
            # Get system stats
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Calculate uptime
            uptime = datetime.now() - self.bot.start_time
            uptime_str = format_duration(uptime.total_seconds())
            
            embed = discord.Embed(
                title=f"{EMOJIS['admin']} Bot Statistics",
                color=COLORS['info']
            )
            
            # Bot Stats
            embed.add_field(
                name="🤖 Bot Info",
                value=f"**Servers:** {len(self.bot.guilds)}\n"
                      f"**Users:** {len(self.bot.users)}\n"
                      f"**Uptime:** {uptime_str}\n"
                      f"**Commands:** {len(self.bot.commands)}",
                inline=True
            )
            
            # System Stats
            embed.add_field(
                name="🖥️ System Info",
                value=f"**CPU:** {cpu_percent}%\n"
                      f"**Memory:** {memory.percent}%\n"
                      f"**Disk:** {disk.percent}%",
                inline=True
            )
            
            # Discord Stats
            embed.add_field(
                name="📊 Discord Stats",
                value=f"**Latency:** {round(self.bot.latency * 1000)}ms\n"
                      f"**Shards:** {self.bot.shard_count or 1}\n"
                      f"**Cached Messages:** {len(self.bot.cached_messages)}",
                inline=True
            )
            
            embed.set_footer(text=f"Bot ID: {self.bot.user.id}")
            embed.timestamp = datetime.now()
            
            return embed
        except Exception as e:
            logger.error(f"Error creating stats embed: {e}")
            return create_embed("❌ Error", "Failed to generate statistics.", COLORS['error'])

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(AdminCog(bot))
