"""
User authentication and management system
"""
import streamlit as st
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from database.connection.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class UserAuthManager:
    """User authentication and management"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.session_timeout = timedelta(hours=24)  # 24 hours session timeout
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, password_hash = stored_hash.split(':')
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == password_hash
        except ValueError:
            return False
    
    def create_user(self, username: str, email: str, password: str, organization: str = None) -> Dict[str, Any]:
        """Create a new user account"""
        try:
            # Check if user already exists
            if self.user_exists(username, email):
                return {"success": False, "message": "User already exists"}
            
            # Generate user ID
            user_id = f"user_{secrets.token_hex(8)}"
            
            # Hash password
            password_hash = self.hash_password(password)
            
            # Create user document
            user_data = {
                "user_id": user_id,
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "organization": organization or "Personal",
                "created_at": datetime.now(),
                "last_login": None,
                "is_active": True,
                "subscription_tier": "free",  # free, pro, enterprise
                "data_retention_days": 30
            }
            
            # Store in MongoDB
            if self.db_manager.is_connected():
                self.db_manager.get_collection('users').insert_one(user_data)
                logger.info(f"User created successfully: {username}")
                return {"success": True, "user_id": user_id, "message": "User created successfully"}
            else:
                logger.error("MongoDB not connected - cannot create user")
                return {"success": False, "message": "Database connection failed"}
                
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return {"success": False, "message": f"Error creating user: {str(e)}"}
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user login"""
        try:
            if not self.db_manager.is_connected():
                return {"success": False, "message": "Database connection failed"}
            
            # Find user by username or email
            user = self.db_manager.get_collection('users').find_one({
                "$or": [
                    {"username": username},
                    {"email": username}
                ],
                "is_active": True
            })
            
            if not user:
                return {"success": False, "message": "Invalid username or password"}
            
            # Verify password
            if not self.verify_password(password, user['password_hash']):
                return {"success": False, "message": "Invalid username or password"}
            
            # Update last login
            self.db_manager.get_collection('users').update_one(
                {"user_id": user['user_id']},
                {"$set": {"last_login": datetime.now()}}
            )
            
            logger.info(f"User authenticated successfully: {username}")
            return {
                "success": True,
                "user_id": user['user_id'],
                "username": user['username'],
                "email": user['email'],
                "organization": user['organization'],
                "subscription_tier": user['subscription_tier']
            }
            
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return {"success": False, "message": f"Authentication error: {str(e)}"}
    
    def user_exists(self, username: str, email: str) -> bool:
        """Check if user already exists"""
        try:
            if not self.db_manager.is_connected():
                return False
            
            existing_user = self.db_manager.get_collection('users').find_one({
                "$or": [
                    {"username": username},
                    {"email": email}
                ]
            })
            
            return existing_user is not None
            
        except Exception as e:
            logger.error(f"Error checking user existence: {str(e)}")
            return False
    
    def get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data by user ID"""
        try:
            if not self.db_manager.is_connected():
                return None
            
            user = self.db_manager.get_collection('users').find_one({"user_id": user_id})
            if user:
                # Remove password hash from response
                user.pop('password_hash', None)
                return user
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}")
            return None
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile"""
        try:
            if not self.db_manager.is_connected():
                return False
            
            # Remove sensitive fields that shouldn't be updated
            updates.pop('password_hash', None)
            updates.pop('user_id', None)
            updates.pop('created_at', None)
            
            updates['updated_at'] = datetime.now()
            
            result = self.db_manager.get_collection('users').update_one(
                {"user_id": user_id},
                {"$set": updates}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return False
    
    def create_session(self, user_id: str) -> str:
        """Create user session"""
        session_id = secrets.token_hex(32)
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + self.session_timeout,
            "is_active": True
        }
        
        if self.db_manager.is_connected():
            self.db_manager.get_collection('sessions').insert_one(session_data)
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[str]:
        """Validate session and return user_id"""
        try:
            if not self.db_manager.is_connected():
                return None
            
            session = self.db_manager.get_collection('sessions').find_one({
                "session_id": session_id,
                "is_active": True,
                "expires_at": {"$gt": datetime.now()}
            })
            
            if session:
                return session['user_id']
            
            return None
            
        except Exception as e:
            logger.error(f"Error validating session: {str(e)}")
            return None
    
    def logout_user(self, session_id: str) -> bool:
        """Logout user by invalidating session"""
        try:
            if not self.db_manager.is_connected():
                return False
            
            result = self.db_manager.get_collection('sessions').update_one(
                {"session_id": session_id},
                {"$set": {"is_active": False, "logged_out_at": datetime.now()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error logging out user: {str(e)}")
            return False

def render_login_page():
    """Render login/registration page"""
    st.title("🛡️ ChurnGuard Login")
    st.caption("AI-powered customer retention platform")
    
    # Initialize auth manager
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = UserAuthManager()
    
    # Create tabs for login and registration
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to your account")
        
        with st.form("login_form"):
            username = st.text_input("Username or Email", placeholder="Enter your username or email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("Login", type="primary")
            
            if login_button:
                if username and password:
                    with st.spinner("Authenticating..."):
                        result = st.session_state.auth_manager.authenticate_user(username, password)
                        
                        if result["success"]:
                            # Create session
                            session_id = st.session_state.auth_manager.create_session(result["user_id"])
                            
                            # Store in session state
                            st.session_state.authenticated = True
                            st.session_state.user_id = result["user_id"]
                            st.session_state.username = result["username"]
                            st.session_state.email = result["email"]
                            st.session_state.organization = result["organization"]
                            st.session_state.subscription_tier = result["subscription_tier"]
                            st.session_state.session_id = session_id
                            
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        st.subheader("Create a new account")
        
        with st.form("register_form"):
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="Enter your email address")
            organization = st.text_input("Organization (Optional)", placeholder="Your company name")
            password = st.text_input("Password", type="password", placeholder="Choose a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            register_button = st.form_submit_button("Register", type="primary")
            
            if register_button:
                if username and email and password and confirm_password:
                    if password != confirm_password:
                        st.error("❌ Passwords do not match")
                    elif len(password) < 6:
                        st.error("❌ Password must be at least 6 characters long")
                    else:
                        with st.spinner("Creating account..."):
                            result = st.session_state.auth_manager.create_user(
                                username, email, password, organization
                            )
                            
                            if result["success"]:
                                st.success("✅ Account created successfully! Please login.")
                                st.info("You can now login with your credentials.")
                            else:
                                st.error(f"❌ {result['message']}")
                else:
                    st.error("Please fill in all required fields")
    
    # Demo account option
    st.markdown("---")
    st.subheader("🚀 Try Demo Account")
    st.info("Want to try ChurnGuard without creating an account? Use our demo mode.")
    
    if st.button("Enter Demo Mode", type="secondary"):
        st.session_state.authenticated = True
        st.session_state.user_id = "demo_user"
        st.session_state.username = "Demo User"
        st.session_state.email = "demo@churnguard.com"
        st.session_state.organization = "Demo Organization"
        st.session_state.subscription_tier = "demo"
        st.session_state.session_id = "demo_session"
        
        st.success("✅ Entered demo mode!")
        st.rerun()

def render_logout():
    """Render logout functionality"""
    if st.session_state.get('authenticated', False):
        if st.session_state.get('session_id') and st.session_state.get('session_id') != 'demo_session':
            # Logout from database
            st.session_state.auth_manager.logout_user(st.session_state.session_id)
        
        # Clear session state
        for key in ['authenticated', 'user_id', 'username', 'email', 'organization', 'subscription_tier', 'session_id']:
            st.session_state.pop(key, None)
        
        st.success("✅ Logged out successfully!")
        st.rerun()
