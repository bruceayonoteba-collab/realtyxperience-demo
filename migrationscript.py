# SQLite Migration - Replace Snowflake with Free Database
# Save as: migrate_to_sqlite.py

import sqlite3
import pandas as pd

# Step 1: Create SQLite database from your CSV files
def create_database():
    """Create SQLite database with your knowledge data"""
    
    # Create database file
    conn = sqlite3.connect('realtyxperience_knowledge.db')
    cursor = conn.cursor()
    
    # Create PROPERTY_KNOWLEDGE table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PROPERTY_KNOWLEDGE (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        CATEGORY TEXT,
        SUBCATEGORY TEXT,
        QUESTION TEXT,
        ANSWER TEXT,
        TAGS TEXT,
        DIFFICULTY_LEVEL TEXT
    )
    ''')
    
    # Create LAND_KNOWLEDGE table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS LAND_KNOWLEDGE (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        CATEGORY TEXT,
        SUBCATEGORY TEXT,
        QUESTION TEXT,
        ANSWER TEXT,
        TAGS TEXT,
        DIFFICULTY_LEVEL TEXT
    )
    ''')
    
    conn.commit()
    
    # Load CSV files (use the files you exported from Snowflake)
    try:
        property_df = pd.read_csv('nigeria_property_knowledge.csv')
        land_df = pd.read_csv('nigeria_land_knowledge.csv')
        
        # Insert data
        property_df.to_sql('PROPERTY_KNOWLEDGE', conn, if_exists='replace', index=False)
        land_df.to_sql('LAND_KNOWLEDGE', conn, if_exists='replace', index=False)
        
        print("✅ Database created successfully!")
        print(f"✅ Property knowledge: {len(property_df)} rows")
        print(f"✅ Land knowledge: {len(land_df)} rows")
        
    except FileNotFoundError:
        print("❌ CSV files not found. Make sure you have:")
        print("   - nigeria_property_knowledge.csv")
        print("   - nigeria_land_knowledge.csv")
    
    conn.close()

# Step 2: Updated AI Assistant Code using SQLite
import streamlit as st
import sqlite3
import anthropic

# Your Claude API key
CLAUDE_API_KEY = "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"

