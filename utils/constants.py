"""
Enhanced Constants for the Epic RPG Bot with Plagg theme
"""
from typing import Dict, Any, List

# RPG System Constants
RPG_CONSTANTS = {
    # Cooldowns (in seconds)
    'work_cooldown': 3600,      # 1 hour
    'daily_cooldown': 86400,    # 24 hours
    'adventure_cooldown': 1800,  # 30 minutes
    'battle_cooldown': 300,     # 5 minutes
    'dungeon_cooldown': 7200,   # 2 hours
    'craft_cooldown': 600,      # 10 minutes
    'gather_cooldown': 900,     # 15 minutes
    'trade_cooldown': 1800,     # 30 minutes
    'quest_cooldown': 3600,     # 1 hour

    # Costs
    'heal_cost': 50,            # Cost to heal
    'revive_cost': 100,         # Cost to revive
    'guild_creation_cost': 5000, # Cost to create guild
    'profession_unlock_cost': 1000, # Cost to unlock profession

    # Level system
    'base_xp': 100,             # XP needed for level 2
    'xp_multiplier': 1.5,       # XP multiplier per level
    'max_level': 100,           # Maximum player level
    'prestige_level': 50,       # Level required for prestige

    # Battle system
    'critical_chance': 0.1,     # 10% critical hit chance
    'critical_multiplier': 2.0,  # 2x damage on critical
    'max_party_size': 4,        # Maximum party members

    # Luck system
    'luck_decay': 0.95,         # Luck decay per day
    'max_luck': 1000,           # Maximum luck points

    # Economy
    'max_inventory_size': 50,   # Maximum inventory slots
    'auction_tax': 0.05,        # 5% auction house tax
    'trade_fee': 100,           # Cost to initiate trade
}

# Player Classes with Plagg theme
PLAYER_CLASSES = {
    'warrior': {
        'name': 'Cheese Guardian',
        'description': 'Protects the sacred cheese with sword and shield',
        'base_stats': {'hp': 120, 'attack': 15, 'defense': 12, 'mana': 50},
        'skills': {
            'cheese_slam': {'damage': 25, 'mana_cost': 15, 'cooldown': 300},
            'camembert_shield': {'defense_boost': 10, 'mana_cost': 20, 'cooldown': 600},
            'gouda_rage': {'attack_boost': 15, 'mana_cost': 25, 'cooldown': 900}
        }
    },
    'mage': {
        'name': 'Kwami Sorcerer',
        'description': 'Harnesses the power of the Miraculous',
        'base_stats': {'hp': 80, 'attack': 20, 'defense': 5, 'mana': 100},
        'skills': {
            'miraculous_blast': {'damage': 35, 'mana_cost': 25, 'cooldown': 300},
            'plagg_protection': {'shield': 30, 'mana_cost': 30, 'cooldown': 600},
            'cataclysm': {'damage': 50, 'mana_cost': 50, 'cooldown': 1200}
        }
    },
    'rogue': {
        'name': 'Shadow Cat',
        'description': 'Strikes from the shadows like a feline predator',
        'base_stats': {'hp': 90, 'attack': 18, 'defense': 8, 'mana': 70},
        'skills': {
            'stealth_strike': {'damage': 30, 'mana_cost': 20, 'cooldown': 300},
            'cat_reflexes': {'dodge_chance': 0.3, 'mana_cost': 15, 'cooldown': 450},
            'shadow_clone': {'extra_attack': True, 'mana_cost': 35, 'cooldown': 900}
        }
    },
    'archer': {
        'name': 'Cheese Hunter',
        'description': 'Masters ranged combat with cheese-tipped arrows',
        'base_stats': {'hp': 95, 'attack': 17, 'defense': 7, 'mana': 60},
        'skills': {
            'cheese_arrow': {'damage': 28, 'mana_cost': 18, 'cooldown': 300},
            'multi_shot': {'hits': 3, 'mana_cost': 30, 'cooldown': 600},
            'piercing_shot': {'armor_ignore': True, 'mana_cost': 25, 'cooldown': 450}
        }
    },
    'healer': {
        'name': 'Tikki Disciple',
        'description': 'Channels creation energy to heal and support',
        'base_stats': {'hp': 85, 'attack': 12, 'defense': 10, 'mana': 120},
        'skills': {
            'healing_light': {'heal': 40, 'mana_cost': 25, 'cooldown': 300},
            'blessing': {'stat_boost': 10, 'mana_cost': 30, 'cooldown': 600},
            'resurrection': {'revive': True, 'mana_cost': 80, 'cooldown': 1800}
        }
    },
    'chrono_weave': {
        'name': 'Chrono Weave',
        'description': 'Master of time manipulation and temporal magic',
        'base_stats': {'hp': 100, 'attack': 25, 'defense': 15, 'mana': 150},
        'skills': {
            'time_reversal': {'revert_turns': 5, 'mana_cost': 80, 'cooldown': 259200},
            'temporal_surge': {'crit_boost': 20, 'xp_boost': 10, 'mana_cost': 40, 'cooldown': 900},
            'chrono_immunity': {'debuff_resist': 100, 'mana_cost': 60, 'cooldown': 1200}
        },
        'unlock_conditions': {
            'time_rift_dragon_defeat': {'level_cap': 30, 'boss_level': 80},
            'chrono_whispers_quest': {'event_required': 'time_rift'},
            'ancient_relics': ['relic_of_past', 'relic_of_future', 'relic_of_present']
        },
        'hidden': True
    }
}

# Professions System
PROFESSIONS = {
    'blacksmith': {
        'name': 'Miraculous Forger',
        'description': 'Crafts weapons and armor infused with kwami power',
        'max_level': 50,
        'recipes': ['iron_sword', 'steel_armor', 'miraculous_blade'],
        'gathering_spots': ['forge', 'mining_cave', 'scrapyard']
    },
    'alchemist': {
        'name': 'Potion Master',
        'description': 'Brews magical potions and elixirs',
        'max_level': 50,
        'recipes': ['health_potion', 'mana_elixir', 'cheese_brew'],
        'gathering_spots': ['herb_garden', 'crystal_cave', 'ancient_lab']
    },
    'enchanter': {
        'name': 'Kwami Enchanter',
        'description': 'Imbues items with magical properties',
        'max_level': 50,
        'recipes': ['fire_enchant', 'luck_charm', 'plagg_blessing'],
        'gathering_spots': ['magic_circle', 'kwami_shrine', 'moonstone_altar']
    }
}

