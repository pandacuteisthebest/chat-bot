import json
import os
import requests
from datetime import datetime
from difflib import SequenceMatcher
import random

class AdvancedChatbot:
    def __init__(self, 
                 local_custom_file="custom_responses.json",
                 config_file="chatbot_config.json",
                 memory_file="chatbot_memory.json",
                 github_owner="pandacuteisthebest",
                 github_repo="chat-bot",
                 github_token=None):
        
        # File paths
        self.local_custom_file = local_custom_file
        self.config_file = config_file
        self.memory_file = memory_file
        
        # GitHub API info
        self.github_owner = github_owner
        self.github_repo = github_repo
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.github_api_url = f"https://api.github.com/repos/{github_owner}/{github_repo}/contents"
        self.github_raw_url = f"https://raw.githubusercontent.com/{github_owner}/{github_repo}/main"
        
        # Data storage
        self.conversation_history = []
        self.learned_responses = {}
        self.custom_patterns = {}  # Local custom taught responses
        self.user_preferences = {}
        self.evolution_stats = {
            "total_conversations": 0,
            "successful_responses": 0,
            "user_taught_patterns": 0,
            "self_modified_count": 0
        }
        
        # Load all data (prefer remote over local)
        self.load_custom_responses()
        self.load_remote_config()
        self.load_memory()
        self.initialize_base_responses()
    
    def fetch_remote_file(self, filename):
        """Fetch a file from GitHub remote repository"""
        try:
            url = f"{self.github_raw_url}/{filename}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ Loaded {filename} from remote repository\n")
                return response.json()
            else:
                print(f"⚠ Remote {filename} not found (HTTP {response.status_code})")
                return None
        except Exception as e:
            print(f"⚠ Could not fetch {filename} from remote: {str(e)}")
            return None
    
    def load_remote_config(self):
        """Load config and evolution data from GitHub (prefers remote)"""
        remote_config = self.fetch_remote_file("chatbot_config.json")
        
        if remote_config:
            self.learned_responses = remote_config.get('learned_responses', {})
            self.user_preferences = remote_config.get('user_preferences', {})
            self.evolution_stats = remote_config.get('evolution_stats', self.evolution_stats)
            print("✓ Using remote configuration\n")
        else:
            # Fallback to local config
            self.load_local_config()
    
    def load_local_config(self):
        """Fallback: Load config from local file if remote unavailable"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.learned_responses = config.get('learned_responses', {})
                    self.user_preferences = config.get('user_preferences', {})
                    self.evolution_stats = config.get('evolution_stats', self.evolution_stats)
                    print("✓ Loaded local configuration (remote unavailable)\n")
            except:
                print("⚠ Could not load local configuration")
    
    def load_custom_responses(self):
        """Load custom taught responses from LOCAL file only"""
        if os.path.exists(self.local_custom_file):
            try:
                with open(self.local_custom_file, 'r') as f:
                    data = json.load(f)
                    self.custom_patterns = data.get('custom_patterns', {})
                    print("✓ Loaded custom responses from local file\n")
            except:
                pass
    
    def load_memory(self):
        """Load conversation memory from local file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    # Note: We don't override learned_responses from memory if already loaded from remote
                    if not self.learned_responses:
                        self.learned_responses = data.get('learned_responses', {})
                    print("✓ Loaded conversation memory\n")
            except:
                pass
    
    def save_custom_responses(self):
        """Save custom taught responses to LOCAL file only"""
        with open(self.local_custom_file, 'w') as f:
            json.dump({
                'custom_patterns': self.custom_patterns,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        print("✓ Custom responses saved locally\n")
    
    def save_local_config(self):
        """Save config to local file (backup)"""
        with open(self.config_file, 'w') as f:
            json.dump({
                'learned_responses': self.learned_responses,
                'user_preferences': self.user_preferences,
                'evolution_stats': self.evolution_stats,
                'version': "1.0",
                'last_modified': datetime.now().isoformat()
            }, f, indent=2)
    
    def push_to_github(self):
        """Push updated config and evolution to GitHub"""
        if not self.github_token:
            print("⚠ No GitHub token found. Set GITHUB_TOKEN env variable to sync.")
            return False
        
        try:
            # Prepare config data
            config_data = {
                'learned_responses': self.learned_responses,
                'user_preferences': self.user_preferences,
                'evolution_stats': self.evolution_stats,
                'version': "1.0",
                'last_modified': datetime.now().isoformat()
            }
            
            headers = {
                "Authorization": f"token {self.github_token}",
                "Content-Type": "application/json"
            }
            
            # Get current SHA for chatbot_config.json
            response = requests.get(
                f"{self.github_api_url}/chatbot_config.json",
                headers=headers
            )
            
            if response.status_code == 200:
                current_sha = response.json()['sha']
                
                # Update config file
                update_response = requests.put(
                    f"{self.github_api_url}/chatbot_config.json",
                    headers=headers,
                    json={
                        "message": "Auto-sync: Update chatbot config and evolution stats",
                        "content": json.dumps(config_data, indent=2),
                        "sha": current_sha
                    }
                )
                
                if update_response.status_code in [200, 201]:
                    print("✓ Successfully synced config to GitHub\n")
                    return True
                else:
                    print(f"⚠ Failed to push to GitHub: {update_response.status_code}")
                    return False
        except Exception as e:
            print(f"⚠ Could not push to GitHub: {str(e)}")
            return False
    
    def initialize_base_responses(self):
        """Initialize base conversation patterns"""
        self.base_responses = {
            "greeting": ["How are you?", "Nice to meet you!", "Hello! What's up?", "Hi there! How's it going?"],
            "positive": ["Glad to hear it!", "That's awesome!", "Wonderful news!", "I'm happy for you!"],
            "fine": ["Ok!"],
            "negative": ["I'm sorry to hear that.", "That's tough.", "Hang in there!", "Things will get better!"],
            "confused": ["I didn't quite understand that.", "Can you rephrase?", "Tell me more about that.", "Interesting, go on..."],
            "farewell": ["Goodbye! See you later!", "Take care!", "See you soon!", "Bye!"]
        }
    
    def extract_keywords(self, text):
        """Extract keywords from user input"""
        stop_words = {'the', 'a', 'is', 'it', 'i', 'and', 'or', 'but', 'to', 'of', 'in', 'on', 'at'}
        words = [w.lower() for w in text.split() if w.lower() not in stop_words]
        return words
    
    def keywords_to_string(self, text):
        """Convert keywords to a string key for JSON serialization"""
        keywords = self.extract_keywords(text)
        return "|".join(sorted(keywords))
    
    def learn_from_conversation(self, user_input, bot_response):
        """Learn from successful conversations"""
        key = self.keywords_to_string(user_input)
        if key not in self.learned_responses:
            self.learned_responses[key] = []
        self.learned_responses[key].append(bot_response)
        self.evolution_stats["successful_responses"] += 1
    
    def teach_custom_pattern(self, trigger, response):
        """User teaches the bot a new pattern (stored locally)"""
        if trigger not in self.custom_patterns:
            self.custom_patterns[trigger] = []
        self.custom_patterns[trigger].append(response)
        self.evolution_stats["user_taught_patterns"] += 1
        self.save_custom_responses()
        print(f"Bot: I learned! When you say '{trigger}', I'll remember this response.")
        print(f"(Saved locally in {self.local_custom_file})\n")
    
    def find_learned_response(self, user_input):
        """Check if we've seen similar input before"""
        key = self.keywords_to_string(user_input)
        
        # Check custom patterns first (LOCAL - user taught)
        for pattern, responses in self.custom_patterns.items():
            if pattern.lower() in user_input.lower() and responses:
                return random.choice(responses)
        
        # Exact match in learned responses (from REMOTE/LOCAL)
        if key in self.learned_responses:
            return random.choice(self.learned_responses[key])
        
        # Find similar patterns
        user_keywords = set(self.extract_keywords(user_input))
        for stored_key, responses in self.learned_responses.items():
            stored_keywords = set(stored_key.split("|")) if stored_key else set()
            if stored_keywords:
                similarity = len(user_keywords & stored_keywords) / max(len(user_keywords | stored_keywords), 1)
                if similarity > 0.5 and responses:
                    return random.choice(responses)
        
        return None
    
    def get_dynamic_response(self, user_input):
        """Generate dynamic response based on input analysis"""
        user_input_lower = user_input.lower().strip()
        
        # Check learned responses first
        learned = self.find_learned_response(user_input)
        if learned:
            return f"Bot: {learned}"
        
        # ORIGINAL FIXED RESPONSES
        if user_input_lower in ["hi", "hello"]:
            print("Bot: How are you?")
            feeling = input("You: ").lower().strip()
            
            if feeling == "good":
                return "Bot: Glad to hear it!"
            elif feeling == "fine":
                return "Bot: Ok!"
            elif feeling in ["bad", "not good", "not fine"]:
                return "Bot: I'm sorry to hear that."
            else:
                return "Bot: ERROR"
        
        elif user_input_lower == "goodbye":
            print("Bot: Rude!")
            apology = input("You: ").lower().strip()
            
            if apology in ["sorry", "sory"]:
                return "Bot: You are forgiven!"
            else:
                return "Bot: ERROR"
        
        elif user_input_lower == "let it grow":
            return """Bot: 
You don't know me, but my name's Cy
I'm just the O'Hare Delivery Guy
But it seems like trees might be worth a try
So, I say let it grow

Let it grow, let it grow
You can't reap what you don't sow
Plant a seed inside the Earth
Just one way to know it's worth
Let's celebrate the world's rebirth
We say let it grow"""
        
        elif user_input_lower == "frick you":
            return "Bot: Artless dirt-rotten blockhead!"
        
        elif user_input_lower == "how are you":
            return "Bot: Oh, just fantastic, since I get to listen to your questions all day!"
        
        elif any(phrase in user_input_lower for phrase in ["stop the music", "dont stop the music", "don't stop the music"]):
            return """Bot:
Please don't stop the music (Music, music, music, music)
Please don't stop the music (Music, music, music, music)"""
        
        # CUSTOM TEACHING
        elif user_input_lower.startswith("teach me:"):
            parts = user_input_lower.replace("teach me:", "").split("|")
            if len(parts) == 2:
                trigger = parts[0].strip()
                response = parts[1].strip()
                self.teach_custom_pattern(trigger, response)
                return f"Bot: I learned! When you say '{trigger}', I'll remember this response."
            else:
                return "Bot: Use format: teach me: [trigger] | [response]"
        
        # SHOW STATS
        elif user_input_lower == "show stats":
            stats = self.evolution_stats
            return f"""Bot: Evolution Statistics:
- Total Conversations: {stats['total_conversations']}
- Successful Responses: {stats['successful_responses']}
- User-Taught Patterns: {stats['user_taught_patterns']}
- Self-Modified: {stats['self_modified_count']}
- Custom Patterns Learned: {len(self.custom_patterns)}
- Remote Config Used: Yes ✓"""
        
        # SHOW CONFIG
        elif user_input_lower == "show config":
            if self.custom_patterns:
                patterns_str = ", ".join([f"'{k}'" for k in self.custom_patterns.keys()])
                return f"Bot: I've learned these custom patterns (LOCAL): {patterns_str}"
            else:
                return "Bot: I haven't learned any custom patterns yet. Use 'teach me: trigger | response'"
        
        # SYNC TO GITHUB
        elif user_input_lower == "sync github":
            if self.push_to_github():
                return "Bot: Successfully synced evolution data to GitHub!"
            else:
                return "Bot: Failed to sync to GitHub. Check your GITHUB_TOKEN."
        
        # DYNAMIC PATTERNS
        elif any(word in user_input_lower for word in ["hi", "hello", "hey"]):
            response = random.choice(self.base_responses["greeting"])
            return f"Bot: {response}"
        
        elif any(word in user_input_lower for word in ["good", "great", "awesome", "fantastic", "wonderful"]):
            response = random.choice(self.base_responses["positive"])
            return f"Bot: {response}"
        
        elif any(word in user_input_lower for word in ["bad", "sad", "terrible", "awful", "hate"]):
            response = random.choice(self.base_responses["negative"])
            return f"Bot: {response}"
        
        elif "name" in user_input_lower:
            if "your name" in user_input_lower or "you" in user_input_lower:
                return "Bot: I'm an AI Chatbot! What's your name?"
            elif "my name" in user_input_lower:
                name = user_input_lower.replace("my name is", "").replace("i'm", "").strip()
                self.user_preferences['name'] = name
                return f"Bot: Nice to meet you, {name}!"
        
        elif "help" in user_input_lower or "what can you do" in user_input_lower:
            return """Bot: I can:
- Chat with you naturally
- teach me: [trigger] | [response] (teach me new patterns - SAVED LOCALLY)
- show stats (see my evolution)
- show config (see my custom patterns)
- sync github (push changes to remote repository)
- Type 'quit' to exit"""
        
        else:
            responses = [
                "Bot: That's interesting! Tell me more.",
                "Bot: I see. Can you elaborate?",
                "Bot: How does that make you feel?",
                "Bot: That's cool! Why do you say that?",
                "Bot: I'm learning about that. Anything else?",
                "Bot: ERROR"
            ]
            return random.choice(responses)
    
    def chat(self):
        """Main chatbot loop"""
        print("=" * 50)
        print("🤖 Self-Evolving AI Chatbot with GitHub Sync")
        print("=" * 50)
        print("I learn from our conversations and evolve!")
        print("Remote config loaded ✓\n")
        print("Type 'help' for options or 'quit' to exit.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["quit", "exit"]:
                    print("Bot: Goodbye! I've learned a lot from our chat. See you next time!")
                    self.save_local_config()
                    self.save_custom_responses()
                    self.push_to_github()
                    break
                
                response = self.get_dynamic_response(user_input)
                print(response)
                
                response_text = response.replace("Bot: ", "")
                self.learn_from_conversation(user_input, response_text)
                self.conversation_history.append({
                    "user": user_input,
                    "bot": response_text,
                    "timestamp": datetime.now().isoformat()
                })
                
                self.evolution_stats["total_conversations"] += 1
                
                if len(self.conversation_history) % 5 == 0:
                    self.save_local_config()
                    self.save_custom_responses()
            
            except KeyboardInterrupt:
                print("\n\nBot: Saving and syncing...")
                self.save_local_config()
                self.save_custom_responses()
                self.push_to_github()
                break
            except Exception as e:
                print(f"Bot: An error occurred: {str(e)}")

if __name__ == "__main__":
    chatbot = AdvancedChatbot()
    chatbot.chat()
