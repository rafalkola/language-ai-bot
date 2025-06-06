import os
import uuid
import json
import logging
import streamlit as st
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from datetime import datetime, timezone

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("language_app")

# Define constants
USER_PROFILES_DIR = "user_profiles"

# Create user profiles directory if it doesn't exist
if not os.path.exists(USER_PROFILES_DIR):
    os.makedirs(USER_PROFILES_DIR)

try:
    # Initialize Pinecone for vector database - updated for Pinecone v6.0+
    pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    
    # Check if index exists, if not create it
    index_name = st.secrets["PINECONE_INDEX_NAME"]
    # Get list of indexes
    indexes = pc.list_indexes()
    
    if index_name not in [index.name for index in indexes]:
        # Create the index if it doesn't exist
        pc.create_index(
            name=index_name,
            dimension=1536,  # OpenAI embedding dimension
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=st.secrets["PINECONE_ENVIRONMENT"])
        )
        logger.info(f"Created new Pinecone index: {index_name}")
    
    # Connect to the index
    index = pc.Index(index_name)
    logger.info(f"Successfully connected to Pinecone index {index_name}")
except Exception as e:
    logger.error(f"Error connecting to Pinecone: {str(e)}")
    # Create a fallback for development/testing
    class DummyIndex:
        def __init__(self):
            self.memories = {}
            logger.warning("Using DummyIndex which stores memories in memory only (data will be lost on restart)")
            
        def upsert(self, vectors, namespace=None):
            try:
                for vector in vectors:
                    user_id = vector["metadata"]["user_id"]
                    if user_id not in self.memories:
                        self.memories[user_id] = []
                    self.memories[user_id].append(vector["metadata"]["payload"])
                return {"upserted_count": len(vectors)}
            except Exception as e:
                logger.error(f"Error in DummyIndex upsert: {str(e)}")
                return {"upserted_count": 0, "error": str(e)}
            
        def query(self, vector, filter=None, namespace=None, include_metadata=True, top_k=10):
            try:
                # Extract user_id from filter
                user_id = "unknown"
                if filter and "$and" in filter:
                    for condition in filter["$and"]:
                        if "user_id" in condition:
                            user_id = condition["user_id"]["$eq"]
                elif filter and "user_id" in filter:
                    user_id = filter["user_id"]["$eq"]
                
                matches = []
                if user_id in self.memories:
                    for memory in self.memories[user_id]:
                        # Create a match object similar to Pinecone's response
                        match = type('obj', (object,), {
                            'id': str(uuid.uuid4()),
                            'score': 0.9,  # Dummy score
                            'metadata': {'payload': memory}
                        })
                        matches.append(match)
                
                return {"matches": matches[:top_k]}
            except Exception as e:
                logger.error(f"Error in DummyIndex query: {str(e)}")
                return {"matches": [], "error": str(e)}
    
    index = DummyIndex()
    logger.warning("Using dummy in-memory index as fallback")

# Initialize OpenAI for embeddings 
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Define the tools
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": "Save a memory to the vector database",
            "parameters": {
                "type": "object",
                "properties": {
                    "memory": {"type": "string"}
                },
                "required": ["memory"]
            },
        },
    },
]

#######################################
# User Profile Management Functions
#######################################
def get_user_profile_path(user_id):
    """
    Get the file path for a user profile.
    
    Args:
        user_id (str): The unique identifier for the user
        
    Returns:
        str: The path to the user's profile JSON file
    """
    return os.path.join(USER_PROFILES_DIR, f"{user_id}.json")

def save_user_profile(user_id, profile_data):
    """
    Save a user's profile data to disk.
    
    Args:
        user_id (str): The unique identifier for the user
        profile_data (dict): The user profile data to save
        
    Returns:
        None
    """
    profile_path = get_user_profile_path(user_id)
    with open(profile_path, 'w') as f:
        json.dump(profile_data, f)
    logger.info(f"Saved profile for user {user_id}")