# Crafting Recipes
CRAFTING_RECIPES = {
    'cheese_sword': {
        'profession': 'blacksmith',
        'level_required': 5,
        'materials': {'iron_ore': 3, 'aged_cheese': 2, 'kwami_essence': 1},
        'result': {'name': 'Cheese Sword', 'type': 'weapon', 'attack': 25, 'special': 'cheese_power'},
        'success_rate': 0.8
    },
    'camembert_armor': {
        'profession': 'blacksmith',
        'level_required': 10,
        'materials': {'steel_ingot': 5, 'camembert_wheel': 3, 'plagg_whisker': 1},
        'result': {'name': 'Camembert Armor', 'type': 'armor', 'defense': 30, 'special': 'cheese_resistance'},
        'success_rate': 0.7
    },
    'kwami_potion': {
        'profession': 'alchemist',
        'level_required': 8,
        'materials': {'crystal_water': 2, 'moonflower': 3, 'kwami_tear': 1},
        'result': {'name': 'Kwami Potion', 'type': 'consumable', 'heal': 100, 'special': 'mana_restore'},
        'success_rate': 0.75
    }
}

# Gathering Materials
GATHERING_MATERIALS = {
    'iron_ore': {'locations': ['mining_cave', 'mountain_pass'], 'rarity': 'common', 'base_chance': 0.6},
    'aged_cheese': {'locations': ['cheese_cellar', 'plagg_shrine'], 'rarity': 'uncommon', 'base_chance': 0.3},
    'kwami_essence': {'locations': ['kwami_shrine', 'miraculous_garden'], 'rarity': 'rare', 'base_chance': 0.1},
    'moonflower': {'locations': ['enchanted_forest', 'moonstone_altar'], 'rarity': 'uncommon', 'base_chance': 0.4},
    'plagg_whisker': {'locations': ['plagg_shrine'], 'rarity': 'legendary', 'base_chance': 0.05}
}

# Factions
FACTIONS = {
    'miraculous_order': {
        'name': 'Order of the Miraculous',
        'description': 'Protectors of the Miraculous and defenders of Paris',
        'alignment': 'good',
        'perks': ['healing_boost', 'teamwork_bonus', 'protection_aura'],
        'enemies': ['butterfly_syndicate']
    },
    'butterfly_syndicate': {
        'name': 'Butterfly Syndicate',
        'description': 'Those who seek power through dark miraculous',
        'alignment': 'evil',
        'perks': ['damage_boost', 'fear_aura', 'corruption_resistance'],
        'enemies': ['miraculous_order']
    },
    'cheese_guild': {
        'name': 'Ancient Cheese Guild',
        'description': 'Devoted followers of Plagg and cheese worship',
        'alignment': 'neutral',
        'perks': ['luck_boost', 'cheese_affinity', 'plagg_blessing'],
        'enemies': []
    }
}

# Quest Types
QUEST_TYPES = {
    'kill': {
        'name': 'Elimination',
        'description': 'Defeat specific monsters',
        'rewards': {'xp': (100, 300), 'coins': (200, 500), 'items': ['weapon', 'armor']}
    },
    'collection': {
        'name': 'Gathering',
        'description': 'Collect specific materials',
        'rewards': {'xp': (50, 150), 'coins': (100, 300), 'items': ['material', 'tool']}
    },
    'exploration': {
        'name': 'Discovery',
        'description': 'Explore new locations',
        'rewards': {'xp': (150, 400), 'coins': (300, 700), 'items': ['map', 'compass']}
    },
    'delivery': {
        'name': 'Courier',
        'description': 'Transport items between NPCs',
        'rewards': {'xp': (75, 200), 'coins': (150, 400), 'items': ['consumable']}
    },
    'story': {
        'name': 'Epic Tale',
        'description': 'Multi-part story quests with choices',
        'rewards': {'xp': (500, 1000), 'coins': (1000, 2500), 'items': ['legendary', 'unique']}
    }
}

# World Events
WORLD_EVENTS = {
    'cheese_storm': {
        'name': 'The Great Cheese Storm',
        'description': 'Plagg has gone wild! Cheese rains from the sky!',
        'duration': 3600,  # 1 hour
        'effects': {'loot_multiplier': 2.0, 'cheese_drop_chance': 0.8},
        'rewards': {'cheese_crown': 1, 'golden_camembert': 5}
    },
    'kwami_invasion': {
        'name': 'Rogue Kwami Invasion',
        'description': 'Wild kwamis have appeared across all locations!',
        'duration': 7200,  # 2 hours
        'effects': {'rare_encounter_chance': 0.5, 'xp_multiplier': 1.5},
        'rewards': {'kwami_fragment': 10, 'miraculous_shard': 3}
    },
    'camembert_colossus': {
        'name': 'Rise of the Camembert Colossus',
        'description': 'A giant cheese monster threatens all! Form parties to defeat it!',
        'duration': 10800,  # 3 hours
        'effects': {'global_boss': True, 'min_players': 10},
        'rewards': {'legendary_cheese_armor': 1, 'colossus_medal': 1}
    }
}

# PvP Arenas with Cheese Theme
PVP_ARENAS = {
    'cheese_pit': {
        'name': 'The Cheese Pit',
        'description': 'Battle in a pit filled with molten cheese',
        'entry_fee': 100,
        'winner_multiplier': 1.8,
        'special_effects': ['cheese_slick', 'heat_damage']
    },
    'miraculous_arena': {
        'name': 'Miraculous Colosseum',
        'description': 'The grand arena where heroes prove their worth',
        'entry_fee': 500,
        'winner_multiplier': 2.5,
        'special_effects': ['power_boost', 'audience_buff']
    },
    'kwami_realm': {
        'name': 'Kwami Dimension',
        'description': 'Fight in the ethereal realm of the kwamis',
        'entry_fee': 1000,
        'winner_multiplier': 3.0,
        'special_effects': ['gravity_shift', 'magic_amplification']
    }
}

