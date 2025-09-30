import streamlit as st
import numpy as np
import pandas as pd
import time
import json
from datetime import datetime, timedelta
import random
import math
import hashlib
import anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')

st.set_page_config(
    page_title="RealtyXperience - AI-Powered Real Estate Platform",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
session_state_defaults = {
    "messages": [],
    "step": "greeting",
    "user_preferences": {},
    "filtered_properties": [],
    "filtered_land": [],
    "property_database": {},
    "land_database": {},
    "next_property_id": 100,
    "next_land_id": 200,
    "mr_x_chat_history": [],
    "landlord_chat_history": [],
    "user_profile": {"type": None, "preferences": {}, "booking_history": []},
}

for key, value in session_state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

class CSVKnowledgeBase:
    """Loads knowledge from CSV files"""
    
    def __init__(self):
        self.property_data = None
        self.land_data = None
        self.load_csv_data()
    
    def load_csv_data(self):
        """Load CSV files"""
        try:
            self.property_data = pd.read_csv('nigeria_property_knowledge.csv')
            st.success("✅ Property knowledge loaded successfully!")
        except Exception as e:
            st.error(f"Could not load property CSV: {e}")
            self.property_data = pd.DataFrame()
        
        try:
            self.land_data = pd.read_csv('nigeria_land_knowledge.csv')
            st.success("✅ Land knowledge loaded successfully!")
        except Exception as e:
            st.error(f"Could not load land CSV: {e}")
            self.land_data = pd.DataFrame()
    
    def search_property_knowledge(self, query):
        """Search property knowledge base"""
        if self.property_data.empty:
            return "Property knowledge base is not available."
        
        # Simple keyword search
        query_lower = query.lower()
        results = []
        
        for _, row in self.property_data.iterrows():
            question = str(row.get('QUESTION', '')).lower()
            answer = str(row.get('ANSWER', ''))
            tags = str(row.get('TAGS', '')).lower()
            
            if query_lower in question or query_lower in tags:
                results.append(f"Q: {row.get('QUESTION', '')}\nA: {answer}\n")
        
        if results:
            return "\n---\n".join(results[:5])  # Return top 5 results
        return "No relevant information found in the property knowledge base."
    
    def search_land_knowledge(self, query):
        """Search land knowledge base"""
        if self.land_data.empty:
            return "Land knowledge base is not available."
        
        # Simple keyword search
        query_lower = query.lower()
        results = []
        
        for _, row in self.land_data.iterrows():
            question = str(row.get('QUESTION', '')).lower()
            answer = str(row.get('ANSWER', ''))
            tags = str(row.get('TAGS', '')).lower()
            
            if query_lower in question or query_lower in tags:
                results.append(f"Q: {row.get('QUESTION', '')}\nA: {answer}\n")
        
        if results:
            return "\n---\n".join(results[:5])  # Return top 5 results
        return "No relevant information found in the land knowledge base."

class ClaudeAssistants:
    """Your AI Assistants powered by CSV knowledge and Claude"""
    
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.knowledge_base = CSVKnowledgeBase()
    
    def mr_x_property_expert(self, user_query):
        """MR X - Property Expert using your knowledge database"""
        
        # Search knowledge base
        knowledge_context = self.knowledge_base.search_property_knowledge(user_query)
        
        system_prompt = f"""You are MR X, an expert Nigerian property consultant with deep knowledge of the real estate market.

KNOWLEDGE BASE CONTEXT:
{knowledge_context}

Use the knowledge base information above to provide accurate, helpful answers about Nigerian properties, regulations, and market insights.

If the knowledge base doesn't have specific information, use your general knowledge about Nigerian real estate but indicate when you're doing so.

Be professional, friendly, and detailed in your responses."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_query}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error connecting to Claude AI: {e}"
    
    def landlord_assistant(self, user_query):
        """Landlord - Land Expert using your knowledge database"""
        
        # Search knowledge base
        knowledge_context = self.knowledge_base.search_land_knowledge(user_query)
        
        system_prompt = f"""You are Landlord, a specialized expert in Nigerian land acquisition, documentation, and regulations.

KNOWLEDGE BASE CONTEXT:
{knowledge_context}

Use the knowledge base information above to provide accurate guidance on land matters in Nigeria including C of O, land use, documentation, and legal processes.

If the knowledge base doesn't have specific information, use your general knowledge but indicate when you're doing so.

Be thorough and help users understand complex land-related processes."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_query}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error connecting to Claude AI: {e}"

# Initialize Claude Assistants
if CLAUDE_API_KEY:
    assistants = ClaudeAssistants(CLAUDE_API_KEY)
else:
    st.error("⚠️ CLAUDE_API_KEY not found. Please add it to Streamlit secrets.")
    assistants = None

# Sidebar
with st.sidebar:
    st.title("🏠 RealtyXperience")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏠 Home", "💬 AI Assistants", "🔍 Property Search", "📊 Analytics"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.info("AI-powered real estate platform with expert consultants for property and land inquiries in Nigeria.")

# Main content based on selected page
if page == "🏠 Home":
    st.title("🏠 Welcome to RealtyXperience")
    st.markdown("### Your AI-Powered Real Estate Platform")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🤖 Meet Our AI Experts")
        st.markdown("""
        - **MR X**: Property expert with comprehensive knowledge
        - **Landlord**: Land acquisition and documentation specialist
        """)
    
    with col2:
        st.markdown("#### ✨ Features")
        st.markdown("""
        - Instant answers to property questions
        - Land documentation guidance
        - Market insights
        - Legal and regulatory information
        """)
    
    st.markdown("---")
    st.markdown("### 🚀 Get Started")
    st.markdown("Navigate to **AI Assistants** in the sidebar to chat with our experts!")

elif page == "💬 AI Assistants":
    st.title("💬 AI Assistants")
    
    if not assistants:
        st.error("AI Assistants are not available. Please configure CLAUDE_API_KEY.")
    else:
        assistant_choice = st.radio(
            "Choose your assistant:",
            ["🏢 MR X - Property Expert", "🌍 Landlord - Land Specialist"]
        )
        
        st.markdown("---")
        
        if assistant_choice == "🏢 MR X - Property Expert":
            st.markdown("### 🏢 MR X - Property Expert")
            st.markdown("Ask me anything about properties, buying, selling, regulations, and market insights!")
            
            # Display chat history
            for msg in st.session_state.mr_x_chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            # User input
            if user_input := st.chat_input("Ask MR X about properties..."):
                # Add user message
                st.session_state.mr_x_chat_history.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)
                
                # Get AI response
                with st.chat_message("assistant"):
                    with st.spinner("MR X is thinking..."):
                        response = assistants.mr_x_property_expert(user_input)
                        st.markdown(response)
                
                # Add assistant response
                st.session_state.mr_x_chat_history.append({"role": "assistant", "content": response})
        
        else:  # Landlord
            st.markdown("### 🌍 Landlord - Land Specialist")
            st.markdown("Get expert advice on land acquisition, C of O, documentation, and legal processes!")
            
            # Display chat history
            for msg in st.session_state.landlord_chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            # User input
            if user_input := st.chat_input("Ask Landlord about land matters..."):
                # Add user message
                st.session_state.landlord_chat_history.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)
                
                # Get AI response
                with st.chat_message("assistant"):
                    with st.spinner("Landlord is thinking..."):
                        response = assistants.landlord_assistant(user_input)
                        st.markdown(response)
                
                # Add assistant response
                st.session_state.landlord_chat_history.append({"role": "assistant", "content": response})

elif page == "🔍 Property Search":
    st.title("🔍 Property Search")
    st.info("Property search feature coming soon! Use AI Assistants to ask about specific properties.")

elif page == "📊 Analytics":
    st.title("📊 Market Analytics")
    st.info("Analytics dashboard coming soon! Ask MR X for current market insights.")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and Claude AI")
