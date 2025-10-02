"""
Chat Interface for Churn Radar Conversation Layer
"""

import streamlit as st
from typing import List, Dict, Any, Tuple
from churn_core.orchestrator import ConversationOrchestrator
from churn_core.data import format_inr


def initialize_chat():
    """Initialize chat session state."""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    if "chat_orchestrator" not in st.session_state:
        try:
            st.session_state.chat_orchestrator = ConversationOrchestrator()
        except ValueError as e:
            st.error(f"Chat unavailable: {str(e)}")
            return False
    
    return True


def render_chat_interface():
    """Render the chat interface in sidebar."""
    
    # Initialize chat
    if not initialize_chat():
        return
    
    with st.sidebar:
        st.markdown("## 💬 Ask Retention Assistant")
        st.markdown("*Get insights, explore cohorts, compare groups*")
        
        # Chat container with fixed height
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for message in st.session_state.chat_messages:
                if message["role"] == "user":
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"**Assistant:** {message['content']}")
                    
                    # Show tool data if available
                    if message.get("tool_data"):
                        tool_data = message["tool_data"]
                        
                        # Format specific tool responses
                        if "recoverable_profit_30d" in tool_data:
                            # KPIs data
                            st.info(f"💰 ₹{format_inr(tool_data['recoverable_profit_30d'])} recoverable")
                        
                        elif isinstance(tool_data, list) and tool_data and "net_profit" in tool_data[0]:
                            # Cohorts list
                            st.markdown("**📊 Top Groups:**")
                            for cohort in tool_data[:3]:
                                st.markdown(f"• {cohort['name']}: {cohort['people']} people")
                        
                        elif "people" in tool_data and "comeback_odds" in tool_data:
                            # Cohort passport
                            st.info(f"👥 {tool_data['people']} people, {tool_data['comeback_odds']:.0%} comeback odds")
                
                st.markdown("---")
        
        # Chat input
        user_input = st.text_input(
            "Ask a question:", 
            placeholder="What should I do today?",
            key="chat_input"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Send", type="primary"):
                if user_input.strip():
                    handle_chat_message(user_input)
        
        with col2:
            if st.button("Clear Chat"):
                clear_chat()
        
        # Quick actions
        st.markdown("**Quick Actions:**")
        if st.button("📊 Today's Overview", use_container_width=True):
            st.session_state.quick_question = "What should I do today?"
            st.rerun()
        
        if st.button("🎯 Top Groups", use_container_width=True):
            st.session_state.quick_question = "Show me the top 3 groups"
            st.rerun()
        
        if st.button("💡 Explain Terms", use_container_width=True):
            st.session_state.quick_question = "What's Come-Back Odds?"
            st.rerun()
            
        # Handle quick questions
        if hasattr(st.session_state, 'quick_question'):
            question = st.session_state.quick_question
            del st.session_state.quick_question
            handle_chat_message(question)


def handle_chat_message(user_input: str):
    """Process user message and get assistant response."""
    
    # Add user message
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Get assistant response
    with st.spinner("🤔 Thinking..."):
        try:
            response, tool_data = st.session_state.chat_orchestrator.chat(user_input)
            
            # Add assistant response
            st.session_state.chat_messages.append({
                "role": "assistant", 
                "content": response,
                "tool_data": tool_data
            })
            
        except Exception as e:
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": f"Sorry, I encountered an error: {str(e)}"
            })
    
    # Rerun to update chat display
    st.rerun()


def clear_chat():
    """Clear chat history."""
    st.session_state.chat_messages = []
    if hasattr(st.session_state, 'chat_orchestrator'):
        st.session_state.chat_orchestrator.reset_conversation()
    st.rerun()


def render_suggested_questions():
    """Render suggested questions based on current context."""
    
    suggestions = [
        "What should I do today?",
        "Show me the Premium engagement lapsed group",
        "Compare Premium vs Payment-sensitive groups", 
        "What's Come-Back Odds?",
        "Export the top group"
    ]
    
    st.markdown("**💡 Try asking:**")
    
    for suggestion in suggestions:
        if st.button(f"❓ {suggestion}", key=f"suggest_{hash(suggestion)}"):
            handle_chat_message(suggestion)


# Conversation starter for main dashboard
def render_conversation_starter():
    """Render conversation starter on main dashboard."""
    
    with st.expander("💬 Ask the Retention Assistant", expanded=False):
        st.markdown("Get instant insights about your customer groups:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 What should I do today?"):
                st.session_state.starter_question = "What should I do today?"
                st.rerun()
        
        with col2:
            if st.button("🎯 Show top groups"):
                st.session_state.starter_question = "Show me the top 3 groups"
                st.rerun()
        
        with col3:
            if st.button("💡 Explain terms"):
                st.session_state.starter_question = "What's Come-Back Odds?"
                st.rerun()
        
        # Handle starter questions
        if hasattr(st.session_state, 'starter_question'):
            question = st.session_state.starter_question
            del st.session_state.starter_question
            
            # Initialize chat if needed
            if initialize_chat():
                with st.spinner("🤔 Getting insights..."):
                    try:
                        response, tool_data = st.session_state.chat_orchestrator.chat(question)
                        
                        st.success("**Assistant:**")
                        st.markdown(response)
                        
                        if tool_data:
                            if "recoverable_profit_30d" in tool_data:
                                st.metric("💰 Recoverable Profit", f"₹{format_inr(tool_data['recoverable_profit_30d'])}")
                                st.metric("📊 Ready Groups", tool_data['ready_groups_today'])
                                st.metric("👥 Expected Reactivations", tool_data['expected_reactivations'])
                        
                    except Exception as e:
                        st.error(f"Sorry, I encountered an error: {str(e)}")