# Legacy System
LEGACY_MODIFIERS = {
    'blessed_by_cheese': {
        'name': 'Blessed by Cheese',
        'description': 'Plagg smiles upon you',
        'effects': {'xp_bonus': 0.1, 'luck_bonus': 50},
        'rarity': 'rare'
    },
    'descendant_of_heroes': {
        'name': 'Descendant of Heroes',
        'description': 'Hero blood flows through your veins',
        'effects': {'stat_bonus': 5, 'skill_cooldown_reduction': 0.1},
        'rarity': 'epic'
    },
    'kwami_chosen': {
        'name': 'Chosen by Kwami',
        'description': 'A kwami has chosen you as their champion',
        'effects': {'mana_bonus': 50, 'special_abilities': True},
        'rarity': 'legendary'
    }
}

# Achievements
ACHIEVEMENTS = {
    'cheese_lover': {
        'name': 'Cheese Connoisseur',
        'description': 'Consume 100 cheese items',
        'requirement': {'cheese_consumed': 100},
        'rewards': {'title': 'Cheese Master', 'luck_points': 100}
    },
    'dragon_slayer': {
        'name': 'Dragon Slayer',
        'description': 'Defeat 10 Dragon Lords',
        'requirement': {'dragons_defeated': 10},
        'rewards': {'title': 'Dragon Bane', 'legendary_weapon': 1}
    },
    'kwami_friend': {
        'name': 'Friend of Kwamis',
        'description': 'Complete 50 kwami-related quests',
        'requirement': {'kwami_quests': 50},
        'rewards': {'title': 'Kwami Whisperer', 'kwami_companion': 1}
    }
}

# Weapon Unlock Conditions
WEAPON_UNLOCK_CONDITIONS = {
    "The Last Echo": {
        "requirements": [
            {"type": "boss_defeat", "boss": "paradox_realm_boss", "min_level": 100},
            {"type": "health_condition", "max_hp_percent": 25},
            {"type": "restriction", "no_buffs": True, "no_potions": True, "no_healing": True},
            {"type": "quest", "quest_name": "final_trial"}
        ],
        "description": "Defeat the Paradox Realm Boss without buffs, potions, or healing while under 25% HP",
        "unlock_message": "The echoes of eternity resonate within you... The Last Echo has chosen its wielder!"
    },
    "The Paradox Core": {
        "requirements": [
            {"type": "dungeon_clear", "dungeon": "paradox_chamber", "floors": 10},
            {"type": "item_required", "item": "paradox_key"},
            {"type": "battle_condition", "no_status_effects": True}
        ],
        "description": "Complete the 10-floor Paradox Chamber and use in battle with no status effects",
        "unlock_message": "Reality bends to your will... The Paradox Core materializes before you!"
    },
    "Timekeeper's Edge": {
        "requirements": [
            {"type": "class_unlock", "class": "chrono_weave"},
            {"type": "boss_defeat", "boss": "time_rift_dragon", "player_level_max": 30, "boss_level_min": 80}
        ],
        "description": "Unlock Chrono Weave class and defeat Time Rift Dragon at level 30 or lower",
        "unlock_message": "Time itself acknowledges your mastery... The Timekeeper's Edge appears!"
    },
    "Chrono Tap": {
        "requirements": [
            {"type": "class_unlock", "class": "chrono_weave"},
            {"type": "temporal_achievement", "achievement": "master_of_time"}
        ],
        "description": "Master temporal magic as Chrono Weave class",
        "unlock_message": "Your mastery of time resonates... The Chrono Tap manifests!"
    },
    "Echo of Eternity": {
        "requirements": [
            {"type": "class_unlock", "class": "chrono_weave"},
            {"type": "special_condition", "condition": "survive_paradox_storm"}
        ],
        "description": "Survive the Paradox Storm event as Chrono Weave",
        "unlock_message": "Eternal echoes shield your soul... The Echo of Eternity forms!"
    }
}

# Special Bosses and Events
SPECIAL_BOSSES = {
    "time_rift_dragon": {
        "name": "Time Rift Dragon",
        "level": 80,
        "hp": 5000,
        "attack": 100,
        "defense": 50,
        "special_abilities": ["temporal_breath", "time_freeze", "chronos_roar"],
        "drops": ["chrono_fragment", "dragon_scale", "time_essence"],
        "location": "temporal_rift"
    },
    "paradox_realm_boss": {
        "name": "Void Sovereign",
        "level": 100,
        "hp": 10000,
        "attack": 150,
        "defense": 75,
        "special_abilities": ["reality_tear", "void_pulse", "paradox_storm"],
        "drops": ["The Last Echo", "void_crystal", "sovereign_crown"],
        "location": "paradox_realm"
    },
    "camembert_colossus": {
        "name": "Camembert Colossus",
        "level": 75,
        "hp": 15000,
        "attack": 120,
        "defense": 100,
        "special_abilities": ["cheese_avalanche", "dairy_rage", "calcium_shield"],
        "drops": ["legendary_cheese_armor", "colossus_medal", "ancient_camembert"],
        "location": "cheese_dimension",
        "event_boss": True,
        "min_players": 10
    }
}

