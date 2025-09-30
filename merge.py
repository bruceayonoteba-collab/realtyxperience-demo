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

# Configuration using environment variables
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
    "market_data": {},
    "user_accounts": {},
    "current_user": None,
    "user_type": None,
    "portal_selection": None,
    "tenant_applications": [],
    "rent_payments": [],
    "property_inquiries": [],
    "land_inquiries": [],
    "ai_system": None
}

for key, default_value in session_state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

class CSVKnowledgeBase:
    """Connects to your CSV knowledge database"""
    
    def __init__(self):
        self.property_df = None
        self.land_df = None
        self.connect()
    
    def connect(self):
        """Load CSV files"""
        try:
            self.property_df = pd.read_csv('nigeria_property_knowledge.csv')
            self.land_df = pd.read_csv('nigeria_land_knowledge.csv')
            return True
        except Exception as e:
            st.error(f"CSV loading issue: {e}")
            return False
    
    def search_property_knowledge(self, query, max_results=3):
        """Search your property knowledge database"""
        if self.property_df is None or self.property_df.empty:
            return []
        
        try:
            query_lower = query.lower()
            knowledge = []
            
            for _, row in self.property_df.iterrows():
                question = str(row.get("QUESTION", "")).lower()
                answer = str(row.get("ANSWER", ""))
                category = str(row.get("CATEGORY", ""))
                tags = str(row.get("TAGS", "")).lower()
                
                if query_lower in question or query_lower in tags or query_lower in answer.lower():
                    knowledge.append({
                        "question": row.get("QUESTION", ""),
                        "answer": answer,
                        "category": category,
                        "tags": row.get("TAGS", "")
                    })
                
                if len(knowledge) >= max_results:
                    break
            
            return knowledge
        except Exception as e:
            st.error(f"Error searching property CSV: {e}")
            return []
    def search_land_knowledge(self, query, max_results=3):
        """Search your land knowledge database"""
        if self.land_df is None or self.land_df.empty:
            return []
        
        try:
            query_lower = query.lower()
            knowledge = []
            
            for _, row in self.land_df.iterrows():
                question = str(row.get("QUESTION", "")).lower()
                answer = str(row.get("ANSWER", ""))
                category = str(row.get("CATEGORY", ""))
                tags = str(row.get("TAGS", "")).lower()
                
                if query_lower in question or query_lower in tags or query_lower in answer.lower():
                    knowledge.append({
                        "question": row.get("QUESTION", ""),
                        "answer": answer,
                        "category": category,
                        "tags": row.get("TAGS", "")
                    })
                
                if len(knowledge) >= max_results:
                    break
            
            return knowledge
        except Exception as e:
            st.error(f"Error searching land CSV: {e}")
            return []
class RealtyXperienceAI:
    """Your AI Assistants powered by Snowflake knowledge and Claude"""
    
    def __init__(self):
        self.knowledge_base = CSVKnowledgeBase()
        try:
            self.claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
            self.claude_available = True
        except Exception as e:
            self.claude_available = False
            st.warning(f"Claude API issue: {e}")
    
    def mr_x_response(self, user_question, context=None):
        """MR X - Property Expert using your knowledge database"""
        
        # Get knowledge from YOUR Snowflake database
        knowledge = self.knowledge_base.search_property_knowledge(user_question, 3)
        
        if not knowledge:
            return self._fallback_property_response(user_question, context)
        
        # Use Claude AI with your knowledge
        if self.claude_available:
            try:
                # Build context from YOUR knowledge database
                knowledge_context = "Here's what I know from my knowledge database:\n\n"
                for item in knowledge:
                    knowledge_context += f"Q: {item['question']}\nA: {item['answer']}\n\n"
                
                # Add platform context if available
                platform_context = ""
                if context:
                    properties = context.get('properties', [])
                    if properties:
                        platform_context += f"\n\nCurrent platform has {len(properties)} properties available.\n"
                
                system_prompt = """You are Mr. X, a property investment expert assistant for RealtyXperience. Use the knowledge database information provided to give helpful, detailed answers about rental properties, ROI calculations, short-term rentals, and property investment strategies. Be specific and professional."""
                
                user_prompt = f"{knowledge_context}{platform_context}\n\nUser question: {user_question}\n\nPlease provide a comprehensive answer using the knowledge database information above."
                
                response = self.claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                
                return response.content[0].text
                
            except Exception as e:
                st.error(f"Claude AI error: {e}")
        
        # Fallback: Direct knowledge database response
        response = "**Mr. X:** Based on my knowledge database:\n\n"
        for item in knowledge:
            response += f"**{item['question']}**\n\n{item['answer']}\n\n---\n\n"
        
        return response
    
    def landlord_response(self, user_question, context=None):
        """Landlord - Land Expert using your knowledge database"""
        
        # Get knowledge from YOUR Snowflake database
        knowledge = self.knowledge_base.search_land_knowledge(user_question, 3)
        
        if not knowledge:
            return self._fallback_land_response(user_question, context)
        
        # Use Claude AI with your knowledge
        if self.claude_available:
            try:
                # Build context from YOUR knowledge database
                knowledge_context = "Here's what I know from my knowledge database:\n\n"
                for item in knowledge:
                    knowledge_context += f"Q: {item['question']}\nA: {item['answer']}\n\n"
                
                # Add platform context if available
                platform_context = ""
                if context:
                    land_plots = context.get('land_plots', [])
                    if land_plots:
                        platform_context += f"\n\nCurrent platform has {len(land_plots)} land plots available.\n"
                
                system_prompt = """You are Landlord, a land development expert assistant for RealtyXperience. Use the knowledge database information provided to give helpful, detailed answers about zoning, land development, permits, and land investment strategies. Be specific and professional."""
                
                user_prompt = f"{knowledge_context}{platform_context}\n\nUser question: {user_question}\n\nPlease provide a comprehensive answer using the knowledge database information above."
                
                response = self.claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                
                return response.content[0].text
                
            except Exception as e:
                st.error(f"Claude AI error: {e}")
        
        # Fallback: Direct knowledge database response
        response = "**Landlord:** Based on my knowledge database:\n\n"
        for item in knowledge:
            response += f"**{item['question']}**\n\n{item['answer']}\n\n---\n\n"
        
        return response
    
    def _fallback_property_response(self, user_question, context=None):
        """Fallback response when no knowledge is found"""
        message_lower = user_question.lower()
        
        if any(word in message_lower for word in ["invest", "investment", "roi", "return"]):
            return """Property Investment Intelligence & Predictions

I can provide comprehensive property investment analysis including:

• Price Predictions & Market timing recommendations
• ROI Analysis & Capital appreciation projections  
• Investment Scoring & Risk assessment
• Location Intelligence & Infrastructure impact analysis

Which property or area would you like me to analyze for investment potential?"""

        elif any(word in message_lower for word in ["find", "search", "recommend"]):
            return """Smart Property Discovery Engine

I can help you find the perfect property with:

• AI-Powered Property Matching based on lifestyle preferences
• Location Intelligence & Commute optimization
• Market Intelligence & Price trend analysis
• Smart Filters beyond basic search

Let me know your preferences (budget, location, lifestyle needs) and I'll find your perfect property match!"""

        return """Welcome to MR X - Your Property Intelligence System!

I'm your expert property advisor specializing in:

• Smart property matching & recommendations
• Investment analysis & market predictions  
• Neighborhood insights & safety analysis
• Portfolio optimization for property owners

Ask me anything about properties, investments, or market trends!"""
    
    def _fallback_land_response(self, user_question, context=None):
        """Fallback response when no knowledge is found"""
        message_lower = user_question.lower()
        
        if any(word in message_lower for word in ["invest", "investment", "development"]):
            return """Land Investment Intelligence & Development Analysis

I provide comprehensive land investment analysis including:

• Development potential assessments & ROI analysis
• Market timing recommendations & Growth corridor identification
• Feasibility studies & Zoning compliance guidance
• Infrastructure development impact analysis

Which land plot or area would you like me to analyze for investment potential?"""

        elif any(word in message_lower for word in ["find", "search", "recommend"]):
            return """Smart Land Discovery Engine

I can help you find perfect land opportunities with:

• AI matching based on investment goals
• Development Intelligence & Future growth analysis
• Strategic Filtering & Location intelligence
• Market entry optimization

Tell me your investment goals and I'll find your perfect land opportunity!"""

        return """Welcome to LANDLORD - Your Land Investment Intelligence System!

I'm your expert land investment advisor specializing in:

• Strategic land acquisition recommendations
• Development potential assessments
• Market timing & growth predictions
• Documentation & regulatory guidance

Ask me anything about land investment, development, or market opportunities!"""

