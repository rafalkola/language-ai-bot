########################################################
# Import the necessary libraries
########################################################
import streamlit as st
from agent import agent
from prompts import (
    get_system_prompt, 
    get_conversation_mode_prompt,
    get_grammar_mode_prompt, 
    get_vocabulary_mode_prompt,
    get_welcome_message,
    get_conversation_response,
    get_grammar_response,
    get_vocabulary_response
)
import uuid
import os
from datetime import datetime
from tools import (
    load_memories, 
    save_memory,
    get_user_profile_path,
    save_user_profile, 
    load_user_profile,
    USER_PROFILES_DIR
)

########################################################
# Set the page config
########################################################
st.set_page_config(
    page_title="Language Learning Assistant", page_icon="📚",
    layout="centered", initial_sidebar_state="collapsed"
)

# Initialize session state variables if not present
for var in ['conversation_started', 'mode_selected', 'messages', 'user_id', 'lesson_ended', 'lesson_score']:
    if var not in st.session_state:
        st.session_state[var] = False if var not in ['messages', 'lesson_score'] else [] if var == 'messages' else None
        if var == 'user_id':
            st.session_state.user_id = str(uuid.uuid4())

# Load or create user profile
user_profile = load_user_profile(st.session_state.user_id)

########################################################
# Sidebar Configuration
########################################################
with st.sidebar:
    st.title("User ID")
    st.info("Copy this ID to return to your learning progress in future sessions.")
    
    # Display user ID with copy functionality
    st.code(st.session_state.user_id, language=None)
    
    # Allow updating user ID
    st.subheader("Change User ID")
    user_id_input = st.text_input("Enter a saved User ID:", 
                      value=st.session_state.user_id,
                      key="user_id_input")
    
    # Update User ID button
    if st.button("Update User ID"):
        old_user_id = st.session_state.user_id
        st.session_state.user_id = user_id_input
        # Reload user profile with new ID
        user_profile = load_user_profile(st.session_state.user_id)
        st.success(f"User ID updated from {old_user_id[:8]}... to {user_id_input[:8]}...")
        
        # Profile information display
        st.write("#### Profile Information:")
        st.write(f"- Created: {user_profile['created_at']}")
        st.write(f"- Languages studied: {len(user_profile['language_history'])}")
        st.write(f"- Last language: {user_profile['last_session']['language']}")
        st.write(f"- Last level: {user_profile['last_session']['level']}")
        
        # Check for existing memories
        memories = load_memories("", user_id=user_id_input)
        if memories:
            st.write(f"#### Found {len(memories)} memories")
            with st.expander("View memories"):
                for i, memory in enumerate(memories[:5]):
                    st.write(f"{i+1}. {memory[:100]}...")
        else:
            st.warning("No memories found for this user ID.")
        
        st.rerun()

########################################################
# Main Interface
########################################################
# App Header
st.title("Language Learning Assistant 📚")
st.subheader("Practice your language skills with a personal AI tutor")

# Add About section to main page
st.info("This app helps you practice language skills with an AI language tutor. Your preferences and progress are saved for personalized learning.")

# User ID notification banner with text instruction
st.warning("⚠️ **Important: Save Your User ID**\n\nYour User ID is how the app remembers your learning progress and preferences.\n\n👈 Click the menu icon in the top-left corner to access your ID")

# Language and level selection
col1, col2 = st.columns(2)

with col1:
    # Language selection
    languages = [
        "English", "French", "Spanish", "German", 
        "Portuguese", "Thai", "Polish", "Russian"
    ]
    # Use last selected language as default if available
    default_lang_index = 0
    if user_profile["last_session"]["language"] in languages:
        default_lang_index = languages.index(user_profile["last_session"]["language"])
    
    selected_language = st.selectbox("I want to learn:", languages, index=default_lang_index)

with col2:
    # CEFR Proficiency level
    levels = ["A1 (Beginner)", "A2 (Elementary)", "B1 (Intermediate)", 
             "B2 (Upper Intermediate)", "C1 (Advanced)"]
    # Use last selected level as default if available
    default_level_index = 0
    if user_profile["last_session"]["level"] in levels:
        default_level_index = levels.index(user_profile["last_session"]["level"])
    
    selected_level = st.selectbox("My current level:", levels, index=default_level_index)

# Extract the CEFR level code
cefr_level = selected_level.split()[0]

# Start conversation button
start_conversation = st.button("Start Learning", use_container_width=True)

