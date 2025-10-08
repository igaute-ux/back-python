from supabase import create_client
from app.core.config import settings

class AuthService:
    @staticmethod
    async def authenticate_user(user_data):
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        result = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        return result