class UserAuth:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def create_account(username, password, email, phone, user_type, full_name):
        if username in st.session_state.user_accounts:
            return False, "Username already exists"
        
        user_data = {
            "username": username,
            "password_hash": UserAuth.hash_password(password),
            "email": email,
            "phone": phone,
            "user_type": user_type,
            "full_name": full_name,
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "properties": [],
            "land_plots": [],
            "tenancy_history": [],
            "verification_status": "pending",
            "rating": 5.0,
            "profile_complete": False
        }
        
        st.session_state.user_accounts[username] = user_data
        return True, "Account created successfully"
    
    @staticmethod
    def login(username, password):
        if username not in st.session_state.user_accounts:
            return False, "User not found"
        
        user = st.session_state.user_accounts[username]
        if user["password_hash"] == UserAuth.hash_password(password):
            st.session_state.current_user = username
            st.session_state.user_type = user["user_type"]
            return True, "Login successful"
        return False, "Invalid password"
    
    @staticmethod
    def logout():
        st.session_state.current_user = None
        st.session_state.user_type = None
        st.session_state.portal_selection = None

def load_initial_properties():
    initial_properties = {
        "Lagos": [
            {
                "id": 1, "name": "Luxury 3BR Apartment", "location": "Ikoyi", "bedrooms": 3, "bathrooms": 3, 
                "area_sqm": 150, "rent_monthly": 2500000, "sale_price": 80000000, 
                "amenities": ["Pool", "Gym", "Security", "Generator"], 
                "description": "Modern luxury apartment with sea view", "year_built": 2020, 
                "owner_contact": "+234-123-456-789", "status": "active", "uploaded_date": "2024-01-15", 
                "demand_score": 8.5, "competition_score": 7.2, "seasonal_multiplier": 1.2, 
                "photos": 12, "description_quality": 9, "booking_rate": 0.85, "avg_rating": 4.7,
                "owner_id": "owner_1", "available_from": "2024-03-01"
            },
            {
                "id": 2, "name": "Cozy 2BR Flat", "location": "Yaba", "bedrooms": 2, "bathrooms": 2,
                "area_sqm": 85, "rent_monthly": 800000, "sale_price": 25000000, 
                "amenities": ["Security", "Parking"], "description": "Perfect for young professionals", 
                "year_built": 2018, "owner_contact": "+234-123-456-790", "status": "active", 
                "uploaded_date": "2024-02-10", "demand_score": 6.8, "competition_score": 8.1,
                "seasonal_multiplier": 1.0, "photos": 6, "description_quality": 7, 
                "booking_rate": 0.72, "avg_rating": 4.3, "owner_id": "owner_2", "available_from": "2024-03-15"
            },
            {
                "id": 3, "name": "Executive 4BR Duplex", "location": "Lekki Phase 1", "bedrooms": 4, 
                "bathrooms": 4, "area_sqm": 200, "rent_monthly": 3200000, "sale_price": 95000000, 
                "amenities": ["Pool", "BQ", "Security", "Generator", "Garden"], 
                "description": "Spacious family home in prime location", "year_built": 2019, 
                "owner_contact": "+234-123-456-791", "status": "active", "uploaded_date": "2024-01-20", 
                "demand_score": 9.1, "competition_score": 6.5, "seasonal_multiplier": 1.15, 
                "photos": 18, "description_quality": 8.5, "booking_rate": 0.91, "avg_rating": 4.8,
                "owner_id": "owner_3", "available_from": "2024-02-01"
            }
        ],
        "Abuja": [
            {
                "id": 4, "name": "Diplomatic 4BR Villa", "location": "Maitama", "bedrooms": 4, 
                "bathrooms": 4, "area_sqm": 250, "rent_monthly": 4500000, "sale_price": 120000000, 
                "amenities": ["Pool", "BQ", "Security", "Generator", "Garden"], 
                "description": "Premium location for diplomats and executives", "year_built": 2019, 
                "owner_contact": "+234-123-456-792", "status": "active", "uploaded_date": "2024-01-25", 
                "demand_score": 8.8, "competition_score": 5.9, "seasonal_multiplier": 1.3, 
                "photos": 20, "description_quality": 9.2, "booking_rate": 0.88, "avg_rating": 4.9,
                "owner_id": "owner_4", "available_from": "2024-03-01"
            },
            {
                "id": 5, "name": "Modern 3BR Apartment", "location": "Wuse II", "bedrooms": 3, 
                "bathrooms": 3, "area_sqm": 130, "rent_monthly": 1800000, "sale_price": 45000000, 
                "amenities": ["Gym", "Security", "Generator"], 
                "description": "Central business district location", "year_built": 2020, 
                "owner_contact": "+234-123-456-793", "status": "active", "uploaded_date": "2024-02-05", 
                "demand_score": 7.5, "competition_score": 7.8, "seasonal_multiplier": 1.1, 
                "photos": 10, "description_quality": 8, "booking_rate": 0.79, "avg_rating": 4.5,
                "owner_id": "owner_5", "available_from": "2024-02-20"
            }
        ]
    }
    return initial_properties