def load_user_profile(user_id):
    """
    Load a user's profile from disk or create a new one if it doesn't exist.
    
    Args:
        user_id (str): The unique identifier for the user
        
    Returns:
        dict: The user's profile data
    """
    profile_path = get_user_profile_path(user_id)
    if os.path.exists(profile_path):
        try:
            with open(profile_path, 'r') as f:
                profile_data = json.load(f)
                logger.info(f"Loaded existing profile for user {user_id}")
                return profile_data
        except Exception as e:
            logger.error(f"Error loading user profile: {str(e)}")
            # Return a new profile if there was an error
    
    # Create a new profile if none exists
    new_profile = {
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "language_history": [],
        "last_session": {
            "language": None,
            "level": None,
            "mode": None
        }
    }
    logger.info(f"Created new profile for user {user_id}")
    return new_profile


def get_embeddings(string_to_embed):
    try:
        response = client.embeddings.create(
            input=string_to_embed,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        # Return a dummy embedding for fallback
        return [0.0] * 1536  # Typical embedding size

def save_memory(memory, user_id="1234"):
    """
    Save a memory to the vector database with user_id tag
    
    Args:
        memory (str): The memory text to save
        user_id (str): The user's unique identifier
        
    Returns:
        str: Status message
    """
    try:
        # Add timestamp to the memory for better context
        current_time = datetime.now(tz=timezone.utc)
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S UTC")
        enhanced_memory = f"[{formatted_time}] {memory}"
        
        logger.info(f"Saving memory for user {user_id}: {memory[:50]}...")
        
        # Step 1: Embed the memory
        vector = get_embeddings(enhanced_memory)
        
        # Step 2: Build the vector document to be stored
        memory_id = str(uuid.uuid4())
        
        # Step 3: Store the vector document in the vector database
        result = index.upsert(
            vectors=[
                {
                    "id": memory_id,
                    "values": vector,
                    "metadata": {
                        "payload": enhanced_memory,
                        "timestamp": str(current_time),
                        "type": "recall", # Define the type of document i.e recall memory
                        "user_id": user_id,
                    },
                }
            ],
            namespace=st.secrets.get("PINECONE_NAMESPACE", "default")
        )
        
        logger.info(f"Memory saved successfully: {result}")
        return "Memory saved successfully"
    except Exception as e:
        logger.error(f"Error saving memory: {str(e)}")
        return f"Error saving memory: {str(e)}"

def load_memories(prompt, user_id="1234"):
    """
    Load relevant memories for a user based on a prompt
    
    Args:
        prompt (str): The prompt to find relevant memories for
        user_id (str): The user's unique identifier
        
    Returns:
        list: List of relevant memories
    """
    try:
        logger.info(f"Loading memories for user {user_id} with prompt: {prompt[:50]}...")
        
        # If prompt is empty, just retrieve recent memories
        search_text = prompt if prompt else "recent memories"
        
        top_k = 10
        vector = get_embeddings(search_text)
        
        filter_dict = {
            "$and": [
                {"user_id": {"$eq": user_id}},
                {"type": {"$eq": "recall"}}
            ]
        }
        
        namespace = st.secrets.get("PINECONE_NAMESPACE", "default")
        logger.info(f"Querying namespace: {namespace} with filter: {filter_dict}")
        
        response = index.query(
            vector=vector,
            filter=filter_dict,
            namespace=namespace,
            include_metadata=True,
            top_k=top_k,
        )
        
        memories = []
        if matches := response.get("matches"):
            logger.info(f"Found {len(matches)} matching memories")
            memories = [m.metadata["payload"] for m in matches]
            for memory in memories[:3]:  # Log first few for debugging
                logger.info(f"Memory sample: {memory[:100]}...")
        else:
            logger.warning(f"No memories found for user {user_id}")
            
        return memories
    except Exception as e:
        logger.error(f"Error loading memories: {str(e)}")
        return [f"Error loading memories: {str(e)}"]