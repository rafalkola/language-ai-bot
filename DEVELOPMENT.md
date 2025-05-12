# Language Learning Assistant - Development Documentation

This document provides technical details for developers who want to understand, contribute to, or extend the Language Learning Assistant application.

## Tech Stack

- **Frontend**: Streamlit
- **AI Model**: OpenAI GPT models
- **Vector Database**: Pinecone
- **Language**: Python 3.8+
- **Dependencies**: See `requirements.txt` for full list

## System Architecture

### Overview

The Language Learning Assistant is built on a modular architecture that separates concerns between:

1. User Interface (Streamlit)
2. Business Logic (Core Application)
3. External Services (OpenAI, Pinecone)
4. Data Persistence (User Profiles)

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────┐
│   User Interface│     │  Business Logic   │     │ External APIs │
│   (Streamlit)   │────▶│  (Core App)      │────▶│ (OpenAI,      │
└─────────────────┘     └──────────────────┘     │  Pinecone)    │
       ▲                        │                 └───────────────┘
       │                        ▼                        ▲
       │                ┌──────────────────┐            │
       └────────────────│  Data Persistence│────────────┘
                        │  (User Profiles) │
                        └──────────────────┘
```

### Component Details

#### User Interface (app.py)
- Manages the Streamlit UI components
- Handles user input and session state
- Coordinates between different application components

#### Business Logic
- **agent_logic.py**: Core intelligence that handles language learning strategies and tutoring logic
- **tools.py**: Core utility functions for processing inputs and outputs
- **prompts.py**: Template management for AI interactions

#### External Services Integration
- OpenAI API integration for language model interactions
- Pinecone vector database for contextual memory

#### Data Persistence
- User profile management in the `user_profiles/` directory
- Session state management

## Project Structure

```
language-ai-bot/
├── app.py              # Main application file
├── sub/                # Core modules directory
│   ├── agent_logic.py  # Core language learning intelligence
│   ├── tools.py        # Utility functions
│   └── prompts.py      # AI interaction templates
├── requirements.txt    # Project dependencies
├── .streamlit/         # Streamlit configuration
│   └── secrets.toml    # API keys and secrets
└── user_profiles/      # User data storage
```

## Key Flows

### Conversation Flow
1. User inputs text in the target language
2. Input is processed through `tools.py` functions
3. Context is retrieved from Pinecone 
4. A prompt is assembled using templates from `prompts.py`
5. The prompt is sent to OpenAI API
6. Response is processed and displayed to the user
7. Interaction is stored in Pinecone for future context

### Learning Progress Flow
1. User interactions are analyzed for language patterns
2. Progress metrics are calculated based on these interactions
3. User profile is updated with new metrics
4. Dashboard displays updated progress

## Development Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Pinecone API key

### Local Development

1. Clone the repository
```bash
git clone https://github.com/yourusername/language-ai-bot.git
cd language-ai-bot
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Create a `.streamlit/secrets.toml` file with your API keys
```toml
# OpenAI Configuration
OPENAI_API_KEY = "your-openai-api-key"

# Pinecone Configuration
PINECONE_API_KEY = "your-pinecone-api-key"
PINECONE_INDEX_NAME = "language-agent"
PINECONE_NAMESPACE = "language-agent"
PINECONE_ENVIRONMENT = "us-east-1"
```

4. Run the development server
```bash
streamlit run app.py
```

## Testing

The application includes several types of tests:

- **Unit Tests**: Test individual functions in isolation
- **Integration Tests**: Test interactions between components
- **System Tests**: Test end-to-end functionality

Run tests with:
```bash
pytest
```

## Deployment

### Streamlit Community Cloud

The application is designed to be deployed on Streamlit Community Cloud:

1. Push your changes to GitHub
2. Connect your GitHub repository to Streamlit Cloud
3. Configure the necessary secrets in the Streamlit Cloud dashboard
4. Deploy the application

### Other Deployment Options

The app can also be deployed using:
- Docker containers
- Heroku
- AWS Elastic Beanstalk

## Contributing Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure that your code follows the project's coding standards and includes appropriate tests.

## Architecture Decisions

### Vector Database
Pinecone was chosen for its optimized vector search capabilities and straightforward API, making it ideal for storing and retrieving conversation context.

### Streamlit UI
Streamlit was selected for its simplicity in creating data-focused web applications with minimal frontend code, allowing rapid development and iteration.

### OpenAI Integration
The application uses OpenAI models for their state-of-the-art language capabilities, particularly in multilingual contexts.

## Future Development

Areas for future expansion include:
- Speech-to-text and text-to-speech capabilities
- Additional language support
- Mobile application
- Enhanced analytics and learning metrics
- Spaced repetition system for vocabulary
- Community features for language exchange
- Custom UI components for a better user experience

## API Documentation

### Internal APIs

#### User Profile API
- `create_user_profile(username, language)`: Creates a new user profile
- `update_user_progress(username, metrics)`: Updates user learning metrics
- `get_user_history(username)`: Retrieves user's learning history

#### Memory API
- `store_interaction(user_id, conversation)`: Stores conversation in vector database
- `retrieve_context(user_id, query)`: Retrieves relevant conversation history using Pinecone

### External APIs

#### OpenAI API
The application interfaces with OpenAI's API for natural language processing.

#### Pinecone API
Used for vector similarity search to maintain conversation context.

## Troubleshooting

Common issues and their solutions:
- **API Rate Limiting**: Implement backoff strategy in `tools.py`
- **Memory Usage**: Optimize Pinecone queries for performance
- **Session Management**: Debug Streamlit session state issues

---

For additional questions, please open an issue on the GitHub repository. 