def load_initial_land():
    initial_land = {
        "Lagos": [
            {
                "id": 201, "name": "Prime Commercial Waterfront Land", "location": "Victoria Island", 
                "land_size_sqm": 5000, "price_total": 500000000, "price_per_sqm": 100000,
                "land_use": "Commercial", "title_document": "C of O", "survey_status": "Completed",
                "features": ["Waterfront", "C of O", "Survey Plan", "Corner Piece"], 
                "description": "Premium waterfront commercial land perfect for high-rise development", 
                "owner_contact": "+234-123-456-800", "status": "active", "uploaded_date": "2024-01-15", 
                "demand_score": 9.2, "competition_score": 6.8, "seasonal_multiplier": 1.3, 
                "photos": 15, "description_quality": 9.5, "inquiry_rate": 0.92, "avg_rating": 4.8,
                "owner_id": "land_owner_1", "available_from": "2024-03-01", "zoning": "Commercial",
                "access_road": "Tarred", "topography": "Flat", "utilities": ["Electricity", "Water", "Internet"]
            },
            {
                "id": 202, "name": "Residential Estate Land", "location": "Lekki Phase 2", 
                "land_size_sqm": 2500, "price_total": 75000000, "price_per_sqm": 30000,
                "land_use": "Residential", "title_document": "Deed of Assignment", "survey_status": "Completed",
                "features": ["Gated Estate", "Survey Plan", "Good Drainage"], 
                "description": "Perfect for luxury residential development in growing Lekki area", 
                "owner_contact": "+234-123-456-801", "status": "active", "uploaded_date": "2024-02-10", 
                "demand_score": 7.8, "competition_score": 7.5, "seasonal_multiplier": 1.1, 
                "photos": 8, "description_quality": 8.2, "inquiry_rate": 0.76, "avg_rating": 4.5,
                "owner_id": "land_owner_2", "available_from": "2024-03-15", "zoning": "Residential",
                "access_road": "Tarred", "topography": "Flat", "utilities": ["Electricity", "Water"]
            },
            {
                "id": 203, "name": "Industrial Development Land", "location": "Ikorodu", 
                "land_size_sqm": 10000, "price_total": 180000000, "price_per_sqm": 18000,
                "land_use": "Industrial", "title_document": "C of O", "survey_status": "Completed",
                "features": ["Large Area", "C of O", "Industrial Zone", "Highway Access"], 
                "description": "Excellent for manufacturing and logistics operations", 
                "owner_contact": "+234-123-456-802", "status": "active", "uploaded_date": "2024-01-20", 
                "demand_score": 8.3, "competition_score": 6.2, "seasonal_multiplier": 1.0, 
                "photos": 12, "description_quality": 8.8, "inquiry_rate": 0.83, "avg_rating": 4.6,
                "owner_id": "land_owner_3", "available_from": "2024-02-01", "zoning": "Industrial",
                "access_road": "Highway", "topography": "Flat", "utilities": ["Electricity", "Water", "Gas"]
            }
        ],
        "Abuja": [
            {
                "id": 204, "name": "Diplomatic Zone Premium Land", "location": "Maitama Extension", 
                "land_size_sqm": 3000, "price_total": 900000000, "price_per_sqm": 300000,
                "land_use": "Residential", "title_document": "C of O", "survey_status": "Completed",
                "features": ["Diplomatic Zone", "C of O", "Corner Piece", "Tarred Road"], 
                "description": "Ultra-premium diplomatic zone land for luxury development", 
                "owner_contact": "+234-123-456-803", "status": "active", "uploaded_date": "2024-01-25", 
                "demand_score": 9.5, "competition_score": 5.8, "seasonal_multiplier": 1.4, 
                "photos": 18, "description_quality": 9.8, "inquiry_rate": 0.95, "avg_rating": 4.9,
                "owner_id": "land_owner_4", "available_from": "2024-03-01", "zoning": "Residential",
                "access_road": "Tarred", "topography": "Flat", "utilities": ["Electricity", "Water", "Internet", "Gas"]
            },
            {
                "id": 205, "name": "Commercial Business District Land", "location": "Central Business District", 
                "land_size_sqm": 4000, "price_total": 600000000, "price_per_sqm": 150000,
                "land_use": "Commercial", "title_document": "C of O", "survey_status": "Completed",
                "features": ["CBD Location", "C of O", "High Traffic", "Metro Access"], 
                "description": "Prime commercial land in the heart of Abuja's business district", 
                "owner_contact": "+234-123-456-804", "status": "active", "uploaded_date": "2024-02-05", 
                "demand_score": 8.9, "competition_score": 6.5, "seasonal_multiplier": 1.2, 
                "photos": 14, "description_quality": 9.1, "inquiry_rate": 0.87, "avg_rating": 4.7,
                "owner_id": "land_owner_5", "available_from": "2024-02-20", "zoning": "Commercial",
                "access_road": "Tarred", "topography": "Flat", "utilities": ["Electricity", "Water", "Internet"]
            }
        ]
    }
    return initial_land

# Initialize AI System
if not st.session_state.ai_system:
    st.session_state.ai_system = RealtyXperienceAI()

# Initialize databases
if not st.session_state.property_database:
    st.session_state.property_database = load_initial_properties()

if not st.session_state.land_database:
    st.session_state.land_database = load_initial_land()

def get_all_properties():
    all_properties = []
    for city, properties in st.session_state.property_database.items():
        for prop in properties:
            if prop.get("status") == "active":
                prop_copy = prop.copy()
                prop_copy["city"] = city
                all_properties.append(prop_copy)
    return all_properties

def get_all_land():
    all_land = []
    for city, land_plots in st.session_state.land_database.items():
        for land in land_plots:
            if land.get("status") == "active":
                land_copy = land.copy()
                land_copy["city"] = city
                all_land.append(land_copy)
    return all_land

