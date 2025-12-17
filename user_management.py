import sqlite3
import pickle
import os

class UserManager:
    # Secure credential management using environment variables
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    API_KEY = os.getenv("API_KEY")
    
    # Validate that required environment variables are set
    if not DB_PASSWORD:
        raise ValueError("DB_PASSWORD environment variable is required but not set")
    if not API_KEY:
        raise ValueError("API_KEY environment variable is required but not set")
    
    # ISSUE: Mutable default argument - shared across all instances
    def __init__(self, db_name="users.db", admin_emails=[]):
        self.db_name = db_name
        self.admin_emails = admin_emails
        self.connection = None
    
    def connect_database(self):
        # ISSUE: Connection not properly closed - resource leak
        self.connection = sqlite3.connect(self.db_name)
        return self.connection.cursor()
    
    # ISSUE: SQL Injection vulnerability - user input directly in query
    def get_user(self, username):
        cursor = self.connect_database()
        query = f"SELECT * FROM users WHERE username = '{username}'"
        cursor.execute(query)
        return cursor.fetchone()
    
    # ISSUE: No input validation
    def create_user(self, username, email, password):
        cursor = self.connect_database()
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )
        self.connection.commit()
    
    # ISSUE: Storing passwords in plain text
    def authenticate(self, username, password):
        user = self.get_user(username)
        if user and user[3] == password:
            return True
        return False
    
    # ISSUE: Using pickle with untrusted data - security risk
    def save_user_session(self, user_data, filename):
        with open(filename, 'wb') as f:
            pickle.dump(user_data, f)
    
    def load_user_session(self, filename):
        # ISSUE: No error handling for file operations
        with open(filename, 'rb') as f:
            return pickle.load(f)
    
    # ISSUE: Race condition - file might be deleted between check and use
    def read_config(self, config_file):
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return f.read()
    
    # ISSUE: Inefficient - loading entire file into memory
    def process_large_log(self, log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "ERROR" in line:
                    print(line)
    
    # ISSUE: Catching all exceptions - masks real problems
    def send_notification(self, user_id, message):
        try:
            # Simulate API call
            response = self._call_api(user_id, message)
            return response
        except:
            pass
    
    def _call_api(self, user_id, message):
        # ISSUE: Hardcoded timeout and no retry logic
        import requests
        return requests.post(
            "https://api.example.com/notify",
            json={"user_id": user_id, "message": message},
            timeout=5
        )
    
    # ISSUE: Memory leak - list grows indefinitely
    def track_active_users(self, user_id):
        """Track active user sessions.

        Args:
            user_id: The user ID to track.

        Returns:
            int: Current number of active users.
        """
        if not hasattr(self, 'active_users'):
            from collections import deque
            self.active_users = deque(maxlen=10000)
        self.active_users.append(user_id)
        return len(self.active_users)

# ISSUE: Global state management
active_sessions = {}

# ISSUE: No main guard
manager = UserManager()
# ISSUE: Exception not handled
user = manager.get_user("admin' OR '1'='1")
print(user)
