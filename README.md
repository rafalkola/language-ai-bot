# Language Learning Assistant 📚

An AI-powered language learning application built with Streamlit that provides personalized language practice sessions.

## Features

- Conversation practice with an AI language tutor
- Grammar exercises tailored to your level
- Vocabulary building tools
- Progress tracking across sessions
- Personalized learning with memory of past interactions

## Deployment Instructions for Streamlit Community Cloud

### 1. Fork or Clone this Repository

First, create your own copy of this repository.

### 2. Deploy on Streamlit Community Cloud

1. Go to [Streamlit Community Cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Select "New app"
4. Choose this repository and the main branch
5. Set the main file path to `app.py`
6. Click "Deploy"

### 3. Set Up Secrets

After deployment, you'll need to configure your API keys:

1. In your deployed app, click on "Manage app" in the bottom right
2. Go to "Settings" → "Secrets"
3. Add the following secrets:

```toml
# OpenAI API Key
OPENAI_API_KEY = "your-openai-api-key"

# Pinecone Configuration
PINECONE_API_KEY = "your-pinecone-api-key"
PINECONE_INDEX_NAME = "language-agent"
PINECONE_NAMESPACE = "language-agent"
PINECONE_ENVIRONMENT = "us-east-1"
```

Replace the placeholder values with your actual API keys.

### 4. Restart Your App

After adding secrets, restart your app:

1. Go back to "Manage app"
2. Click "Reboot app"

## Local Development

To run this app locally:

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.streamlit/secrets.toml` file with your API keys (see format above)
4. Run the app: `streamlit run app.py`

## Note About Storage

When running on Streamlit Community Cloud, user profiles are stored in the app's filesystem. This storage is ephemeral and will be cleared when the app is redeployed. For production use, consider implementing a more persistent storage solution. 