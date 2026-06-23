# backend/database.py

from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

# Grab values from .env file
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Create Supabase client
# Service key gives us full access to the database
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)