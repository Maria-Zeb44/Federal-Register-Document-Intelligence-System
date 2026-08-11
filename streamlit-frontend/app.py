import streamlit as st
import requests
import json

# ============================================
# 🔓 BYPASS AUTHENTICATION - TESTING MODE
# ============================================
# This bypasses the login page for testing
# Remove or comment this when login is fixed
st.session_state.authenticated = True
st.session_state.user = {"id": 1, "name": "Test User", "email": "test@123.com"}
# ============================================

API_BASE = "http://localhost:8000/api"

st.set_page_config(
    page_title="Federal Register Intelligence System",
    page_icon="📜",
    layout="wide"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'selected_doc_id' not in st.session_state:
    st.session_state.selected_doc_id = None
if 'documents' not in st.session_state:
    st.session_state.documents = []
if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = False

# ============================================
# LOGIN / SIGNUP PAGE
# ============================================
def login_page():
    st.title("📜 Federal Register Intelligence System")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Signup"])
    
    with tab1:
        st.subheader("Welcome Back")
        login_email = st.text_input("Email", key="login_email_input")
        login_password = st.text_input("Password", type="password", key="login_password_input")
        
        if st.button("Login", key="login_btn", use_container_width=True):
            if login_email and login_password:
                try:
                    response = requests.post(
                        f"{API_BASE}/auth/login",
                        json={"email": login_email, "password": login_password}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.authenticated = True
                        st.session_state.user = data['user']
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend. Make sure it's running on port 8000.")
            else:
                st.warning("Please fill all fields")
    
    with tab2:
        st.subheader("Create Account")
        signup_name = st.text_input("Full Name", key="signup_name_input")
        signup_email = st.text_input("Email", key="signup_email_input")
        signup_password = st.text_input("Password", type="password", key="signup_password_input")
        
        if st.button("Create Account", key="signup_btn", use_container_width=True):
            if all([signup_name, signup_email, signup_password]):
                try:
                    response = requests.post(
                        f"{API_BASE}/auth/signup",
                        json={"name": signup_name, "email": signup_email, "password": signup_password}
                    )
                    if response.status_code == 200:
                        st.success("✅ Account created! Please login.")
                    else:
                        st.error("❌ Signup failed. Email may already be in use.")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend.")
            else:
                st.warning("Please fill all fields")

# ============================================
# DASHBOARD PAGE
# ============================================
def dashboard_page():
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user['name']}")
        st.markdown(f"📧 {st.session_state.user['email']}")
        st.markdown("---")
        
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.selected_doc_id = None
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🛠️ Actions")
        
        if st.button("🔄 Collect Documents", key="collect_btn", use_container_width=True):
            with st.spinner("Collecting documents..."):
                try:
                    response = requests.post(f"{API_BASE}/documents/collect?limit=50")
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"✅ Collected {data.get('processed', 0)} documents with {data.get('chunks_created', 0)} chunks!")
                        st.session_state.documents_loaded = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to collect documents")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Main content
    st.title("📚 Executive Orders Dashboard")
    
    # Search
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_term = st.text_input("🔍 Search documents", placeholder="Search by title or document number...", key="search_input")
    with col2:
        if st.button("🔄 Refresh", key="refresh_btn", use_container_width=True):
            st.session_state.documents_loaded = False
            st.rerun()
    with col3:
        if st.button("Search", key="search_btn", use_container_width=True):
            st.rerun()
    
    # Fetch and display documents
    if not st.session_state.documents_loaded:
        with st.spinner("Loading documents..."):
            try:
                response = requests.get(f"{API_BASE}/documents/?limit=50")
                if response.status_code == 200:
                    st.session_state.documents = response.json().get('documents', [])
                    st.session_state.documents_loaded = True
            except Exception as e:
                st.error(f"Error loading documents: {str(e)}")
    
    docs = st.session_state.documents
    
    if not docs:
        st.info("📭 No documents found. Click 'Collect Documents' to fetch Executive Orders.")
    else:
        st.markdown(f"**Found {len(docs)} documents**")
        
        # Filter by search term
        if search_term:
            docs = [d for d in docs if search_term.lower() in d.get('title', '').lower() or search_term in d.get('document_number', '')]
            st.markdown(f"**Found {len(docs)} matching documents**")
        
        for doc in docs:
            with st.container():
                col1, col2, col3 = st.columns([4, 2, 1])
                with col1:
                    st.markdown(f"### 📄 {doc['title'][:80]}..." if len(doc['title']) > 80 else f"### 📄 {doc['title']}")
                with col2:
                    st.markdown(f"**EO #:** {doc.get('executive_order_number', 'N/A')}")
                    st.markdown(f"📅 {doc.get('publication_date', 'N/A')}")
                with col3:
                    if st.button("📖 View", key=f"view_btn_{doc['id']}", use_container_width=True):
                        st.session_state.selected_doc_id = doc['id']
                        st.rerun()
                st.divider()
    
    # Document detail view
    if st.session_state.selected_doc_id:
        st.markdown("---")
        st.subheader("📄 Document Details")
        
        try:
            response = requests.get(f"{API_BASE}/documents/{st.session_state.selected_doc_id}")
            if response.status_code == 200:
                doc = response.json()
                
                if st.button("⬅ Back to Dashboard", key="back_btn", use_container_width=False):
                    st.session_state.selected_doc_id = None
                    st.rerun()
                
                st.markdown(f"## {doc['title']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**📋 Document #:** {doc.get('document_number', 'N/A')}")
                    st.markdown(f"**🔢 EO #:** {doc.get('executive_order_number', 'N/A')}")
                with col2:
                    st.markdown(f"**📅 Published:** {doc.get('publication_date', 'N/A')}")
                    if doc.get('pdf_url'):
                        st.markdown(f"[📥 Download PDF]({doc.get('pdf_url')})")
                
                if doc.get('abstract'):
                    st.markdown("### 📝 Abstract")
                    st.write(doc['abstract'])
                
                if doc.get('full_text'):
                    with st.expander("📄 Full Document Text", expanded=False):
                        st.text_area("Document Text", doc['full_text'], height=400, disabled=True, key="doc_text_area")
                
                # ============================================
                # RAG question section - PASSING DOCUMENT ID
                # ============================================
                st.markdown("---")
                st.markdown("### 💬 Ask a Question About This Document")
                
                question = st.text_area(
                    "Your question:", 
                    placeholder="What does this executive order say about...", 
                    height=100, 
                    key="question_input"
                )
                
                if st.button("🔍 Ask Question", key="ask_btn", use_container_width=True):
                    if question:
                        with st.spinner("Searching documents and generating answer..."):
                            try:
                                # ✅ PASS document_id as query parameter
                                response = requests.post(
                                    f"{API_BASE}/rag/query?document_id={doc['id']}",
                                    json={"question": question}
                                )
                                if response.status_code == 200:
                                    data = response.json()
                                    st.markdown("#### 🤖 Answer")
                                    st.markdown(data['answer'])
                                    
                                    if data.get('sources'):
                                        st.markdown("#### 📚 Sources")
                                        for source in data['sources']:
                                            st.markdown(f"- {source['title']} (EO #{source.get('executive_order_number', 'N/A')})")
                                else:
                                    st.error(f"Failed to get answer: {response.text}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    else:
                        st.warning("Please enter a question")
            else:
                st.error("Document not found")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ============================================
# RAG CHAT PAGE
# ============================================
def rag_chat_page():
    st.title("💬 RAG Chat - Ask Questions About Executive Orders")
    st.markdown("Ask questions about the Executive Orders in the system.")
    
    if "rag_messages" not in st.session_state:
        st.session_state.rag_messages = []
    
    for message in st.session_state.rag_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask a question about Executive Orders..."):
        st.session_state.rag_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating answer..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/rag/query",
                        json={"question": prompt}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        answer = data['answer']
                        st.markdown(answer)
                        
                        if data.get('sources'):
                            with st.expander("📚 Sources"):
                                for source in data['sources']:
                                    st.markdown(f"- {source['title']} (EO #{source.get('executive_order_number', 'N/A')})")
                        
                        st.session_state.rag_messages.append({"role": "assistant", "content": answer})
                    else:
                        st.error(f"Failed to get answer: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    if st.button("🗑️ Clear Chat", key="clear_chat_btn"):
        st.session_state.rag_messages = []
        st.rerun()

# ============================================
# MAIN
# ============================================
def main():
    if not st.session_state.authenticated:
        login_page()
    else:
        with st.sidebar:
            st.markdown(f"### 👤 {st.session_state.user['name']}")
            st.markdown(f"📧 {st.session_state.user['email']}")
            st.markdown("---")
            
            if st.button("📚 Dashboard", key="nav_dashboard_btn", use_container_width=True):
                st.session_state.page = "dashboard"
                st.rerun()
            
            if st.button("💬 RAG Chat", key="nav_rag_btn", use_container_width=True):
                st.session_state.page = "rag_chat"
                st.rerun()
            
            st.markdown("---")
            if st.button("🚪 Logout", key="nav_logout_btn", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.selected_doc_id = None
                st.session_state.rag_messages = []
                st.rerun()
        
        if 'page' not in st.session_state:
            st.session_state.page = "dashboard"
        
        if st.session_state.page == "dashboard":
            dashboard_page()
        elif st.session_state.page == "rag_chat":
            rag_chat_page()

if __name__ == "__main__":
    main()