# Interactive Dungeon System with Scenarios
INTERACTIVE_DUNGEONS = {
    "cheese_labyrinth": {
        "name": "🧀 Plagg's Cheese Labyrinth",
        "description": "Navigate through a maze of aged cheese and dairy dangers",
        "difficulty": "easy",
        "min_level": 1,
        "max_level": 10,
        "floors": 3,
        "scenarios": [
            {
                "type": "choice",
                "title": "The Moldy Passage",
                "description": "You encounter a passage blocked by moldy cheese. What do you do?",
                "choices": [
                    {"text": "🗡️ Cut through with your weapon", "result": "combat", "enemy": "mold_spores"},
                    {"text": "🧀 Eat the moldy cheese", "result": "poison", "damage": 20, "reward": "cheese_immunity"},
                    {"text": "🚪 Look for another path", "result": "secret", "reward": "hidden_treasure"}
                ]
            },
            {
                "type": "puzzle",
                "title": "The Camembert Riddle",
                "description": "A wise cheese spirit asks: 'What gets stronger the longer it ages?'",
                "answer": "cheese",
                "success_reward": {"coins": 200, "xp": 50},
                "failure_penalty": {"hp": 10}
            },
            {
                "type": "boss",
                "title": "Cheese Golem Guardian",
                "description": "A massive golem made of hardened cheese blocks your path!",
                "boss": {
                    "name": "Ancient Cheese Golem",
                    "hp": 150,
                    "attack": 15,
                    "defense": 20,
                    "special": "cheese_heal"
                }
            }
        ],
        "rewards": {"coins": (100, 300), "xp": (50, 150), "items": ["cheese_sword", "aged_cheddar"]},
        "boss": "Cheese Golem King"
    },
    "kwami_sanctuary": {
        "name": "✨ Hidden Kwami Sanctuary",
        "description": "Discover the secret refuge where kwamis gather",
        "difficulty": "medium",
        "min_level": 5,
        "max_level": 15,
        "floors": 5,
        "scenarios": [
            {
                "type": "choice",
                "title": "The Kwami Test",
                "description": "Three kwamis test your worthiness. Which trial do you choose?",
                "choices": [
                    {"text": "🔥 Plagg's Destruction Trial", "result": "combat", "enemy": "shadow_clone"},
                    {"text": "❤️ Tikki's Creation Trial", "result": "healing", "reward": "full_heal"},
                    {"text": "🐢 Wayzz's Protection Trial", "result": "defense", "reward": "shield_boost"}
                ]
            },
            {
                "type": "mystery",
                "title": "The Vanishing Kwami",
                "description": "A kwami has gone missing! Follow the clues to find them.",
                "clues": ["tiny_footprints", "magical_residue", "cheese_crumbs"],
                "solution": "plagg_hiding_spot",
                "reward": {"kwami_blessing": True, "luck_points": 100}
            },
            {
                "type": "boss",
                "title": "Corrupted Guardian",
                "description": "Face a kwami guardian consumed by dark energy!",
                "boss": {
                    "name": "Void Kwami",
                    "hp": 300,
                    "attack": 25,
                    "defense": 15,
                    "special": "void_drain"
                }
            }
        ],
        "rewards": {"coins": (300, 600), "xp": (150, 300), "items": ["kwami_charm", "miraculous_shard"]},
        "boss": "Ancient Kwami Elder"
    },
    "akuma_factory": {
        "name": "🦋 Hawkmoth's Akuma Factory",
        "description": "Infiltrate the dark facility where akumas are created",
        "difficulty": "hard",
        "min_level": 10,
        "max_level": 25,
        "floors": 7,
        "scenarios": [
            {
                "type": "stealth",
                "title": "Security Bypass",
                "description": "Sneak past the akuma sentries or fight your way through?",
                "choices": [
                    {"text": "🥷 Sneak past quietly", "result": "stealth_success", "bonus": "surprise_attack"},
                    {"text": "⚔️ Fight through", "result": "combat", "enemy": "akuma_patrol"},
                    {"text": "🎭 Disguise yourself", "result": "disguise", "reward": "insider_info"}
                ]
            },
            {
                "type": "sabotage",
                "title": "Disable the Machinery",
                "description": "You find the akuma creation machine. How do you disable it?",
                "actions": ["cut_power", "overload_system", "virus_upload"],
                "success_reward": {"coins": 500, "xp": 200, "achievement": "saboteur"},
                "failure_consequence": {"reinforcements": True}
            },
            {
                "type": "boss",
                "title": "Mayura's Champion",
                "description": "Face off against Mayura's most powerful sentimonster!",
                "boss": {
                    "name": "Sentibug Supreme",
                    "hp": 500,
                    "attack": 35,
                    "defense": 25,
                    "special": "multiply"
                }
            }
        ],
        "rewards": {"coins": (500, 1000), "xp": (300, 600), "items": ["akuma_purifier", "butterfly_fragment"]},
        "boss": "Shadow Moth"
    },
    "temporal_nexus": {
        "name": "⏰ Temporal Nexus",
        "description": "Navigate through time itself in this reality-bending dungeon",
        "difficulty": "legendary",
        "min_level": 20,
        "max_level": 50,
        "floors": 10,
        "scenarios": [
            {
                "type": "time_puzzle",
                "title": "Paradox Gate",
                "description": "Solve the temporal equation to unlock the next area",
                "puzzle": "time_calculation",
                "success_reward": {"time_shard": 1, "xp": 300},
                "failure_penalty": {"time_loop": True}
            },
            {
                "type": "time_choice",
                "title": "Past or Future?",
                "description": "You can travel to the past or future. Choose wisely!",
                "choices": [
                    {"text": "⏪ Travel to the past", "result": "past_encounter", "enemy": "ancient_guardian"},
                    {"text": "⏩ Travel to the future", "result": "future_encounter", "enemy": "cyber_kwami"},
                    {"text": "⏸️ Stay in the present", "result": "present_stability", "reward": "temporal_anchor"}
                ]
            },
            {
                "type": "boss",
                "title": "Time Rift Dragon",
                "description": "The guardian of time itself challenges you!",
                "boss": {
                    "name": "Chronos Dragon",
                    "hp": 1000,
                    "attack": 50,
                    "defense": 35,
                    "special": "time_stop"
                }
            }
        ],
        "rewards": {"coins": (1000, 2000), "xp": (500, 1000), "items": ["timekeeper_edge", "chrono_crystal"]},
        "boss": "Master of Time"
    }
}

# Special Dungeons
SPECIAL_DUNGEONS = {
    "paradox_chamber": {
        "name": "Paradox Chamber",
        "floors": 10,
        "difficulty": "mythic",
        "mechanics": ["time_puzzles", "reality_shifts", "temporal_traps"],
        "rewards": ["The Paradox Core", "paradox_fragments", "time_crystals"],
        "unlock_requirement": "paradox_key"
    },
    "temporal_rift": {
        "name": "Temporal Rift",
        "floors": 5,
        "difficulty": "legendary",
        "mechanics": ["time_dilation", "past_echoes", "future_visions"],
        "rewards": ["chrono_fragments", "time_essence", "temporal_gear"],
        "event_dungeon": True
    }
}

# Ancient Relics for Chrono Weave Unlock
ANCIENT_RELICS = {
    "relic_of_past": {
        "name": "Relic of the Past",
        "description": "Echoes with memories of what was",
        "location": "ancient_ruins",
        "drop_chance": 0.05,
        "requirement": "archaeology_quest"
    },
    "relic_of_future": {
        "name": "Relic of the Future",
        "description": "Pulses with energy of what will be",
        "location": "crystal_caverns",
        "drop_chance": 0.05,
        "requirement": "prophecy_quest"
    },
    "relic_of_present": {
        "name": "Relic of the Present",
        "description": "Hums with the power of now",
        "location": "temporal_nexus",
        "drop_chance": 0.05,
        "requirement": "meditation_quest"
    }
}

