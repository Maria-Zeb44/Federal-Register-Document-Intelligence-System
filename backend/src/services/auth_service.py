import bcrypt
from src.core.database import Database

class AuthService:
    def __init__(self):
        self.db = Database()
    
    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_user(self, name: str, email: str, password: str):
        # Check if user exists
        existing = self.db.execute_query(
            "SELECT id FROM users WHERE email = %s",
            (email,),
            fetch=True
        )
        if existing:
            return None
        
        password_hash = self.hash_password(password)
        query = """
            INSERT INTO users (name, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id, name, email
        """
        result = self.db.execute_query(query, (name, email, password_hash), fetch=True)
        return result[0] if result else None
    
    def authenticate(self, email: str, password: str):
        result = self.db.execute_query(
            "SELECT id, name, email, password_hash FROM users WHERE email = %s",
            (email,),
            fetch=True
        )
        if not result:
            return None
        
        user_data = result[0]
        if self.verify_password(password, user_data['password_hash']):
            return {
                "id": user_data['id'],
                "name": user_data['name'],
                "email": user_data['email']
            }
        return None