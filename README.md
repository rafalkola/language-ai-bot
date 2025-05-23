# Language Learning Assistant 📚

Your personal AI language tutor that helps you learn and practice languages through natural conversations and interactive exercises. Whether you're a beginner or advanced learner, this assistant adapts to your level and helps you improve your language skills in a fun and engaging way.

## Link to the [App](https://language-ai-bot.streamlit.app/)

## What You Can Do

### Practice Conversations
- Have natural conversations with an AI tutor
- Get instant feedback on your grammar and vocabulary
- Practice speaking and comprehension in a safe environment
- Learn common phrases and expressions for daily use

### Learn at Your Own Pace
- Start with simple greetings and basic phrases
- Progress to more complex conversations
- Practice specific topics you're interested in
- Get help with pronunciation and grammar

### Track Your Progress
- See your improvement over time
- Get personalized recommendations
- Review your learning history
- Celebrate your achievements

## How to Use

1. **Start a Conversation**
   - Type your message in your target language
   - The AI tutor will respond and help you practice
   - Don't worry about making mistakes - that's how we learn!

2. **Practice Grammar**
   - The tutor will gently correct your mistakes
   - Get explanations for grammar rules
   - Practice with example sentences
   - Build confidence in your writing

3. **Build Vocabulary**
   - Learn new words in context
   - Get examples of how to use new vocabulary
   - Review words you've learned
   - Practice with flashcards and exercises

4. **Track Your Learning**
   - See your progress over time
   - Get personalized learning tips
   - Review your conversation history
   - Set and achieve learning goals

## Tips for Success

- Practice regularly, even for short periods
- Don't be afraid to make mistakes
- Try to use new words and phrases you learn
- Ask questions when you're unsure
- Set realistic goals for your learning journey

## Learning Goals

The app helps you achieve:
- Better conversational skills
- Improved grammar and vocabulary
- More natural pronunciation
- Cultural understanding
- Confidence in using the language

Remember: Learning a language is a journey, and this app is here to make it enjoyable and effective. Start your language learning adventure today! 🌍✨ 

## Application Structure

The Language Learning Assistant consists of these core components:

- **app.py**: Main application entry point that initializes the Streamlit interface and manages the app workflow
- **agent_logic.py**: Core intelligence of the application that handles the language learning strategies and tutoring logic
- **tools.py**: Utility functions for API interactions, data processing, and helper methods
- **prompts.py**: Contains template prompts used for AI interactions with carefully crafted system messages
- **user_profiles/**: Directory storing user data and learning history in JSON format

## How it works:
The user chats with an AI tutor via a Streamlit web app. Each message is enriched with past interactions retrieved from a Pinecone vector database and sent to OpenAI for a personalized response. Meaningful messages are stored back in Pinecone for future context. User profiles and preferences are saved locally in JSON files.