# Seasonal Changes
SEASONS = {
    'spring': {
        'name': 'Season of Growth',
        'effects': {'gathering_bonus': 1.2, 'new_monsters': ['flower_sprite', 'garden_golem']},
        'special_events': ['bloom_festival']
    },
    'summer': {
        'name': 'Season of Power',
        'effects': {'xp_bonus': 1.15, 'combat_intensity': 1.1},
        'special_events': ['solar_eclipse', 'cheese_melting']
    },
    'autumn': {
        'name': 'Season of Harvest',
        'effects': {'crafting_bonus': 1.3, 'rare_material_chance': 1.2},
        'special_events': ['harvest_moon', 'cheese_aging']
    },
    'winter': {
        'name': 'Season of Trials',
        'effects': {'boss_strength': 1.2, 'legendary_drop_chance': 1.5},
        'special_events': ['frost_invasion', 'frozen_cheese']
    }
}

# Mini-Games
MINI_GAMES = {
    'cheese_fishing': {
        'name': 'Cheese Pond Fishing',
        'description': 'Fish in magical cheese ponds for rare aquatic pets',
        'cost': 50,
        'rewards': ['cheese_fish', 'aquatic_pet', 'fishing_rod']
    },
    'plagg_trivia': {
        'name': "Plagg's Cheese Trivia",
        'description': 'Test your knowledge of cheese and kwamis',
        'cost': 25,
        'rewards': ['trivia_trophy', 'wisdom_boost', 'cheese_knowledge']
    },
    'miraculous_roulette': {
        'name': 'Miraculous Roulette',
        'description': 'Spin the wheel of fortune for miraculous prizes',
        'cost': 100,
        'rewards': ['coins', 'items', 'miraculous_fragments']
    }
}

# Item Rarity System
RARITY_COLORS = {
    "common": 0x9E9E9E,      # Gray
    "uncommon": 0x4CAF50,    # Green
    "rare": 0x2196F3,        # Blue
    "epic": 0x9C27B0,        # Purple
    "legendary": 0xFF9800,   # Orange
    "mythic": 0xF44336,      # Red
    "divine": 0xFFD700,      # Gold
    "omnipotent": 0xFF1493   # Deep Pink
}

RARITY_WEIGHTS = {
    "common": 0.50,      # 50%
    "uncommon": 0.25,    # 25%
    "rare": 0.15,        # 15%
    "epic": 0.07,        # 7%
    "legendary": 0.025,  # 2.5%
    "mythic": 0.004,     # 0.4%
    "divine": 0.001,     # 0.1%
    "omnipotent": 0.0001 # 0.01%
}

# Luck Levels
LUCK_LEVELS = {
    'cursed': {'min': -1000, 'max': -100, 'emoji': '💀', 'bonus_percent': -25},
    'unlucky': {'min': -99, 'max': -1, 'emoji': '😰', 'bonus_percent': -10},
    'normal': {'min': 0, 'max': 99, 'emoji': '😐', 'bonus_percent': 0},
    'lucky': {'min': 100, 'max': 499, 'emoji': '😊', 'bonus_percent': 15},
    'blessed': {'min': 500, 'max': 999, 'emoji': '✨', 'bonus_percent': 30},
    'divine': {'min': 1000, 'max': 9999, 'emoji': '🌟', 'bonus_percent': 50}
}

# Weapons System
WEAPONS = {
    # Warrior Class Weapons
    "Iron Petal": {
        "attack": 10,
        "defense": 2,
        "rarity": "common",
        "class_req": "warrior",
        "special": "boss_damage",
        "boss_damage": 5
    },
    "Stump Cleave": {
        "attack": 15,
        "defense": 5,
        "rarity": "common",
        "class_req": "warrior",
        "special": "crit_chance",
        "crit_chance": 3
    },
    "Wooden Round": {
        "attack": 2,
        "defense": 15,
        "rarity": "common",
        "class_req": "warrior",
        "special": "block_chance",
        "block_chance": 10
    },

    # Mage Class Weapons
    "Sprintling": {
        "attack": 10,
        "defense": 1,
        "rarity": "uncommon",
        "class_req": "mage",
        "special": "mana_regen",
        "mana_regen": 5
    },
    "Ashen Quill": {
        "attack": 12,
        "defense": 3,
        "rarity": "uncommon",
        "class_req": "mage",
        "special": "spell_power",
        "spell_power": 10
    },
    "The Tome of Flare": {
        "attack": 8,
        "defense": 2,
        "rarity": "uncommon",
        "class_req": "mage",
        "special": "fireball_chance",
        "fireball_chance": 3
    },

    # Rogue Class Weapons
    "Shiny Slicer": {
        "attack": 18,
        "defense": 3,
        "rarity": "rare",
        "class_req": "rogue",
        "special": "crit_chance",
        "crit_chance": 10
    },
    "Whispering Curve": {
        "attack": 20,
        "defense": 2,
        "rarity": "rare",
        "class_req": "rogue",
        "special": "ranged_damage",
        "ranged_damage": 7
    },
    "Stinger Vial": {
        "attack": 5,
        "defense": 0,
        "rarity": "rare",
        "class_req": "rogue",
        "special": "stun_chance",
        "stun_chance": 10
    },

    # Archer Class Weapons
    "Sylvan Edge": {
        "attack": 25,
        "defense": 4,
        "rarity": "epic",
        "class_req": "archer",
        "special": "airborne_damage",
        "airborne_damage": 15
    },
    "Thunderpop": {
        "attack": 30,
        "defense": 3,
        "rarity": "epic",
        "class_req": "archer",
        "special": "crit_chance",
        "crit_chance": 20
    },
    "Ethereal Tip": {
        "attack": 5,
        "defense": 0,
        "rarity": "epic",
        "class_req": "archer",
        "special": "speed_reduction",
        "speed_reduction": 5
    },

    # Healer Class Weapons
    "Elder's Pulse": {
        "attack": 15,
        "defense": 7,
        "rarity": "legendary",
        "class_req": "healer",
        "special": "healing_power",
        "healing_power": 20
    },
    "Nectar of Lifespan": {
        "attack": 0,
        "defense": 0,
        "rarity": "legendary",
        "class_req": "healer",
        "special": "instant_heal",
        "instant_heal": 200,
        "uses": 1
    },
    "Eternal Glow": {
        "attack": 10,
        "defense": 5,
        "rarity": "legendary",
        "class_req": "healer",
        "special": "multi_bonus",
        "mana_regen": 10,
        "crit_heal": 5
    },

    # Chrono Weave (Hidden Class) Weapons
    "Timekeeper's Edge": {
        "attack": 35,
        "defense": 5,
        "rarity": "legendary",
        "class_req": "chrono_weave",
        "special": "time_reversal",
        "time_reversal_charges": 1,
        "cooldown": 259200  # 3 days in seconds
    },
    "Chrono Tap": {
        "attack": 25,
        "defense": 3,
        "rarity": "legendary",
        "class_req": "chrono_weave",
        "special": "temporal_surge",
        "crit_chance": 20,
        "xp_gain": 10
    },
    "Echo of Eternity": {
        "attack": 8,
        "defense": 25,
        "rarity": "legendary",
        "class_req": "chrono_weave",
        "special": "chrono_immunity",
        "debuff_resist": 100
    },

    # Mythic Weapons
    "The Last Echo": {
        "attack": 50,
        "defense": 10,
        "rarity": "mythic",
        "class_req": "any",
        "special": "legendary_bonus",
        "xp_gain": 25,
        "boss_damage": 30,
        "unlock_condition": "paradox_realm_boss"
    },
    "The Paradox Core": {
        "attack": 40,
        "defense": 8,
        "rarity": "mythic",
        "class_req": "any",
        "special": "randomized_boost",
        "random_stat_chance": 50,
        "random_stat_boost": 15,
        "unlock_condition": "paradox_chamber"
    },

    # Omnipotent Weapons (existing)
    "World Ender": {
        "attack": 999999,
        "defense": 0,
        "rarity": "omnipotent",
        "class_req": "any",
        "special": "one_shot_kill"
    }
}

