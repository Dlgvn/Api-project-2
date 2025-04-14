from supabase import create_client, Client

url: str = "https://fhbnbquxzuumvhmycflu.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZoYm5icXV4enV1bXZobXljZmx1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE4Mzk0NDksImV4cCI6MjA1NzQxNTQ0OX0.odm7X9uZO6DEkynv4AVIgllDtOojWnIwU1zAtafRMnI"

supabase: Client = create_client(url, key)