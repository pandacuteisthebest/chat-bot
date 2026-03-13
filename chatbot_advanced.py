# This is a self-evolving chatbot script

class SelfEvolvingChatbot:
    def __init__(self):
        self.knowledge_base = []

    def learn(self, new_info):
        self.knowledge_base.append(new_info)
        
    def respond(self, query):
        for knowledge in self.knowledge_base:
            if query.lower() in knowledge.lower():
                return f'Based on what I learned, {knowledge}'
        return "I'm sorry, I don't know the answer to that yet."

# Example Usage
if __name__ == '__main__':
    chatbot = SelfEvolvingChatbot()
    chatbot.learn('Python is a programming language.')
    print(chatbot.respond('What is Python?'))
    chatbot.learn('GitHub is a code hosting platform. ')
    print(chatbot.respond('What is GitHub?'))