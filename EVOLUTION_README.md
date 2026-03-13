# 🧬 Self-Evolving AI Chatbot

This chatbot has the ability to **modify and evolve its own behavior** without affecting core functionality.

## Architecture

### Core Files
- **chatbot_advanced.py** - Main immutable bot logic (never self-modifies)
- **chatbot_memory.json** - Stores learned conversations
- **chatbot_config.json** - Stores custom patterns and evolution data (**Evolves automatically**)

## Self-Evolution Features

### 1. **User Teaching**
Teach the bot custom patterns that it will remember:

```
You: teach me: pizza | I love pizza!
Bot: I learned! When you say 'pizza', I'll remember this response.
```

### 2. **Automatic Learning**
The bot learns from every conversation and stores patterns in `chatbot_config.json`:
- Successful response patterns
- User-taught patterns
- Evolution statistics

### 3. **Self-Modification**
The bot can modify its own behavior by:
- Adding new custom patterns
- Adjusting response strategies
- Tracking evolution metrics

### 4. **Evolution Statistics**
Check how the bot is evolving:

```
You: show stats
Bot: Evolution Statistics:
- Total Conversations: 42
- Successful Responses: 38
- User-Taught Patterns: 5
- Self-Modified: 2
- Custom Patterns Learned: 5
```

### 5. **Show Learned Patterns**
See what the bot has learned:

```
You: show config
Bot: I've learned these custom patterns: 'pizza', 'programming', 'music'
```

## How Self-Evolution Works

### File Separation Strategy

```
┌─────────────────────────────────┐
│   chatbot_advanced.py           │
│   (Core Logic - Immutable)      │
│   - Pattern matching            │
│   - Response generation         │
│   - Basic conversations         │
└──────────────┬──────────────────┘
               │ reads/writes
               ↓
┌──────────────────────────────────┐
│   chatbot_config.json            │
│   (Evolution Data - Mutable)     │
│   - Custom patterns              │
│   - Evolution stats              │
│   - User-taught responses        │
└──────────────────────────────────┘
               ↑
               │ reads/writes
┌──────────────────────────────────┐
│   chatbot_memory.json            │
│   (Learning Data)                │
│   - Learned conversations        │
│   - User preferences             │
└──────────────────────────────────┘
```

## Example Evolution Process

### Session 1
```
You: teach me: python | Python is awesome!
Bot: I learned! When you say 'python', I'll remember this response.

You: show stats
Bot: Custom Patterns Learned: 1
```

### Session 2 (Next time you run the chatbot)
```
Bot: ✓ Loaded custom patterns and evolution data

You: python
Bot: Python is awesome!

You: show stats
Bot: Total Conversations: 5, User-Taught Patterns: 1
```

## Methods for Self-Modification

### `teach_custom_pattern(trigger, response)`
User teaches the bot a new pattern. The bot stores this in `chatbot_config.json` and updates evolution stats.

### `self_modify_response(pattern_key, new_response)`
The bot can call this method to improve its own responses based on experience.

### `load_config()` / `save_config()`
These methods handle reading and writing to the mutable config file without touching core logic.

## Data Flow

```
1. User Input
   ↓
2. check learned_responses (memory.json)
   ↓
3. check custom_patterns (config.json) ← EVOLVED DATA
   ↓
4. check base patterns (core logic)
   ↓
5. Generate Response
   ↓
6. Learn & Save to both files
   ↓
7. Update evolution_stats in config.json
```

## Why This Design Works

✅ **Core Logic Never Changes** - All core functionality is in the immutable Python class

✅ **Easy Evolution** - New patterns are stored in JSON (very easy to modify)

✅ **Persistent Learning** - Config file survives between sessions

✅ **Safe Modifications** - Can't break core logic, only extend behavior

✅ **Transparent** - You can inspect `chatbot_config.json` to see what it learned

✅ **Scalable** - Easy to add more evolution capabilities

## Future Enhancements

- [ ] Self-generated pattern suggestions
- [ ] Automatic response quality scoring
- [ ] Predictive pattern creation
- [ ] Machine learning integration
- [ ] Multi-file config for different domains
- [ ] Version control for config changes
- [ ] Rollback to previous evolution states

---

**Made with ❤️ - A chatbot that learns and grows!**
