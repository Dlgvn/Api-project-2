from fastapi import APIRouter, HTTPException
from models import SongResponse, UserCreate
from supabase_client import supabase
from typing import List, Optional
import logging

router = APIRouter(prefix="/user", tags=["user"])


logger = logging.getLogger(__name__)

@router.post("/register/", status_code=201)
async def register_user(user: UserCreate):
    """Register a new user with username and password"""
    try:
        user_data = user.dict(exclude_unset=True)
        

        existing = supabase.table("users").select("*").eq("username", user_data['username']).execute()
        if existing.data:
            raise HTTPException(400, "Username already exists")
            

        result = supabase.table("users").insert(user_data).execute()
        
        if not result.data:
            raise HTTPException(400, "Failed to create user")
            
        return {"message": "User created successfully", "user_id": result.data[0]["id"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to register user")
        raise HTTPException(500, "Failed to register user") from e

@router.get("/songs/", response_model=List[SongResponse])
async def search_songs(
    artist_name: Optional[str] = None,
    track_name: Optional[str] = None
):
    """Search songs by track name or artist name"""
    try:
        query = supabase.table("songs").select("*")
        
        if artist_name:
            query = query.ilike("artist_name", f"%{artist_name}%")
        if track_name:
            query = query.ilike("track_name", f"%{track_name}%")
        
        result = query.execute()
        
        if not hasattr(result, 'data'):
            logger.error("Invalid response format from Supabase")
            raise HTTPException(500, "Invalid server response")
            
        return result.data or []

    except Exception as e:
        logger.exception("Failed to search songs")
        raise HTTPException(500, "Failed to search songs") from e

@router.get("/favorites/{user_id}", response_model=List[SongResponse])
async def get_favorite_songs(user_id: int):
    """Get all favorite songs for a user"""
    try:

        favorites_result = supabase.table("favorites").select("song_id").eq("user_id", user_id).execute()
        
        if not hasattr(favorites_result, 'data'):
            raise HTTPException(500, "Invalid server response")
            
        if not favorites_result.data:
            return []
            
        song_ids = [fav["song_id"] for fav in favorites_result.data]
        

        songs_result = supabase.table("songs").select("*").in_("id", song_ids).execute()
        
        if not hasattr(songs_result, 'data'):
            raise HTTPException(500, "Invalid server response")
            
        return songs_result.data or []
        
    except Exception as e:
        logger.exception(f"Failed to get favorite songs for user {user_id}")
        raise HTTPException(500, "Failed to get favorite songs") from e

@router.post("/favorites/{user_id}/{song_id}", status_code=201)
async def add_favorite_song(user_id: int, song_id: int):
    """Add a song to user's favorites """
    try:

        song = supabase.table("songs").select("*").eq("id", song_id).execute()
        if not song.data:
            raise HTTPException(404, "Song not found")
            

        user = supabase.table("users").select("*").eq("id", user_id).execute()
        if not user.data:
            raise HTTPException(404, "User not found")
            

        existing = supabase.table("favorites").select("*").eq("user_id", user_id).eq("song_id", song_id).execute()
        if existing.data:
            raise HTTPException(400, "Song already in favorites")
            

        result = supabase.table("favorites").insert({
            "user_id": user_id,
            "song_id": song_id
        }).execute()
        
        if not result.data:
            raise HTTPException(400, "Failed to add favorite")
            
        return {"message": "Song added to favorites"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to add favorite song {song_id} for user {user_id}")
        raise HTTPException(500, "Failed to add favorite song") from e

@router.delete("/favorites/{user_id}/{song_id}")
async def remove_favorite_song(user_id: int, song_id: int):
    """Remove a song from user's favorites"""
    try:

        existing = supabase.table("favorites").select("*").eq("user_id", user_id).eq("song_id", song_id).execute()
        if not existing.data:
            raise HTTPException(404, "Favorite not found")
            

        supabase.table("favorites").delete().eq("user_id", user_id).eq("song_id", song_id).execute()
        
        return {"message": "Song removed from favorites"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to remove favorite song {song_id} for user {user_id}")
        raise HTTPException(500, "Failed to remove favorite song") from e