class SQLiteKnowledgeBase:
    """SQLite knowledge base - no monthly fees"""
    
    def __init__(self, db_path='realtyxperience_knowledge.db'):
        self.db_path = db_path
    
    def search_property_knowledge(self, query, max_results=3):
        """Search property knowledge"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = """
        SELECT QUESTION, ANSWER, CATEGORY, TAGS 
        FROM PROPERTY_KNOWLEDGE 
        WHERE LOWER(QUESTION || ' ' || ANSWER || ' ' || TAGS) LIKE LOWER(?)
        ORDER BY 
            CASE 
                WHEN LOWER(QUESTION) LIKE LOWER(?) THEN 1
                WHEN LOWER(CATEGORY) LIKE LOWER(?) THEN 2
                ELSE 3
            END
        LIMIT ?
        """
        
        search_term = f'%{query}%'
        cursor.execute(sql, (search_term, search_term, search_term, max_results))
        results = cursor.fetchall()
        
        knowledge = []
        for row in results:
            knowledge.append({
                'question': row[0],
                'answer': row[1],
                'category': row[2],
                'tags': row[3]
            })
        
        conn.close()
        return knowledge
    
    def search_land_knowledge(self, query, max_results=3):
        """Search land knowledge"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = """
        SELECT QUESTION, ANSWER, CATEGORY, TAGS 
        FROM LAND_KNOWLEDGE 
        WHERE LOWER(QUESTION || ' ' || ANSWER || ' ' || TAGS) LIKE LOWER(?)
        ORDER BY 
            CASE 
                WHEN LOWER(QUESTION) LIKE LOWER(?) THEN 1
                WHEN LOWER(CATEGORY) LIKE LOWER(?) THEN 2
                ELSE 3
            END
        LIMIT ?
        """
        
        search_term = f'%{query}%'
        cursor.execute(sql, (search_term, search_term, search_term, max_results))
        results = cursor.fetchall()
        
        knowledge = []
        for row in results:
            knowledge.append({
                'question': row[0],
                'answer': row[1],
                'category': row[2],
                'tags': row[3]
            })
        
        conn.close()
        return knowledge

class RealtyXperienceAI:
    """Your AI Assistants - now with SQLite"""
    
    def __init__(self):
        self.knowledge_base = SQLiteKnowledgeBase()
        try:
            self.claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
            self.claude_available = True
        except:
            self.claude_available = False
    
    def mr_x_response(self, user_question):
        """Mr. X - Property Expert"""
        knowledge = self.knowledge_base.search_property_knowledge(user_question, 3)
        
        if not knowledge:
            return "I couldn't find specific information about that in my knowledge base."
        
        if self.claude_available:
            try:
                knowledge_context = "Here's what I know:\n\n"
                for item in knowledge:
                    knowledge_context += f"Q: {item['question']}\nA: {item['answer']}\n\n"
                
                system_prompt = "You are Mr. X, a property investment expert for RealtyXperience. Use the knowledge provided to give helpful answers about Nigerian real estate."
                
                response = self.claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": f"{knowledge_context}\n\nUser question: {user_question}"}]
                )
                
                return response.content[0].text
            except:
                pass
        
        # Fallback
        response = "**Mr. X:** Based on my knowledge:\n\n"
        for item in knowledge:
            response += f"**{item['question']}**\n\n{item['answer']}\n\n---\n\n"
        return response
    
    def landlord_response(self, user_question):
        """Landlord - Land Expert"""
        knowledge = self.knowledge_base.search_land_knowledge(user_question, 3)
        
        if not knowledge:
            return "I couldn't find specific information about that in my knowledge base."
        
        if self.claude_available:
            try:
                knowledge_context = "Here's what I know:\n\n"
                for item in knowledge:
                    knowledge_context += f"Q: {item['question']}\nA: {item['answer']}\n\n"
                
                system_prompt = "You are Landlord, a land development expert for RealtyXperience. Use the knowledge provided to give helpful answers about Nigerian land investment."
                
                response = self.claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": f"{knowledge_context}\n\nUser question: {user_question}"}]
                )
                
                return response.content[0].text
            except:
                pass
        
        # Fallback
        response = "**Landlord:** Based on my knowledge:\n\n"
        for item in knowledge:
            response += f"**{item['question']}**\n\n{item['answer']}\n\n---\n\n"
        return response

def main():
    st.set_page_config(page_title="RealtyXperience AI Demo", page_icon="🏠")
    
    st.title("🏠 RealtyXperience AI Assistants")
    st.subheader("Nigerian Real Estate Intelligence")
    
    if 'ai' not in st.session_state:
        st.session_state.ai = RealtyXperienceAI()
    
    # Sidebar
    st.sidebar.title("Choose Assistant")
    assistant = st.sidebar.radio("Select:", ["Mr. X (Property)", "Landlord (Land)"])
    
    # Quick tests
    st.sidebar.markdown("---")
    st.sidebar.subheader("Try These")
    if "Mr. X" in assistant:
        if st.sidebar.button("What is ROI?"):
            st.session_state.test_q = "How do I calculate ROI for rental property?"
        if st.sidebar.button("What is cash flow?"):
            st.session_state.test_q = "What is cash flow?"
    else:
        if st.sidebar.button("What is C of O?"):
            st.session_state.test_q = "What is a Certificate of Occupancy?"
        if st.sidebar.button("Land valuation?"):
            st.session_state.test_q = "How do I determine land value?"
    
    # Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "test_q" in st.session_state:
        prompt = st.session_state.test_q
        del st.session_state.test_q
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Thinking..."):
            if "Mr. X" in assistant:
                response = st.session_state.ai.mr_x_response(prompt)
            else:
                response = st.session_state.ai.landlord_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about Nigerian real estate..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Consulting knowledge base..."):
                if "Mr. X" in assistant:
                    response = st.session_state.ai.mr_x_response(prompt)
                else:
                    response = st.session_state.ai.landlord_response(prompt)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    # First time: create database
    # create_database()
    
    # Then run app
    main()