# Armor System
ARMOR = {
    # Common Armor
    "Leather Vest": {
        "defense": 8,
        "rarity": "common",
        "class_req": "any"
    },
    "Iron Chestplate": {
        "defense": 15,
        "rarity": "uncommon",
        "class_req": "warrior"
    },
    "Mage Robes": {
        "defense": 5,
        "mana_boost": 20,
        "rarity": "uncommon",
        "class_req": "mage"
    },
    "Shadow Cloak": {
        "defense": 10,
        "stealth_bonus": 15,
        "rarity": "rare",
        "class_req": "rogue"
    },
    "Ranger's Coat": {
        "defense": 12,
        "range_bonus": 10,
        "rarity": "rare",
        "class_req": "archer"
    },
    "Holy Vestments": {
        "defense": 8,
        "healing_bonus": 25,
        "rarity": "epic",
        "class_req": "healer"
    },
    "Temporal Armor": {
        "defense": 20,
        "time_resistance": 50,
        "rarity": "legendary",
        "class_req": "chrono_weave"
    }
}

# Omnipotent Items
OMNIPOTENT_ITEM = {
    "Reality Stone": {
        "rarity": "omnipotent",
        "special": "wish_any_item",
        "description": "Can grant any item except World Ender"
    }
}

# Shop Items - Unique ID-based system to prevent duplication
SHOP_ITEMS = {
    "weapon_001": {
        "id": "weapon_001",
        "name": "Iron Sword",
        "attack": 5,
        "defense": 2,
        "price": 100,
        "rarity": "common",
        "category": "weapons",
        "description": "A basic iron sword for beginners"
    },
    "weapon_009": {
        "id": "weapon_009",
        "name": "Plagg's Cataclysm Blade",
        "attack": 40,
        "defense": 15,
        "price": 8000,
        "rarity": "legendary",
        "category": "weapons",
        "description": "⚡ A blade infused with destructive kwami energy",
        "effect": "cataclysm_strike",
        "special_ability": "30% chance to destroy enemy armor on hit"
    },
    "weapon_010": {
        "id": "weapon_010",
        "name": "Miraculous Dual Blades",
        "attack": 35,
        "defense": 10,
        "price": 6500,
        "rarity": "epic",
        "category": "weapons",
        "description": "🗡️ Twin blades that grow stronger together",
        "effect": "dual_strike",
        "special_ability": "Each hit increases next attack by 5% (max 50%)"
    },
    "weapon_011": {
        "id": "weapon_011",
        "name": "Cheese Slicer Supreme",
        "attack": 25,
        "defense": 5,
        "price": 3000,
        "rarity": "rare",
        "category": "weapons",
        "description": "🧀 Plagg's favorite weapon for cheese... and enemies",
        "effect": "cheese_power",
        "special_ability": "Heals 10 HP per enemy defeated"
    },
    "weapon_012": {
        "id": "weapon_012",
        "name": "Quantum Disruptor",
        "attack": 55,
        "defense": 20,
        "price": 18000,
        "rarity": "mythical",
        "category": "weapons",
        "description": "⚛️ A weapon that manipulates quantum fields",
        "effect": "quantum_chaos",
        "special_ability": "Ignores all enemy defenses and shields"
    },
    "weapon_013": {
        "id": "weapon_013",
        "name": "Akuma Purifier",
        "attack": 30,
        "defense": 12,
        "price": 4500,
        "rarity": "epic",
        "category": "weapons",
        "description": "🦋 A blade that purifies corrupted souls",
        "effect": "purification",
        "special_ability": "Deals 2x damage to corrupted enemies"
    },
    "armor_006": {
        "id": "armor_006",
        "name": "Kwami Guardian Armor",
        "defense": 30,
        "price": 5000,
        "rarity": "legendary",
        "category": "armor",
        "description": "🛡️ Blessed armor protected by kwami magic",
        "effect": "kwami_protection",
        "special_ability": "Blocks 25% of magical damage"
    },
    "armor_007": {
        "id": "armor_007",
        "name": "Camembert Plate Mail",
        "defense": 35,
        "price": 7000,
        "rarity": "legendary",
        "category": "armor",
        "description": "🧀 Armor forged from the finest aged camembert",
        "effect": "cheese_resistance",
        "special_ability": "Immune to poison and curse effects"
    },
    "armor_008": {
        "id": "armor_008",
        "name": "Miraculous Suit",
        "defense": 40,
        "price": 10000,
        "rarity": "mythical",
        "category": "armor",
        "description": "✨ The ultimate protection for miraculous holders",
        "effect": "miraculous_power",
        "special_ability": "Regenerates 5 HP per turn in combat"
    },
    "item_008": {
        "id": "item_008",
        "name": "Tikki's Cookie",
        "effect": "tikki_blessing",
        "price": 500,
        "rarity": "rare",
        "category": "consumables",
        "description": "🍪 A magical cookie that grants Tikki's blessing",
        "special_ability": "Grants lucky streak for 1 hour (+50% rare drops)"
    },
    "item_009": {
        "id": "item_009",
        "name": "Plagg's Camembert Wheel",
        "effect": "plagg_power",
        "price": 800,
        "rarity": "epic",
        "category": "consumables",
        "description": "🧀 Plagg's favorite snack with destructive power",
        "special_ability": "Next attack ignores all defenses"
    },
    "item_010": {
        "id": "item_010",
        "name": "Kwami Energy Crystal",
        "effect": "kwami_energy",
        "price": 1200,
        "rarity": "legendary",
        "category": "consumables",
        "description": "💎 Pure kwami energy in crystallized form",
        "special_ability": "Restores full HP and MP, grants temporary invincibility"
    },
    "item_011": {
        "id": "item_011",
        "name": "Miraculous Compass",
        "effect": "navigation_boost",
        "price": 2000,
        "rarity": "epic",
        "category": "accessories",
        "description": "🧭 Always points toward your greatest adventure",
        "special_ability": "Reveals hidden dungeon rooms and secret passages"
    },
    "item_012": {
        "id": "item_012",
        "name": "Butterfly Miraculous Fragment",
        "effect": "emotion_control",
        "price": 3500,
        "rarity": "legendary",
        "category": "accessories",
        "description": "🦋 A fragment of the butterfly miraculous",
        "special_ability": "Can pacify hostile enemies or enrage allies"
    },
    "item_013": {
        "id": "item_013",
        "name": "Guardian's Grimoire",
        "effect": "knowledge_boost",
        "price": 5000,
        "rarity": "mythical",
        "category": "accessories",
        "description": "📚 Ancient tome containing miraculous secrets",
        "special_ability": "Reveals weaknesses of all enemies and boss patterns"
    },
    "item_014": {
        "id": "item_014",
        "name": "Temporal Anchor",
        "effect": "time_stability",
        "price": 10000,
        "rarity": "mythical",
        "category": "accessories",
        "description": "⏰ Anchors you to the current timeline",
        "special_ability": "Prevents time-based attacks and allows time travel"
    },
    "item_015": {
        "id": "item_015",
        "name": "Cheese Golem Heart",
        "effect": "summon_golem",
        "price": 4000,
        "rarity": "epic",
        "category": "consumables",
        "description": "🧀 The heart of an ancient cheese golem",
        "special_ability": "Summons a cheese golem ally for 5 turns"
    },
    "weapon_002": {
        "id": "weapon_002",
        "name": "Steel Sword",
        "attack": 8,
        "defense": 3,
        "price": 200,
        "rarity": "uncommon",
        "category": "weapons",
        "description": "A sturdy steel blade"
    },
    "weapon_003": {
        "id": "weapon_003",
        "name": "Mystic Blade",
        "attack": 12,
        "defense": 5,
        "price": 500,
        "rarity": "rare",
        "category": "weapons",
        "description": "A blade infused with magical energy"
    },
    "weapon_004": {
        "id": "weapon_004",
        "name": "Dragon Slayer",
        "attack": 20,
        "defense": 8,
        "price": 1500,
        "rarity": "epic",
        "category": "weapons",
        "description": "Forged to slay the mightiest dragons"
    },
    "weapon_005": {
        "id": "weapon_005",
        "name": "Timekeeper's Edge",
        "attack": 35,
        "defense": 15,
        "price": 5000,
        "rarity": "legendary",
        "category": "weapons",
        "description": "Twin-blade sword with time manipulation powers",
        "effect": "Time Reversal (1 charge/3 days, reverses 5 turns)"
    },
    "weapon_006": {
        "id": "weapon_006",
        "name": "The Last Echo",
        "attack": 50,
        "defense": 25,
        "price": 15000,
        "rarity": "mythical",
        "category": "weapons",
        "description": "Great Axe that echoes with the power of fallen heroes",
        "effect": "+25% XP gain, +30% boss damage"
    },
    "weapon_007": {
        "id": "weapon_007",
        "name": "Chrono Weave",
        "attack": 45,
        "defense": 20,
        "price": 12000,
        "rarity": "mythical",
        "category": "weapons",
        "description": "A weapon that weaves through time itself",
        "effect": "Time manipulation abilities"
    },
    "weapon_008": {
        "id": "weapon_008",
        "name": "The Paradox Core",
        "attack": 60,
        "defense": 30,
        "price": 25000,
        "rarity": "mythical",
        "category": "weapons",
        "description": "Crystal Staff containing the essence of paradox",
        "effect": "Reality manipulation powers"
    },
    "armor_001": {
        "id": "armor_001",
        "name": "Leather Armor",
        "defense": 3,
        "price": 80,
        "rarity": "common",
        "category": "armor",
        "description": "Basic leather protection"
    },
    "armor_002": {
        "id": "armor_002",
        "name": "Chain Mail",
        "defense": 6,
        "price": 180,
        "rarity": "uncommon",
        "category": "armor",
        "description": "Interlocked metal rings for protection"
    },
    "armor_003": {
        "id": "armor_003",
        "name": "Plate Armor",
        "defense": 10,
        "price": 400,
        "rarity": "rare",
        "category": "armor",
        "description": "Heavy metal plates for maximum protection"
    },
    "armor_004": {
        "id": "armor_004",
        "name": "Dragon Scale Armor",
        "defense": 18,
        "price": 1200,
        "rarity": "epic",
        "category": "armor",
        "description": "Armor crafted from ancient dragon scales"
    },
    "armor_005": {
        "id": "armor_005",
        "name": "Celestial Robes",
        "defense": 25,
        "price": 4000,
        "rarity": "legendary",
        "category": "armor",
        "description": "Robes blessed by celestial beings"
    },
    "item_001": {
        "id": "item_001",
        "name": "Health Potion",
        "effect": "heal_50",
        "price": 25,
        "rarity": "common",
        "category": "consumables",
        "description": "Restores 50 HP"
    },
    "item_002": {
        "id": "item_002",
        "name": "Mana Potion",
        "effect": "mana_50",
        "price": 30,
        "rarity": "common",
        "category": "consumables",
        "description": "Restores 50 MP"
    },
    "item_003": {
        "id": "item_003",
        "name": "Lucky Charm",
        "effect": "luck_boost",
        "price": 150,
        "rarity": "uncommon",
        "category": "consumables",
        "description": "Increases luck for a short time"
    },
    "item_004": {
        "id": "item_004",
        "name": "XP Boost",
        "effect": "xp_double",
        "price": 200,
        "rarity": "rare",
        "category": "consumables",
        "description": "Doubles XP gain for next battle"
    },
    "item_005": {
        "id": "item_005",
        "name": "Phoenix Feather",
        "effect": "revive",
        "price": 800,
        "rarity": "epic",
        "category": "consumables",
        "description": "Revives from death once"
    },
    "item_006": {
        "id": "item_006",
        "name": "Golden Elixir",
        "effect": "heal_500",
        "price": 1500,
        "rarity": "legendary",
        "category": "consumables",
        "description": "Restores 500 HP instantly"
    },
    "item_007": {
        "id": "item_007",
        "name": "Lootbox",
        "effect": "random_reward",
        "price": 1000,
        "rarity": "rare",
        "category": "consumables",
        "description": "Contains random rewards including rare items"
    }
}