def show_login_signup():
    st.title("Welcome to RealtyXperience")
    st.markdown("*Your AI-Powered Real Estate Platform*")
    
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    
    with tab1:
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", type="primary"):
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                success, message = UserAuth.login(username, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    with tab2:
        st.subheader("Create New Account")
        new_username = st.text_input("Choose Username")
        new_password = st.text_input("Password", type="password", key="new_pass")
        confirm_password = st.text_input("Confirm Password", type="password")
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        user_type = st.selectbox("I am a:", ["tenant", "host", "agent", "investor", "land_developer"])
        
        agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        if st.button("Create Account", type="primary"):
            if not all([new_username, new_password, full_name, email, phone]):
                st.error("Please fill in all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif not agree_terms:
                st.error("Please agree to the terms")
            else:
                success, message = UserAuth.create_account(
                    new_username, new_password, email, phone, user_type, full_name
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)

def show_portal_selection():
    st.title("Welcome to RealtyXperience")
    st.markdown("### Your Complete AI-Powered Real Estate Platform")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        st.subheader("Choose Your Portal")
        
        # Properties Portal Button
        if st.button("🏠 Properties Portal", key="properties_portal", use_container_width=True):
            st.session_state.portal_selection = "properties"
            st.rerun()
        
        st.markdown("**Properties Portal Features:**")
        st.write("• Residential & Commercial Properties")
        st.write("• MR X AI Assistant for Real Estate")
        st.write("• Smart Property Search & Matching")
        st.write("• Rent & Sale Management")
        
        st.markdown("---")
        
        # Land Portal Button
        if st.button("🌍 Land Portal", key="land_portal", use_container_width=True):
            st.session_state.portal_selection = "land"
            st.rerun()
            
        st.markdown("**Land Portal Features:**")
        st.write("• Commercial, Residential & Industrial Land")
        st.write("• LANDLORD AI Assistant for Land Investment")
        st.write("• Smart Land Discovery & Matching")
        st.write("• Development Planning & Documentation")

def show_mr_x_chat():
    st.header("MR X - AI Property Assistant")
    st.markdown("*Your intelligent guide powered by Snowflake knowledge database*")
    
    # Database connection status
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔧 Test Database Connection"):
            with st.spinner("Testing connection..."):
                if st.session_state.ai_system.knowledge_base.connect():
                    st.success("✅ Database Connected!")
                else:
                    st.error("❌ Database Connection Failed")
    
    with col2:
        user_type = st.selectbox("I am a:", ["Guest/Buyer", "Property Host/Owner", "Real Estate Agent", "Property Investor", "Tenant"])
    with col3:
        if st.button("Clear Chat History"):
            st.session_state.mr_x_chat_history = []
            st.rerun()
    
    chat_container = st.container()
    with chat_container:
        if not st.session_state.mr_x_chat_history:
            welcome_msg = st.session_state.ai_system.mr_x_response("", {"user_type": user_type.lower().split('/')[0]})
            st.info(f"**MR X:** {welcome_msg}")
        
        for user_msg, bot_response in st.session_state.mr_x_chat_history:
            st.success(f"**You:** {user_msg}")
            st.info(f"**MR X:** {bot_response}")
    
    st.markdown("---")
    user_input = st.text_input("Ask MR X anything about properties...", 
                              placeholder="e.g., 'Find me investment properties in Lekki' or 'What's the best area for families in Abuja?'",
                              key="mr_x_input")
    
    if st.button("Send Message", type="primary", key="send_mr_x") and user_input:
        context = {
            "properties": get_all_properties(),
            "user_type": user_type,
            "current_user": st.session_state.current_user
        }
        
        response = st.session_state.ai_system.mr_x_response(user_input, context)
        
        st.session_state.mr_x_chat_history.append((user_input, response))
        st.rerun()
    
    st.markdown("### Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    quick_actions = {
        "Investment Analysis": "Analyze property investment potential in my budget",
        "Neighborhood Guide": "Tell me about the best neighborhoods for my lifestyle",
        "Market Trends": "What are current property market trends in Lagos and Abuja?",
        "Price Predictions": "Predict property price movements in key areas"
    }
    
    for i, (action, prompt) in enumerate(quick_actions.items()):
        col = [col1, col2, col3, col4][i]
        with col:
            if st.button(action, key=f"property_action_{i}"):
                context = {"properties": get_all_properties(), "user_type": user_type}
                response = st.session_state.ai_system.mr_x_response(prompt, context)
                st.session_state.mr_x_chat_history.append((action, response))
                st.rerun()

def show_landlord_chat():
    st.header("LANDLORD - AI Land Investment Assistant")
    st.markdown("*Your strategic advisor powered by Snowflake knowledge database*")
    
    # Database connection status
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔧 Test Database Connection", key="landlord_db_test"):
            with st.spinner("Testing connection..."):
                if st.session_state.ai_system.knowledge_base.connect():
                    st.success("✅ Database Connected!")
                else:
                    st.error("❌ Database Connection Failed")
    
    with col2:
        user_type = st.selectbox("I am a:", ["Guest/Investor", "Land Developer", "Real Estate Agent", "Land Owner", "Investment Firm"], key="landlord_user_type")
    with col3:
        if st.button("Clear Chat History", key="clear_landlord"):
            st.session_state.landlord_chat_history = []
            st.rerun()
    
    chat_container = st.container()
    with chat_container:
        if not st.session_state.landlord_chat_history:
            welcome_msg = st.session_state.ai_system.landlord_response("", {"user_type": user_type.lower().split('/')[0]})
            st.info(f"**LANDLORD:** {welcome_msg}")
        
        for user_msg, bot_response in st.session_state.landlord_chat_history:
            st.success(f"**You:** {user_msg}")
            st.info(f"**LANDLORD:** {bot_response}")
    
    st.markdown("---")
    user_input = st.text_input("Ask LANDLORD anything about land investment...", 
                              placeholder="e.g., 'Find commercial land in Lagos' or 'Analyze development potential in Maitama'",
                              key="landlord_input")
    
    if st.button("Send Message", type="primary", key="send_landlord") and user_input:
        context = {
            "land_plots": get_all_land(),
            "user_type": user_type,
            "current_user": st.session_state.current_user
        }
        
        response = st.session_state.ai_system.landlord_response(user_input, context)
        
        st.session_state.landlord_chat_history.append((user_input, response))
        st.rerun()
    
    st.markdown("### Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    quick_actions = {
        "Investment Analysis": "Analyze land investment opportunities in my budget range",
        "Documentation Guide": "Guide me through land documentation requirements",
        "Market Intelligence": "What are current land market trends and timing?",
        "Development Planning": "Help me plan development strategy for my land"
    }
    
    for i, (action, prompt) in enumerate(quick_actions.items()):
        col = [col1, col2, col3, col4][i]
        with col:
            if st.button(action, key=f"land_action_{i}"):
                context = {"land_plots": get_all_land(), "user_type": user_type}
                response = st.session_state.ai_system.landlord_response(prompt, context)
                st.session_state.landlord_chat_history.append((action, response))
                st.rerun()

def show_property_search():
    st.title("Find Your Perfect Property")
    st.markdown("*AI-powered property discovery with intelligent matching*")
    
    all_props = get_all_properties()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Available Properties", len(all_props))
    with col2:
        avg_rent = np.mean([p.get('rent_monthly', 0) for p in all_props if p.get('rent_monthly')])
        st.metric("Avg Rent", f"₦{avg_rent:,.0f}")
    with col3:
        high_demand = len([p for p in all_props if p.get('demand_score', 0) > 8])
        st.metric("High Demand", f"{high_demand} properties")
    with col4:
        recent_count = len([p for p in all_props if p.get("uploaded_date", "") >= "2024-02-01"])
        st.metric("New Listings", recent_count)
    
    search_mode = st.radio("Search Mode:", ["Quick Filter Search", "Chat with MR X"])
    
    if search_mode == "Quick Filter Search":
        with st.expander("Search Filters", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                filter_city = st.selectbox("City", ["All", "Lagos", "Abuja"])
                filter_type = st.selectbox("Type", ["All", "Rent", "Sale", "Both"])
            with col2:
                filter_beds = st.selectbox("Bedrooms", ["All", "1", "2", "3", "4", "5+"])
                max_budget = st.number_input("Max Budget (₦)", min_value=0, value=0, help="0 = no limit")
            with col3:
                min_area = st.number_input("Min Area (sqm)", min_value=0, value=0)
                location_filter = st.selectbox("Location", ["All", "Ikoyi", "Lekki Phase 1", "Yaba", "Maitama", "Wuse II"])
            with col4:
                required_amenities = st.multiselect("Must Have", ["Security", "Generator", "Pool", "Gym", "Parking", "Garden"])
        
        if st.button("Search Properties", type="primary"):
            filtered = all_props.copy()
            
            if filter_city != "All":
                filtered = [p for p in filtered if p.get("city") == filter_city]
            
            if location_filter != "All":
                filtered = [p for p in filtered if p.get("location") == location_filter]
            
            if filter_type == "Rent":
                filtered = [p for p in filtered if p.get("rent_monthly")]
            elif filter_type == "Sale":
                filtered = [p for p in filtered if p.get("sale_price")]
            
            if filter_beds != "All":
                target_beds = 5 if filter_beds == "5+" else int(filter_beds)
                if filter_beds == "5+":
                    filtered = [p for p in filtered if p["bedrooms"] >= target_beds]
                else:
                    filtered = [p for p in filtered if p["bedrooms"] == target_beds]
            
            if max_budget > 0:
                filtered = [p for p in filtered if 
                          (p.get("rent_monthly") and p["rent_monthly"] <= max_budget) or
                          (p.get("sale_price") and p["sale_price"] <= max_budget)]
            
            if min_area > 0:
                filtered = [p for p in filtered if p.get("area_sqm", 0) >= min_area]
            
            if required_amenities:
                filtered = [p for p in filtered if all(amenity in p.get("amenities", []) for amenity in required_amenities)]
            
            display_property_results(filtered)
    else:
        show_mr_x_chat()

def show_land_search():
    st.title("Discover Prime Land Opportunities")
    st.markdown("*AI-powered land discovery with intelligent investment matching*")
    
    all_land = get_all_land()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Available Land Plots", len(all_land))
    with col2:
        avg_price = np.mean([l.get('price_per_sqm', 0) for l in all_land if l.get('price_per_sqm')])
        st.metric("Avg Price/sqm", f"₦{avg_price:,.0f}")
    with col3:
        high_demand = len([l for l in all_land if l.get('demand_score', 0) > 8])
        st.metric("High Demand", f"{high_demand} plots")
    with col4:
        recent_count = len([l for l in all_land if l.get("uploaded_date", "") >= "2024-02-01"])
        st.metric("New Listings", recent_count)
    
    search_mode = st.radio("Search Mode:", ["Quick Filter Search", "Chat with LANDLORD"])
    
    if search_mode == "Quick Filter Search":
        with st.expander("Search Filters", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                filter_city = st.selectbox("City", ["All", "Lagos", "Abuja"], key="land_city")
                land_use_filter = st.selectbox("Land Use", ["All", "Residential", "Commercial", "Industrial"])
            with col2:
                min_size = st.number_input("Min Size (sqm)", min_value=0, value=0)
                max_budget = st.number_input("Max Budget (₦)", min_value=0, value=0, key="land_budget")
            with col3:
                location_filter = st.selectbox("Location", ["All", "Victoria Island", "Lekki Phase 1", "Maitama", "Ikorodu"], key="land_location")
                title_filter = st.selectbox("Title Document", ["All", "C of O", "Deed of Assignment"])
            with col4:
                required_features = st.multiselect("Must Have", ["C of O", "Survey Plan", "Corner Piece", "Waterfront", "Highway Access"])
        
        if st.button("Search Land Plots", type="primary"):
            filtered = all_land.copy()
            
            if filter_city != "All":
                filtered = [l for l in filtered if l.get("city") == filter_city]
            
            if location_filter != "All":
                filtered = [l for l in filtered if l.get("location") == location_filter]
            
            if land_use_filter != "All":
                filtered = [l for l in filtered if l.get("land_use") == land_use_filter]
            
            if title_filter != "All":
                filtered = [l for l in filtered if l.get("title_document") == title_filter]
            
            if max_budget > 0:
                filtered = [l for l in filtered if l.get("price_total", 0) <= max_budget]
            
            if min_size > 0:
                filtered = [l for l in filtered if l.get("land_size_sqm", 0) >= min_size]
            
            if required_features:
                filtered = [l for l in filtered if all(feature in l.get("features", []) for feature in required_features)]
            
            display_land_results(filtered)
    else:
        show_landlord_chat()

def display_property_results(properties):
    if not properties:
        st.info("No properties found matching your criteria.")
        return
    
    st.subheader(f"Found {len(properties)} Properties")
    
    for i, prop in enumerate(properties, 1):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                demand_score = prop.get('demand_score', 7.0)
                rating = prop.get('avg_rating', 4.0)
                
                if demand_score > 8.5 and rating > 4.5:
                    value_indicator = "Hot Property"
                    indicator_color = "success"
                elif demand_score > 7.5:
                    value_indicator = "High Demand"
                    indicator_color = "success"
                elif demand_score < 6.0:
                    value_indicator = "Value Opportunity"
                    indicator_color = "warning"
                else:
                    value_indicator = "Good Option"
                    indicator_color = "info"
                
                getattr(st, indicator_color)(f"**{i}. {prop['name']}** - {value_indicator}")
                
                st.markdown(f"""
                **Location:** {prop['location']}, {prop.get('city', '')}
                
                **Details:** {prop['bedrooms']} bed • {prop['bathrooms']} bath • {prop['area_sqm']} sqm • Built {prop.get('year_built', 'N/A')}
                
                **Price:** {'Rent: ₦' + f"{prop['rent_monthly']:,}/month" if prop.get('rent_monthly') else ''} {'Sale: ₦' + f"{prop['sale_price']:,}" if prop.get('sale_price') else ''}
                
                **Quality:** Rating: {prop.get('avg_rating', 4.0)}/5 • Demand Score: {prop.get('demand_score', 7.0)}/10
                
                **Amenities:** {', '.join(prop.get('amenities', []))}
                
                **Description:** {prop['description'][:150]}...
                """)
            
            with col2:
                st.markdown(f"**Property ID:** NF-{prop['id']:04d}")
                st.markdown(f"**Available:** {prop.get('available_from', 'Now')}")
                st.markdown(f"**Contact:** {prop['owner_contact']}")
                
                if st.button(f"Contact Owner", key=f"contact_property_{prop['id']}"):
                    st.success("Contact initiated!")
                
                if st.button(f"Save to Favorites", key=f"save_property_{prop['id']}"):
                    st.success("Saved to favorites!")
            
            st.markdown("---")

def display_land_results(land_plots):
    if not land_plots:
        st.info("No land plots found matching your criteria.")
        return
    
    st.subheader(f"Found {len(land_plots)} Land Opportunities")
    
    for i, land in enumerate(land_plots, 1):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                demand_score = land.get('demand_score', 7.0)
                rating = land.get('avg_rating', 4.0)
                
                if demand_score > 8.5 and rating > 4.5:
                    value_indicator = "Premium Investment"
                    indicator_color = "success"
                elif demand_score > 7.5:
                    value_indicator = "High Demand"
                    indicator_color = "success"
                elif demand_score < 6.0:
                    value_indicator = "Value Opportunity"
                    indicator_color = "warning"
                else:
                    value_indicator = "Good Investment"
                    indicator_color = "info"
                
                getattr(st, indicator_color)(f"**{i}. {land['name']}** - {value_indicator}")
                
                st.markdown(f"""
                **Location:** {land['location']}, {land.get('city', '')}
                
                **Details:** {land['land_size_sqm']:,} sqm • {land['land_use']} • {land.get('zoning', 'N/A')} Zone
                
                **Price:** ₦{land['price_total']:,} (₦{land.get('price_per_sqm', 0):,}/sqm)
                
                **Documentation:** {land.get('title_document', 'N/A')} • Survey: {land.get('survey_status', 'N/A')}
                
                **Infrastructure:** Road: {land.get('access_road', 'N/A')} • Utilities: {', '.join(land.get('utilities', []))}
                
                **Key Features:** {', '.join(land.get('features', []))}
                
                **Description:** {land['description'][:150]}...
                """)
            
            with col2:
                st.markdown(f"**Land ID:** NL-{land['id']:04d}")
                st.markdown(f"**Available:** {land.get('available_from', 'Now')}")
                st.markdown(f"**Contact:** {land['owner_contact']}")
                
                if st.button(f"Contact Owner", key=f"contact_land_{land['id']}"):
                    st.success("Contact initiated!")
                
                if st.button(f"Save to Watchlist", key=f"save_land_{land['id']}"):
                    st.success("Added to watchlist!")
            
            st.markdown("---")

def save_property_to_database(property_data):
    city = property_data["city"]
    if city not in st.session_state.property_database:
        st.session_state.property_database[city] = []
    
    property_data["id"] = st.session_state.next_property_id
    property_data["uploaded_date"] = datetime.now().strftime("%Y-%m-%d")
    property_data["status"] = "active"
    property_data["owner_id"] = st.session_state.current_user
    
    property_data["demand_score"] = round(random.uniform(6.0, 9.5), 1)
    property_data["competition_score"] = round(random.uniform(5.0, 9.0), 1)
    property_data["seasonal_multiplier"] = round(random.uniform(0.9, 1.3), 2)
    property_data["booking_rate"] = round(random.uniform(0.6, 0.95), 2)
    property_data["avg_rating"] = round(random.uniform(3.8, 4.9), 1)
    property_data["photos"] = random.randint(3, 20)
    property_data["description_quality"] = round(random.uniform(6.0, 9.5), 1)
    
    st.session_state.property_database[city].append(property_data)
    st.session_state.next_property_id += 1
    
    return property_data["id"]

def save_land_to_database(land_data):
    city = land_data["city"]
    if city not in st.session_state.land_database:
        st.session_state.land_database[city] = []
    
    land_data["id"] = st.session_state.next_land_id
    land_data["uploaded_date"] = datetime.now().strftime("%Y-%m-%d")
    land_data["status"] = "active"
    land_data["owner_id"] = st.session_state.current_user
    
    land_data["demand_score"] = round(random.uniform(6.0, 9.5), 1)
    land_data["competition_score"] = round(random.uniform(5.0, 9.0), 1)
    land_data["seasonal_multiplier"] = round(random.uniform(0.9, 1.4), 2)
    land_data["inquiry_rate"] = round(random.uniform(0.6, 0.95), 2)
    land_data["avg_rating"] = round(random.uniform(3.8, 4.9), 1)
    land_data["photos"] = random.randint(3, 20)
    land_data["description_quality"] = round(random.uniform(6.0, 9.5), 1)
    
    st.session_state.land_database[city].append(land_data)
    st.session_state.next_land_id += 1
    
    return land_data["id"]

def show_property_upload_form():
    st.header("List Your Property with AI Optimization")
    st.markdown("*Get AI-powered insights and optimization recommendations*")
    
    if not st.session_state.current_user:
        st.warning("Please log in to list properties")
        return
    
    with st.form("enhanced_property_upload"):
        st.subheader("Property Information")
        col1, col2 = st.columns(2)
        
        with col1:
            property_name = st.text_input("Property Title*", placeholder="e.g., Luxury 3BR Waterfront Apartment")
            city = st.selectbox("City*", ["Lagos", "Abuja"])
            location = st.text_input("Specific Location*", placeholder="e.g., Ikoyi, Lekki Phase 1")
            bedrooms = st.number_input("Bedrooms*", min_value=1, max_value=10, value=3)
            bathrooms = st.number_input("Bathrooms*", min_value=1, max_value=10, value=2)
        
        with col2:
            area_sqm = st.number_input("Area (Square Meters)*", min_value=20.0, value=120.0)
            year_built = st.number_input("Year Built*", min_value=1950, max_value=2024, value=2020)
            property_type = st.selectbox("Property Type*", ["Apartment", "Duplex", "Bungalow", "Mansion", "Penthouse"])
            furnished = st.selectbox("Furnishing", ["Unfurnished", "Semi-Furnished", "Fully Furnished"])
        
        st.subheader("Pricing")
        col1, col2 = st.columns(2)
        
        with col1:
            rent_monthly = st.number_input("Monthly Rent (₦)", min_value=0, value=0, help="Leave as 0 if not for rent")
        
        with col2:
            sale_price = st.number_input("Sale Price (₦)", min_value=0, value=0, help="Leave as 0 if not for sale")
        
        st.subheader("Amenities & Features")
        amenity_options = [
            "Security Guard", "CCTV", "Gated Community", "Intercom",
            "Generator", "Solar Power", "Inverter", "Backup Water",
            "Swimming Pool", "Gym", "Garden", "Playground", "Tennis Court",
            "Parking", "Elevator", "Balcony", "Store Room", "Boys Quarter"
        ]
        
        selected_amenities = st.multiselect("Select available amenities", amenity_options)
        
        st.subheader("Property Description")
        description = st.text_area("Property Description*", placeholder="Describe your property's unique features...", height=100)
        
        st.subheader("Contact Information")
        col1, col2 = st.columns(2)
        
        with col1:
            owner_contact = st.text_input("Phone Number*", placeholder="+234-XXX-XXX-XXXX")
            owner_email = st.text_input("Email Address", placeholder="your.email@example.com")
        
        with col2:
            whatsapp_number = st.text_input("WhatsApp Number", placeholder="For quick communication")
            preferred_contact = st.selectbox("Preferred Contact Method", ["Phone Call", "WhatsApp", "Email", "Any"])
        
        st.subheader("Legal & Compliance")
        property_documents = st.checkbox("I confirm all property documents are valid and up-to-date")
        marketing_consent = st.checkbox("I consent to marketing this property on RealtyXperience platform")
        terms_agreement = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        submitted = st.form_submit_button("List Property", type="primary")
        
        if submitted:
            required_fields = [property_name, city, location, bedrooms, bathrooms, owner_contact, description]
            if not all(required_fields):
                st.error("Please fill in all required fields marked with *")
            elif rent_monthly == 0 and sale_price == 0:
                st.error("Please specify either rental price or sale price (or both)")
            elif not all([property_documents, marketing_consent, terms_agreement]):
                st.error("Please agree to all required terms and conditions")
            else:
                property_data = {
                    "name": property_name,
                    "city": city,
                    "location": location,
                    "bedrooms": int(bedrooms),
                    "bathrooms": int(bathrooms),
                    "area_sqm": float(area_sqm),
                    "year_built": int(year_built),
                    "property_type": property_type,
                    "furnished": furnished,
                    "rent_monthly": int(rent_monthly) if rent_monthly > 0 else None,
                    "sale_price": int(sale_price) if sale_price > 0 else None,
                    "amenities": selected_amenities,
                    "description": description,
                    "owner_contact": owner_contact,
                    "owner_email": owner_email if owner_email else None,
                    "whatsapp_number": whatsapp_number if whatsapp_number else None,
                    "preferred_contact": preferred_contact,
                    "available_from": datetime.now().strftime("%Y-%m-%d")
                }
                
                property_id = save_property_to_database(property_data)
                
                st.success(f"""Property Successfully Listed!
                
**Property ID:** NF-{property_id:04d}
**Status:** Active and searchable
**Listed in:** {city} - {location}""")

def show_land_upload_form():
    st.header("List Your Land with AI Optimization")
    st.markdown("*Get AI-powered insights and investment optimization recommendations*")
    
    if not st.session_state.current_user:
        st.warning("Please log in to list land")
        return
    
    with st.form("enhanced_land_upload"):
        st.subheader("Land Information")
        col1, col2 = st.columns(2)
        
        with col1:
            land_name = st.text_input("Land Title*", placeholder="e.g., Prime Commercial Waterfront Land")
            city = st.selectbox("City*", ["Lagos", "Abuja"], key="land_upload_city")
            location = st.text_input("Specific Location*", placeholder="e.g., Victoria Island, Maitama")
            land_size_sqm = st.number_input("Land Size (Square Meters)*", min_value=100.0, value=2000.0)
            land_use = st.selectbox("Intended Use*", ["Residential", "Commercial", "Industrial", "Mixed Use"])
        
        with col2:
            zoning = st.selectbox("Zoning Classification", ["Residential", "Commercial", "Industrial", "Mixed", "Agricultural"])
            topography = st.selectbox("Topography", ["Flat", "Sloped", "Hilly", "Waterfront", "Mixed"])
            access_road = st.selectbox("Road Access", ["Tarred", "Gravel", "Highway", "Expressway", "Untarred"])
            drainage = st.selectbox("Drainage", ["Excellent", "Good", "Fair", "Poor", "Requires Work"])
        
        st.subheader("Pricing")
        col1, col2 = st.columns(2)
        
        with col1:
            price_total = st.number_input("Total Price (₦)*", min_value=1000000, value=50000000)
        
        with col2:
            price_per_sqm = st.number_input("Price per SqM (₦)", min_value=0, value=int(price_total/land_size_sqm) if land_size_sqm > 0 else 0, 
                                          help="Auto-calculated, but you can adjust")
        
        st.subheader("Documentation & Legal")
        col1, col2 = st.columns(2)
        
        with col1:
            title_document = st.selectbox("Title Document*", ["Certificate of Occupancy (C of O)", "Deed of Assignment", "Customary Right", "Survey Plan Only"])
            survey_status = st.selectbox("Survey Status*", ["Completed", "In Progress", "Required", "Not Available"])
        
        with col2:
            government_consent = st.selectbox("Government Consent", ["Available", "In Process", "Required", "Not Required"])
            excision_status = st.selectbox("Excision Status", ["Excised", "Gazette", "Not Excised", "In Process"])
        
        st.subheader("Infrastructure & Utilities")
        utility_options = ["Electricity", "Water", "Gas", "Internet", "Sewage", "Phone Lines"]
        available_utilities = st.multiselect("Available Utilities", utility_options)
        
        st.subheader("Key Features")
        feature_options = [
            "Corner Piece", "Waterfront", "Highway Access", "Gated Estate",
            "Survey Plan", "Fence", "Good Drainage", "High Traffic Area",
            "Government Allocation", "Free from Encumbrance", "Strategic Location"
        ]
        
        selected_features = st.multiselect("Select key features", feature_options)
        
        st.subheader("Land Description")
        description = st.text_area("Land Description*", placeholder="Describe your land's unique investment potential...", height=100)
        
        st.subheader("Contact Information")
        col1, col2 = st.columns(2)
        
        with col1:
            owner_contact = st.text_input("Phone Number*", placeholder="+234-XXX-XXX-XXXX", key="land_contact")
            owner_email = st.text_input("Email Address", placeholder="your.email@example.com", key="land_email")
        
        with col2:
            whatsapp_number = st.text_input("WhatsApp Number", placeholder="For quick communication", key="land_whatsapp")
            preferred_contact = st.selectbox("Preferred Contact Method", ["Phone Call", "WhatsApp", "Email", "Any"], key="land_contact_pref")
        
        st.subheader("Legal & Compliance")
        land_documents = st.checkbox("I confirm all land documents are valid and up-to-date")
        marketing_consent = st.checkbox("I consent to marketing this land on RealtyXperience platform", key="land_marketing")
        terms_agreement = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="land_terms")
        
        submitted = st.form_submit_button("List Land", type="primary")
        
        if submitted:
            required_fields = [land_name, city, location, land_size_sqm, price_total, owner_contact, description]
            if not all(required_fields):
                st.error("Please fill in all required fields marked with *")
            elif not all([land_documents, marketing_consent, terms_agreement]):
                st.error("Please agree to all required terms and conditions")
            else:
                land_data = {
                    "name": land_name,
                    "city": city,
                    "location": location,
                    "land_size_sqm": float(land_size_sqm),
                    "land_use": land_use,
                    "zoning": zoning,
                    "topography": topography,
                    "access_road": access_road,
                    "drainage": drainage,
                    "price_total": int(price_total),
                    "price_per_sqm": int(price_per_sqm),
                    "title_document": title_document,
                    "survey_status": survey_status,
                    "government_consent": government_consent,
                    "excision_status": excision_status,
                    "utilities": available_utilities,
                    "features": selected_features,
                    "description": description,
                    "owner_contact": owner_contact,
                    "owner_email": owner_email if owner_email else None,
                    "whatsapp_number": whatsapp_number if whatsapp_number else None,
                    "preferred_contact": preferred_contact,
                    "available_from": datetime.now().strftime("%Y-%m-%d")
                }
                
                land_id = save_land_to_database(land_data)
                
                st.success(f"""Land Successfully Listed!
                
**Land ID:** NL-{land_id:04d}
**Status:** Active and searchable
**Listed in:** {city} - {location}
**Investment Potential:** High demand area identified""")

def show_dashboard():
    if not st.session_state.current_user:
        st.warning("Please log in to access your dashboard")
        return
    
    user_type = st.session_state.user_type
    user_data = st.session_state.user_accounts.get(st.session_state.current_user, {})
    portal = st.session_state.portal_selection
    
    st.title(f"Welcome back, {user_data.get('full_name', st.session_state.current_user)}!")
    st.markdown(f"*{portal.title()} Portal - {user_type.title()} Dashboard*")
    
    if portal == "properties":
        if user_type == "host":
            show_property_host_dashboard()
        elif user_type == "tenant":
            show_property_tenant_dashboard()
        elif user_type == "agent":
            show_property_agent_dashboard()
        elif user_type == "investor":
            show_property_investor_dashboard()
        else:
            show_general_property_dashboard()
    elif portal == "land":
        if user_type == "land_developer":
            show_land_developer_dashboard()
        elif user_type == "investor":
            show_land_investor_dashboard()
        else:
            show_general_land_dashboard()

def show_property_host_dashboard():
    st.subheader("Property Portfolio Management")
    
    user_properties = []
    for city, properties in st.session_state.property_database.items():
        for prop in properties:
            if prop.get('owner_id') == st.session_state.current_user:
                prop_copy = prop.copy()
                prop_copy['city'] = city
                user_properties.append(prop_copy)
    
    if user_properties:
        col1, col2, col3, col4 = st.columns(4)
        
        total_properties = len(user_properties)
        total_value = sum(p.get('sale_price', 0) for p in user_properties)
        monthly_income = sum(p.get('rent_monthly', 0) for p in user_properties)
        avg_rating = np.mean([p.get('avg_rating', 4.0) for p in user_properties])
        
        with col1:
            st.metric("Total Properties", total_properties)
        with col2:
            st.metric("Portfolio Value", f"₦{total_value/1000000:.1f}M")
        with col3:
            st.metric("Monthly Income", f"₦{monthly_income/1000000:.1f}M")
        with col4:
            st.metric("Avg Rating", f"{avg_rating:.1f}/5")
        
        st.subheader("Your Properties")
        for prop in user_properties:
            with st.expander(f"{prop['name']} - {prop['location']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    **Property Details:**
                    • {prop['bedrooms']} bed, {prop['bathrooms']} bath, {prop['area_sqm']} sqm
                    • Built: {prop.get('year_built')} | Type: {prop.get('property_type', 'apartment').title()}
                    • Status: {prop.get('status', 'active').title()}
                    
                    **Pricing:**
                    {'• Monthly Rent: ₦' + f"{prop['rent_monthly']:,}" if prop.get('rent_monthly') else ''}
                    {'• Sale Price: ₦' + f"{prop['sale_price']:,}" if prop.get('sale_price') else ''}
                    
                    **Performance:**
                    • Views: {random.randint(15, 250)}
                    • Inquiries: {random.randint(3, 25)}
                    • Rating: {prop.get('avg_rating', 4.0)}/5
                    """)
                
                with col2:
                    st.markdown("**Quick Actions**")
                    
                    if st.button("Edit Listing", key=f"edit_prop_{prop['id']}"):
                        st.info("Edit functionality coming soon!")
                    
                    if st.button("View Analytics", key=f"analytics_prop_{prop['id']}"):
                        st.info("Analytics dashboard coming soon!")
                    
                    if prop.get('status') == 'active':
                        if st.button("Pause Listing", key=f"pause_prop_{prop['id']}"):
                            prop['status'] = 'paused'
                            st.success("Listing paused")
                            st.rerun()
                    else:
                        if st.button("Activate Listing", key=f"activate_prop_{prop['id']}"):
                            prop['status'] = 'active'
                            st.success("Listing activated")
                            st.rerun()
    else:
        st.info("No properties listed yet.")
        if st.button("List Your First Property", type="primary"):
            st.info("Navigate to 'List New Property' to add your first property")

def show_land_developer_dashboard():
    st.subheader("Land Development Portfolio")
    
    user_land = []
    for city, land_plots in st.session_state.land_database.items():
        for land in land_plots:
            if land.get('owner_id') == st.session_state.current_user:
                land_copy = land.copy()
                land_copy['city'] = city
                user_land.append(land_copy)
    
    if user_land:
        col1, col2, col3, col4 = st.columns(4)
        
        total_land = len(user_land)
        total_value = sum(l.get('price_total', 0) for l in user_land)
        total_area = sum(l.get('land_size_sqm', 0) for l in user_land)
        avg_rating = np.mean([l.get('avg_rating', 4.0) for l in user_land])
        
        with col1:
            st.metric("Total Land Plots", total_land)
        with col2:
            st.metric("Portfolio Value", f"₦{total_value/1000000:.1f}M")
        with col3:
            st.metric("Total Area", f"{total_area/10000:.1f} Hectares")
        with col4:
            st.metric("Avg Rating", f"{avg_rating:.1f}/5")
        
        st.subheader("Your Land Holdings")
        for land in user_land:
            with st.expander(f"{land['name']} - {land['location']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    **Land Details:**
                    • Size: {land['land_size_sqm']:,} sqm ({land['land_size_sqm']/10000:.2f} hectares)
                    • Use: {land['land_use']} | Zoning: {land.get('zoning', 'N/A')}
                    • Status: {land.get('status', 'active').Title()}
                    
                    **Pricing:**
                    • Total Value: ₦{land['price_total']:,}
                    • Price per SqM: ₦{land.get('price_per_sqm', 0):,}
                    
                    **Documentation:**
                    • Title: {land.get('title_document', 'N/A')}
                    • Survey: {land.get('survey_status', 'N/A')}
                    
                    **Performance:**
                    • Views: {random.randint(10, 150)}
                    • Inquiries: {random.randint(2, 20)}
                    • Rating: {land.get('avg_rating', 4.0)}/5
                    """)
                
                with col2:
                    st.markdown("**Quick Actions**")
                    
                    if st.button("Edit Listing", key=f"edit_land_{land['id']}"):
                        st.info("Edit functionality coming soon!")
                    
                    if st.button("Development Plan", key=f"develop_land_{land['id']}"):
                        st.info("Development planning tools coming soon!")
                    
                    if land.get('status') == 'active':
                        if st.button("Pause Listing", key=f"pause_land_{land['id']}"):
                            land['status'] = 'paused'
                            st.success("Listing paused")
                            st.rerun()
                    else:
                        if st.button("Activate Listing", key=f"activate_land_{land['id']}"):
                            land['status'] = 'active'
                            st.success("Listing activated")
                            st.rerun()
    else:
        st.info("No land plots listed yet.")
        if st.button("List Your First Land Plot", type="primary"):
            st.info("Navigate to 'List New Land' to add your first land")

def show_property_tenant_dashboard():
    st.subheader("Property Tenant Management Portal")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Properties", "1")
    with col2:
        st.metric("Monthly Rent", "₦2.5M")
    with col3:
        st.metric("Next Due Date", "Mar 15")
    with col4:
        st.metric("Payment Status", "✅ Current")
    
    st.info("Tenant management features coming soon!")

def show_property_agent_dashboard():
    st.subheader("Property Agent Management Portal")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Property Listings", "12")
    with col2:
        st.metric("This Month Sales", "₦450M")
    with col3:
        st.metric("Commission Earned", "₦22.5M")
    with col4:
        st.metric("Client Satisfaction", "4.8/5")
    
    st.info("Property agent-specific features coming soon!")

def show_property_investor_dashboard():
    st.subheader("Property Investment Portfolio")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Property Portfolio Value", "₦2.8B")
    with col2:
        st.metric("Monthly Rental Income", "₦45M")
    with col3:
        st.metric("Property ROI This Year", "14.2%")
    with col4:
        st.metric("Properties Owned", "28")
    
    st.info("Property investor analytics dashboard coming soon!")

def show_land_investor_dashboard():
    st.subheader("Land Investment Portfolio")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Land Portfolio Value", "₦5.2B")
    with col2:
        st.metric("Total Land Area", "45 Hectares")
    with col3:
        st.metric("Land ROI This Year", "18.7%")
    with col4:
        st.metric("Land Plots Owned", "15")
    
    st.info("Land investor analytics dashboard coming soon!")

def show_general_property_dashboard():
    st.subheader("Your Property Experience Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Recent Property Searches**\n\n• 3BR apartments in Lekki\n• Investment properties\n• Luxury homes in Ikoyi")
    
    with col2:
        st.success("**Saved Properties**\n\n• Luxury 3BR Apartment - Ikoyi\n• Modern Duplex - Lekki\n• Executive Villa - Maitama")
    
    with col3:
        st.warning("**Property Alerts**\n\n• New properties in Lekki\n• Price drops in preferred areas\n• Investment opportunities")

def show_general_land_dashboard():
    st.subheader("Your Land Investment Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Recent Land Searches**\n\n• Commercial land in VI\n• Development opportunities\n• Industrial plots in Ikorodu")
    
    with col2:
        st.success("**Watchlisted Land**\n\n• Commercial Plot - Victoria Island\n• Residential Land - Maitama\n• Industrial Zone - Ikorodu")
    
    with col3:
        st.warning("**Land Market Alerts**\n\n• New land in growth corridors\n• Price opportunities\n• Development zone updates")

def main_app():
    if not st.session_state.current_user:
        show_login_signup()
        return
    
    if not st.session_state.portal_selection:
        show_portal_selection()
        return
    
    portal = st.session_state.portal_selection
    
    with st.sidebar:
        st.title("RealtyXperience")
        st.markdown(f"*{portal.title()} Portal*")
        st.markdown(f"*Welcome, {st.session_state.current_user}*")
        
        # AI System Status
        st.markdown("---")
        st.markdown("### AI System Status")
        if st.session_state.ai_system.claude_available:
            st.success("🤖 AI Assistants: Online")
        else:
            st.warning("🤖 AI Assistants: Limited")
        
        # Quick DB test
        if st.button("Test Snowflake DB", key="sidebar_db_test"):
            if st.session_state.ai_system.knowledge_base.connect():
                st.success("✅ Database: Connected")
            else:
                st.error("❌ Database: Offline")
        
        user_type = st.session_state.user_type
        
        if portal == "properties":
            if user_type == "tenant":
                page_options = ["Dashboard", "Find Properties", "MR X AI Assistant"]
            elif user_type == "host":
                page_options = ["Dashboard", "List New Property", "MR X AI Assistant"]
            elif user_type == "agent":
                page_options = ["Dashboard", "Find Properties", "List Property", "MR X AI Assistant"]
            elif user_type == "investor":
                page_options = ["Dashboard", "Investment Opportunities", "MR X AI Assistant"]
            else:
                page_options = ["Dashboard", "Find Properties", "MR X AI Assistant", "List Property"]
        
        elif portal == "land":
            if user_type == "land_developer":
                page_options = ["Dashboard", "List New Land", "LANDLORD AI Assistant"]
            elif user_type == "investor":
                page_options = ["Dashboard", "Land Opportunities", "LANDLORD AI Assistant"]
            elif user_type == "agent":
                page_options = ["Dashboard", "Find Land", "List Land", "LANDLORD AI Assistant"]
            else:
                page_options = ["Dashboard", "Find Land", "LANDLORD AI Assistant", "List Land"]
        
        page = st.selectbox("Navigate:", page_options)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Switch Portal"):
                st.session_state.portal_selection = None
                st.rerun()
        with col2:
            if st.button("Logout"):
                UserAuth.logout()
                st.rerun()
        
        st.markdown("---")
        st.markdown("### Quick Insights")
        
        if portal == "properties":
            all_props = get_all_properties()
            if all_props:
                avg_demand = np.mean([p.get('demand_score', 7.0) for p in all_props])
                market_status = "High Demand" if avg_demand > 8 else "Stable" if avg_demand > 7 else "Buyer's Market"
                st.info(f"Property Market: {market_status}")
                
                user_city = "Lagos"
                city_props = [p for p in all_props if p.get('city') == user_city]
                if city_props:
                    city_avg_rent = np.mean([p.get('rent_monthly', 0) for p in city_props if p.get('rent_monthly')])
                    st.success(f"{user_city} Avg Rent: ₦{city_avg_rent:,.0f}")
        
        elif portal == "land":
            all_land = get_all_land()
            if all_land:
                avg_demand = np.mean([l.get('demand_score', 7.0) for l in all_land])
                market_status = "High Demand" if avg_demand > 8 else "Stable" if avg_demand > 7 else "Buyer's Market"
                st.info(f"Land Market: {market_status}")
                
                user_city = "Lagos"
                city_land = [l for l in all_land if l.get('city') == user_city]
                if city_land:
                    city_avg_price = np.mean([l.get('price_per_sqm', 0) for l in city_land if l.get('price_per_sqm')])
                    st.success(f"{user_city} Avg Price: ₦{city_avg_price:,.0f}/sqm")
    
    # Main content area based on portal and page selection
    if portal == "properties":
        if page == "Dashboard":
            show_dashboard()
        elif page == "Find Properties" or page == "Investment Opportunities":
            show_property_search()
        elif page == "MR X AI Assistant":
            show_mr_x_chat()
        elif page in ["List New Property", "List Property"]:
            show_property_upload_form()
        else:
            show_dashboard()
    
    elif portal == "land":
        if page == "Dashboard":
            show_dashboard()
        elif page == "Find Land" or page == "Land Opportunities":
            show_land_search()
        elif page == "LANDLORD AI Assistant":
            show_landlord_chat()
        elif page in ["List New Land", "List Land"]:
            show_land_upload_form()
        else:
            show_dashboard()

if __name__ == "__main__":
    if "welcomed" not in st.session_state:
        if not st.session_state.current_user:
            st.markdown("""
            ## Welcome to RealtyXperience!
            ### Your Complete AI-Powered Real Estate Platform
            
            **Choose Your Portal:**
            - **Properties Portal** - Residential & commercial properties with MR X AI assistant
            - **Land Portal** - Investment land opportunities with LANDLORD AI assistant
            
            **Featured Services:**
            - **Smart Search** with AI matching powered by Snowflake knowledge database
            - **AI Assistants** - MR X for properties, LANDLORD for land investment
            - **Dynamic Pricing** optimization for hosts and developers
            - **Portfolio Management** for all user types
            - **Investment Analysis** and predictions
            - **Management Systems** for tenants and developers
            
            **Sign up or log in to get started!**
            """)
        st.session_state.welcomed = True
    
    main_app()
