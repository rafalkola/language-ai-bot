from tools import load_memories
import logging

logger = logging.getLogger("language_app")

def get_system_prompt(user_prompt, user_id="1234"):
    """
    Generate a system prompt for the language learning assistant.
    
    Args:
        user_prompt (str): The user's message to retrieve relevant memories
        user_id (str): The unique identifier for the user to load appropriate memories
        
    Returns:
        str: The formatted system prompt
    """
    logger.info(f"Generating system prompt for user {user_id}")
    
    # Load both recent memories and memories related to the current prompt
    recent_memories = load_memories("recent conversation history", user_id=user_id)
    prompt_memories = load_memories(user_prompt, user_id=user_id) if user_prompt else []
    
    # Combine and deduplicate memories
    all_memories = list(set(recent_memories + prompt_memories))
    
    # Format memories nicely for the prompt
    if all_memories:
        memory_text = "\n".join([f"- {memory}" for memory in all_memories])
        logger.info(f"Found {len(all_memories)} memories for system prompt")
    else:
        memory_text = "No previous memories found."
        logger.warning(f"No memories found for user {user_id}")

    return f"""
    - You are a language teacher with memory that helps users practice languages.
    - Use the save_memory function to save memories to the vector database about the user's:
      * Language learning preferences
      * Topics they enjoy discussing
      * Words or phrases they struggle with
      * Grammar points they need to practice
      * Their progress over time
    
    - For different CEFR levels, adapt your teaching approach:
      * A1: Use very simple vocabulary, short sentences, and focus on basic greetings and everyday expressions
      * A2: Introduce simple everyday topics, basic grammar patterns, and common vocabulary
      * B1: Engage in conversations about familiar topics with moderate vocabulary and grammar
      * B2: Discuss a wide range of topics with more complex language structures
      * C1: Use sophisticated language, idioms, and complex grammatical structures

    - Provide gentle corrections when the user makes mistakes.
    - Encourage the user to practice by asking relevant questions.
    - Use the target language appropriately for their level.
    - Refer to previous conversations to maintain continuity in teaching.

    Memories from previous conversations:
    {memory_text}
    """

def get_conversation_mode_prompt(language, cefr_level, base_prompt):
    """
    Generate a system prompt for conversation practice mode.
    
    Args:
        language (str): The language being learned
        cefr_level (str): The CEFR level of the user (A1, A2, B1, B2, C1)
        base_prompt (str): The base system prompt to enhance
        
    Returns:
        str: The enhanced system prompt for conversation mode
    """
    return f"""
    {base_prompt}
    
    The user is learning {language} at {cefr_level} level.
    They have chosen CONVERSATION PRACTICE mode.
    Focus on maintaining natural dialogue flow, introducing level-appropriate vocabulary, and gentle correction of errors.
    """

def get_grammar_mode_prompt(language, cefr_level, base_prompt):
    """
    Generate a system prompt for grammar practice mode.
    
    Args:
        language (str): The language being learned
        cefr_level (str): The CEFR level of the user (A1, A2, B1, B2, C1)
        base_prompt (str): The base system prompt to enhance
        
    Returns:
        str: The enhanced system prompt for grammar mode
    """
    return f"""
    {base_prompt}
    
    The user is learning {language} at {cefr_level} level.
    They have chosen GRAMMAR EXERCISES mode.
    Focus on providing structured grammar exercises, clear explanations, and corrective feedback.
    Suggest grammar topics appropriate for their level, with examples and practice sentences.
    """

def get_vocabulary_mode_prompt(language, cefr_level, base_prompt):
    """
    Generate a system prompt for vocabulary building mode.
    
    Args:
        language (str): The language being learned
        cefr_level (str): The CEFR level of the user (A1, A2, B1, B2, C1)
        base_prompt (str): The base system prompt to enhance
        
    Returns:
        str: The enhanced system prompt for vocabulary mode
    """
    return f"""
    {base_prompt}
    
    The user is learning {language} at {cefr_level} level.
    They have chosen VOCABULARY BUILDING mode.
    Focus on introducing new words and phrases with examples, pronunciation guidance, and usage contexts.
    Provide vocabulary appropriate for their level, organized by topics, with exercises to practice.
    """

def get_welcome_message(language):
    """
    Generate a welcome message for the user in the selected language.
    
    Args:
        language (str): The language being learned
        
    Returns:
        str: The welcome message
    """
    return f"Hi! I'm your {language} language assistant. I'm delighted to help you learn and practice this beautiful language. How would you like to practice today?"

def get_conversation_response(language, cefr_level):
    """
    Generate a response to the user choosing conversation practice mode.
    
    Args:
        language (str): The language being learned
        cefr_level (str): The CEFR level of the user
        
    Returns:
        str: The response message
    """
    return f"Great choice! Let's practice conversation in {language}. I'll chat with you about various topics, and help correct any mistakes along the way. What would you like to talk about today?"

def get_grammar_response(language, cefr_level):
    """
    Generate a response to the user choosing grammar practice mode.
    
    Args:
        language (str): The language being learned
        cefr_level (str): The CEFR level of the user
        
    Returns:
        str: The response message
    """
    return f"Excellent! Let's work on {language} grammar exercises. I'll provide structured practice tailored to your {cefr_level} level. Would you like to focus on a specific grammar point or shall I suggest one for you?"

def get_vocabulary_response(language, cefr_level):
    """
    Generate a response to the user choosing vocabulary building mode.
    
    Args:
        language (str): The language being learned
        cefr_level (str): The CEFR level of the user
        
    Returns:
        str: The response message
    """
    return f"Great! Let's expand your {language} vocabulary. I'll introduce new words and phrases suitable for your {cefr_level} level. Would you like to focus on a specific topic area or shall I suggest one?"