# Rarity display configuration
RARITY_DISPLAY = {
    "common": {"emoji": "⚪", "color": 0x95A5A6},
    "uncommon": {"emoji": "🟢", "color": 0x2ECC71},
    "rare": {"emoji": "🔵", "color": 0x3498DB},
    "epic": {"emoji": "🟣", "color": 0x9B59B6},
    "legendary": {"emoji": "🟠", "color": 0xF39C12},
    "mythical": {"emoji": "🔴", "color": 0xE74C3C}
}

def get_all_shop_items():
    """Get all shop items with deduplication by ID"""
    all_items = {}

    for item_id, item_data in SHOP_ITEMS.items():
        if item_id and item_data not in all_items:
            all_items[item_id] = {
                **item_data,
            }

    return all_items

def get_items_by_rarity(rarity_filter=None):
    """Get items filtered by rarity with no duplicates"""
    all_items = get_all_shop_items()

    if not rarity_filter:
        return all_items

    if isinstance(rarity_filter, str):
        rarity_filter = [rarity_filter]

    return {
        item_id: item_data
        for item_id, item_data in all_items.items()
        if item_data.get("rarity") in rarity_filter
    }

def get_dynamic_weapons():
    """Get dynamically created weapons from database."""
    from replit import db
    return db.get("dynamic_weapons", {})