# Divider between selections and chat
st.divider()

########################################################
# Conversation Initialization
########################################################
# Initialize conversation when Start Learning button is clicked
if start_conversation and not st.session_state.conversation_started:
    # Get welcome message from prompts.py
    welcome_message = get_welcome_message(selected_language)
    
    # Update user profile with selections
    user_profile["last_session"]["language"] = selected_language
    user_profile["last_session"]["level"] = selected_level
    
    # Add to language history
    user_profile["language_history"].append({
        "language": selected_language,
        "level": selected_level,
        "timestamp": datetime.now().isoformat()
    })
    
    # Save updated profile
    save_user_profile(st.session_state.user_id, user_profile)
    
    # Save a memory about session start
    save_memory(f"User started learning {selected_language} at {selected_level} level.", user_id=st.session_state.user_id)
    
    # Initialize conversation
    st.session_state.messages = [
        {"role": "system", "content": get_system_prompt("", user_id=st.session_state.user_id)},
        {"role": "assistant", "content": welcome_message}
    ]
    st.session_state.conversation_started = True
    st.session_state.lesson_ended = False
    st.session_state.lesson_score = None
    st.rerun()

########################################################
# Chat Interface
########################################################
# Display conversation if started
if st.session_state.get('messages', []) and st.session_state.conversation_started:
    # Show all messages except the system prompt
    for msg in st.session_state.messages[1:]:
        st.chat_message(msg["role"]).write(msg["content"])

    # Show practice mode selection if not yet selected
    if not st.session_state.mode_selected:
        st.write("Choose a practice mode:")
        
        col1, col2, col3 = st.columns(3)
        last_mode = user_profile["last_session"]["mode"]
        
        # Define a helper function for handling mode selection
        def handle_mode_selection(mode_type, column):
            mode_data = {
                "conversation": {
                    "message": "I'd like to practice conversation.",
                    "response_func": get_conversation_response,
                    "prompt_func": get_conversation_mode_prompt,
                    "button_text": "Conversation Practice"
                },
                "grammar": {
                    "message": "I'd like to practice grammar.",
                    "response_func": get_grammar_response,
                    "prompt_func": get_grammar_mode_prompt,
                    "button_text": "Grammar Exercises"
                },
                "vocabulary": {
                    "message": "I'd like to build my vocabulary.",
                    "response_func": get_vocabulary_response,
                    "prompt_func": get_vocabulary_mode_prompt,
                    "button_text": "Vocabulary Building"
                }
            }
            
            data = mode_data[mode_type]
            with column:
                if st.button(data["button_text"], use_container_width=True, 
                            disabled=last_mode==mode_type and st.session_state.mode_selected):
                    # Get mode response
                    mode_message = data["message"]
                    mode_response = data["response_func"](selected_language, cefr_level)
                    
                    # Update conversation
                    st.session_state.messages.append({"role": "user", "content": mode_message})
                    st.session_state.messages.append({"role": "assistant", "content": mode_response})
                    
                    # Update system prompt
                    system_prompt = st.session_state.messages[0]["content"]
                    enhanced_prompt = data["prompt_func"](selected_language, cefr_level, system_prompt)
                    st.session_state.messages[0]["content"] = enhanced_prompt
                    
                    # Update user profile and state
                    user_profile["last_session"]["mode"] = mode_type
                    save_user_profile(st.session_state.user_id, user_profile)
                    st.session_state.mode_selected = True
                    st.rerun()
        
        # Create buttons for each mode
        handle_mode_selection("conversation", col1)
        handle_mode_selection("grammar", col2)
        handle_mode_selection("vocabulary", col3)

    # User input chat interface (only shown when mode is selected)
    if st.session_state.mode_selected and not st.session_state.lesson_ended:
        prompt = st.chat_input("Type your message here...")

        if prompt:
            # Get enhanced system prompt with memories
            system_prompt = get_system_prompt(prompt, user_id=st.session_state.user_id)
            existing_prompt = st.session_state.messages[0]["content"]
            language_context = existing_prompt.split("The user is learning")[1] if "The user is learning" in existing_prompt else f"The user is learning {selected_language} at {cefr_level} level."
            
            # Update system prompt
            st.session_state.messages[0]["content"] = f"{system_prompt}\n{language_context}"
            
            # Add user message to conversation
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            # Get AI response
            with st.spinner("Thinking..."):
                response = agent(st.session_state.messages, user_id=st.session_state.user_id)
            
            # Add AI response to conversation
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)
        
    # Display lesson score and summary if lesson has ended
    if st.session_state.lesson_ended:
        st.divider()
        
        # Display score in a prominent way
        if st.session_state.lesson_score:
            score_col1, score_col2 = st.columns([1, 3])
            with score_col1:
                st.metric("Your Score", f"{st.session_state.lesson_score}/10")
            with score_col2:
                st.success("Lesson completed! See your evaluation above.")
        else:
            st.success("Lesson completed! See your evaluation above.")
        
        # Option to review progress in sidebar
        if "lesson_history" in user_profile and len(user_profile["lesson_history"]) > 1:
            with st.sidebar:
                st.divider()
                st.subheader("Learning Progress")
                lesson_count = len(user_profile["lesson_history"])
                
                # Calculate average score
                scores = [lesson.get("score", 0) for lesson in user_profile["lesson_history"] if lesson.get("score")]
                avg_score = sum(scores) / len(scores) if scores else 0
                
                st.write(f"Total lessons: {lesson_count}")
                st.write(f"Average score: {avg_score:.1f}/10")
                
                # Show last 5 lessons
                st.write("Recent lessons:")
                for lesson in user_profile["lesson_history"][-5:]:
                    st.write(f"- {lesson['language']} ({lesson['level']}): {lesson.get('score', 'N/A')}/10")
    
    # Action buttons at the bottom
    st.divider()
    
    # Create either a row with two buttons or just the reset button
    if st.session_state.mode_selected and not st.session_state.lesson_ended:
        # Show both End Lesson and Reset Conversation buttons side by side
        col1, col2 = st.columns(2)
        
        # End Lesson button - Column 1
        with col1:
            st.info("👨‍🏫 When done with your lesson, click for feedback and a score")
            if st.button("End Lesson", use_container_width=True):
                # Add message to get scoring and feedback
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Please evaluate my performance in this lesson. Give me a score out of 10 and a brief summary of what I did well and what I can improve on."
                })
                
                # Get AI response with score and summary
                with st.spinner("Evaluating your lesson..."):
                    # Update system prompt to instruct AI to provide scoring
                    score_instruction = "\nNow provide a genuine assessment of the user's performance. Give a score out of 10 and a concise summary of strengths and areas for improvement."
                    st.session_state.messages[0]["content"] += score_instruction
                    
                    evaluation = agent(st.session_state.messages, user_id=st.session_state.user_id)
                
                # Save evaluation as last response
                st.session_state.messages.append({"role": "assistant", "content": evaluation})
                
                # Extract score using simple heuristic (first number out of 10 mentioned)
                import re
                score_match = re.search(r'(\d+(\.\d+)?)/10', evaluation)
                score = float(score_match.group(1)) if score_match else None
                
                # Update session state
                st.session_state.lesson_ended = True
                st.session_state.lesson_score = score
                
                # Save lesson summary to user profile
                if "lesson_history" not in user_profile:
                    user_profile["lesson_history"] = []
                
                user_profile["lesson_history"].append({
                    "language": selected_language,
                    "level": selected_level,
                    "mode": user_profile["last_session"]["mode"],
                    "score": score,
                    "summary": evaluation,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Save memory about lesson completion
                save_memory(
                    f"User completed a {user_profile['last_session']['mode']} lesson in {selected_language} at {selected_level} level with a score of {score}/10.",
                    user_id=st.session_state.user_id
                )
                
                # Save updated profile
                save_user_profile(st.session_state.user_id, user_profile)
                
                st.rerun()
        
        # Reset Conversation button - Column 2
        with col2:
            st.info("👇 Click to change language, level, or practice mode")
            if st.button("Reset Conversation", use_container_width=True):
                st.session_state.messages = []
                st.session_state.conversation_started = False
                st.session_state.mode_selected = False
                st.session_state.lesson_ended = False
                st.session_state.lesson_score = None
                st.rerun()
    else:
        # Just show the Reset Conversation button
        st.info("👇 Click the button below if you wish to change your language, level, or practice mode.")
        if st.button("Reset Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_started = False
            st.session_state.mode_selected = False
            st.session_state.lesson_ended = False
            st.session_state.lesson_score = None
            st.rerun()
elif not start_conversation:
    # Initial instruction for users
    st.info("👆 Select your language and level, then click 'Start Learning' to begin your conversation.")
