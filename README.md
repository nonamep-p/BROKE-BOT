
# 🧀 Plagg - AI Chatbot with RPG Features

**A Discord bot featuring advanced AI chat capabilities powered by Google Gemini, with bonus RPG game features.**

## 🤖 Main Feature: AI Chatbot

Plagg is primarily an **AI chatbot** with the personality of Plagg from Miraculous Ladybug - sarcastic, lazy, cheese-obsessed, but surprisingly wise and helpful. The bot uses Google Gemini AI for natural, context-aware conversations.

### AI Features:
- **Natural Conversations**: Just mention `@Plagg` or reply to his messages
- **Personality**: Sarcastic, lazy, cheese-obsessed character from Miraculous
- **Context Memory**: Remembers conversation history per user
- **Smart Responses**: Powered by Google Gemini 2.5 Flash
- **Channel Control**: Can be restricted to specific channels

## 🎮 Bonus Game Features

While AI chat is the main focus, Plagg also includes RPG gaming features:

### RPG System
- **Character Progression**: Level up, gain XP, improve stats
- **Adventures**: Explore different locations for rewards
- **Dungeons**: Multi-floor challenges with increasing difficulty
- **Battle System**: Fight monsters and other players
- **Equipment**: Weapons, armor, and items with rarity system
- **Inventory**: Manage your collected items

### Additional Features
- **Moderation Tools**: Kick, ban, mute, message management
- **Admin Controls**: Module configuration and server settings
- **Interactive UI**: Button and dropdown-based interfaces
- **Persistent Data**: All progress saved automatically

## 🚀 Quick Start

1. **Invite the bot** to your Discord server
2. **Start chatting**: Mention `@Plagg` to begin conversations
3. **Try RPG features**: Use `$start` to begin your adventure
4. **Get help**: Use `$help` for all available commands

### Essential Commands
- `@Plagg` or reply to Plagg - **Start AI conversation**
- `$help` - Interactive help menu
- `$start` - Begin RPG adventure
- `$profile` - View your character
- `$chat <message>` - Direct AI chat command

## 🛠️ Setup & Hosting

### Prerequisites
- Python 3.11+
- Discord Bot Token
- Google Gemini API Key

### Environment Variables
```
DISCORD_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
```

### Installation
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables
4. Run: `python main.py`

### Deployment on Replit
This bot is designed to run on Replit with:
- Built-in database for persistent storage
- Web server keep-alive system
- Automatic dependency management

## 📋 Features Overview

### Core Modules
- **AI Chatbot** (`cogs/ai_chatbot.py`) - Main feature
- **RPG Games** (`cogs/rpg_games.py`) - Adventure and battle system
- **Moderation** (`cogs/moderation.py`) - Server management
- **Admin** (`cogs/admin.py`) - Bot configuration
- **Help** (`cogs/help.py`) - Interactive help system

### Technical Features
- **Modular Architecture**: Easy to extend with new features
- **Database Integration**: Persistent user data and configurations
- **Error Handling**: Comprehensive error management and logging
- **Permission System**: Role-based access control
- **Interactive UI**: Discord buttons and dropdowns
- **API Integration**: Google Gemini for AI responses

## 🎯 Commands Reference

### AI Chat Commands
- `@Plagg <message>` - Chat with AI (mention)
- `$chat <message>` - Direct chat command
- `$clear_chat` - Clear your conversation history
- `$ai_status` - Check AI system status

### RPG Commands
- `$start` - Begin your RPG adventure
- `$profile` - View character profile
- `$adventure [location]` - Go on adventures
- `$dungeon [name]` - Explore dungeons
- `$battle [target]` - Battle monsters/players
- `$inventory` - Check your items
- `$equip <item>` - Equip weapons/armor

### Admin Commands
- `$config` - Server configuration
- `$stats` - Bot statistics
- `$reload <cog>` - Reload bot modules

## 🔧 Configuration

Administrators can configure:
- **Module toggles**: Enable/disable features per server
- **AI channels**: Restrict AI chat to specific channels
- **Moderation settings**: Auto-moderation and logging
- **Permission levels**: Role-based access control

## 📊 Database Structure

The bot uses Replit's built-in database for:
- User profiles and progress
- Server configurations
- RPG data (stats, inventories)
- Conversation histories
- Global statistics

## 🐛 Error Handling & Logging

- Comprehensive error catching and logging
- Graceful failure recovery
- User-friendly error messages
- Performance monitoring
- Debug information for troubleshooting

## 📈 Performance & Scalability

- **Memory Management**: Automatic cleanup of old data
- **Rate Limiting**: Discord API compliance
- **Caching**: Efficient data access patterns
- **Modular Loading**: Load only needed features
- **Database Optimization**: Efficient queries and indexing

## 🤝 Contributing

This bot was created by **NoNameP_P**. If you'd like to contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is open source. Please provide credit to **NoNameP_P** when using or modifying this code.

## 📞 Support

- **Creator**: NoNameP_P
- **Main Feature**: AI Chatbot with Plagg's personality
- **Bonus Features**: RPG systems
- **Platform**: Optimized for Replit hosting

## 🏷️ Bot Description for Discord Developer Portal

```
🧀 Plagg - AI Chatbot with RPG Features

Meet Plagg, your AI companion with the personality of the famous Kwami of Destruction! 

🤖 MAIN FEATURE - AI CHAT:
• Advanced conversations powered by Google Gemini
• Plagg's sarcastic, cheese-obsessed personality
• Context-aware responses with memory
• Just mention @Plagg to start chatting!

🎮 BONUS GAME FEATURES:
• Complete RPG system with adventures & dungeons
• Battle system and character progression
• Interactive UI with buttons and menus

🚀 QUICK START:
• Mention @Plagg for AI conversations
• Use $help for interactive command menu
• Use $start to begin RPG adventure

Created by NoNameP_P | Optimized for all server sizes
Main focus: AI Chatbot | Bonus: RPG features
```

---

**Created by NoNameP_P** - A Discord AI chatbot with RPG features, designed for natural conversations and entertainment.