def get_dynamic_armor():
    """Get dynamically created armor from database."""
    from replit import db
    return db.get("dynamic_armor", {})

def get_dynamic_bosses():
    """Get dynamically created bosses from database."""
    from replit import db
    return db.get("dynamic_bosses", {})

def get_dynamic_classes():
    """Get dynamically created classes from database."""
    from replit import db
    return db.get("dynamic_classes", {})

def get_all_weapons():
    """Get all weapons including dynamic ones."""
    all_weapons = WEAPONS.copy()
    dynamic_weapons = get_dynamic_weapons()
    all_weapons.update(dynamic_weapons)
    return all_weapons

def get_all_armor():
    """Get all armor including dynamic ones."""
    all_armor = ARMOR.copy()
    dynamic_armor = get_dynamic_armor()
    all_armor.update(dynamic_armor)
    return all_armor

def get_all_bosses():
    """Get all bosses including dynamic ones."""
    all_bosses = SPECIAL_BOSSES.copy()
    dynamic_bosses = get_dynamic_bosses()
    all_bosses.update(dynamic_bosses)
    return all_bosses

def get_all_classes():
    """Get all classes including dynamic ones."""
    all_classes = PLAYER_CLASSES.copy()
    dynamic_classes = get_dynamic_classes()
    all_classes.update(dynamic_classes)
    return all_classes

def get_game_difficulty():
    """Get current game difficulty setting."""
    from replit import db
    settings = db.get("game_settings", {})
    return settings.get("difficulty", 5)

def get_xp_multiplier():
    """Get current XP multiplier setting."""
    from replit import db
    settings = db.get("game_settings", {})
    return settings.get("xp_multiplier", 1.0)

# Daily Rewards
DAILY_REWARDS = {
    'base': 100,
    'level_multiplier': 10,
    'streak_bonus': 25,
    'max_streak': 7
}

# Status Effects
STATUS_EFFECTS = {
    'blessed': {'duration': 1800, 'effects': {'luck_bonus': 100, 'xp_bonus': 1.2}},
    'cursed': {'duration': 1800, 'effects': {'luck_penalty': -50, 'damage_penalty': 0.8}},
    'cheese_power': {'duration': 600, 'effects': {'attack_bonus': 1.3, 'cheese_immunity': True}},
    'kwami_protection': {'duration': 900, 'effects': {'defense_bonus': 1.5, 'magic_resistance': 0.5}}
}

# World Locations with cheese theme
WORLD_LOCATIONS = {
    'paris_streets': {
        'name': 'Streets of Paris',
        'description': 'The familiar streets where miraculous holders patrol',
        'level_range': (1, 10),
        'monsters': ['akuma_victim', 'sentimonster'],
        'resources': ['city_materials', 'tourist_coins']
    },
    'cheese_dimension': {
        'name': 'Plagg\'s Cheese Dimension',
        'description': 'A realm made entirely of different cheeses',
        'level_range': (15, 30),
        'monsters': ['cheese_golem', 'cheddar_spirit'],
        'resources': ['aged_cheese', 'mystical_dairy']
    },
    'kwami_realm': {
        'name': 'The Kwami Realm',
        'description': 'The mystical home dimension of all kwamis',
        'level_range': (25, 50),
        'monsters': ['rogue_kwami', 'guardian_spirit'],
        'resources': ['kwami_essence', 'miraculous_energy']
    }
}