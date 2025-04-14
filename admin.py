from fastapi import APIRouter, HTTPException
from models import SongCreate, SongUpdate, SongResponse
from supabase_client import supabase
from typing import List, Optional
import logging

router = APIRouter(prefix="/admin", tags=["admin"])

logger = logging.getLogger(__name__)

@router.get("/songs/", response_model=List[SongResponse])
async def search_songs(
    artist_name: Optional[str] = None,
    track_name: Optional[str] = None,
    year: Optional[int] = None,
    genre: Optional[str] = None
):
    """Search songs"""
    try:
        query = supabase.table("songs").select("*")

        if artist_name:
            query = query.ilike("artist_name", f"%{artist_name}%")
        if track_name:
            query = query.ilike("track_name", f"%{track_name}%")
        if year:
            query = query.eq("year", year)
        if genre:
            query = query.eq("genre", genre)
        
        result = query.execute()
        
        if not hasattr(result, 'data'):
            logger.error("Invalid response format from Supabase")
            raise HTTPException(500, "Invalid server response")
            
        return result.data or []

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to search songs")
        raise HTTPException(500, "Failed to search songs") from e

@router.post("/songs/", response_model=SongResponse, status_code=201)
async def create_song(song: SongCreate):
    """Create new song """
    try:

        song_data = song.dict(exclude_unset=True)
        song_data.pop('id', None)
        

        required_fields = ['artist_name', 'track_name', 'track_id', 'year', 'genre']
        if not all(field in song_data for field in required_fields):
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields. Required: {required_fields}"
            )
        
        result = supabase.table("songs").insert(song_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Failed to create song")
            
        return result.data[0]
        
    except Exception as e:
        logger.exception("Failed to create song")
        if 'null value' in str(e):
            raise HTTPException(
                status_code=400,
                detail="Database error: Required field missing"
            )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create song: {str(e)}"
        )
        
@router.put("/songs/{song_id}")
async def update_song(song_id: int, song: SongUpdate):
    """Update existing song"""
    try:

        existing = supabase.table("songs").select("*").eq("id", song_id).execute()
        if not existing.data:
            raise HTTPException(404, "Song not found")
        

        update_data = song.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(400, "No update data provided")
            
        supabase.table("songs").update(update_data).eq("id", song_id).execute()
        return {"message": "Song updated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to update song {song_id}")
        raise HTTPException(500, "Failed to update song") from e

@router.delete("/songs/{song_id}")
async def delete_song(song_id: int):
    """Delete song"""
    try:

        existing = supabase.table("songs").select("*").eq("id", song_id).execute()
        if not existing.data:
            raise HTTPException(404, "Song not found")
            
        supabase.table("songs").delete().eq("id", song_id).execute()
        return {"message": "Song deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete song {song_id}")
        raise HTTPException(500, "Failed to delete song") from e

@router.get("/users/", response_model=List[dict])
async def get_all_users():
    """Get all users"""
    try:
        result = supabase.table("users").select("*").execute()
        if not hasattr(result, 'data'):
            raise HTTPException(500, "Invalid server response")
        return result.data or []
    except Exception as e:
        logger.exception("Failed to fetch users")
        raise HTTPException(500, "Failed to fetch users") from e

@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Delete user and their favorites"""
    try:

        existing = supabase.table("users").select("*").eq("id", user_id).execute()
        if not existing.data:
            raise HTTPException(404, "User not found")
            

        supabase.table("favorites").delete().eq("user_id", user_id).execute()
        

        supabase.table("users").delete().eq("id", user_id).execute()
        
        return {"message": "User deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete user {user_id}")
        raise HTTPException(500, "Failed to delete user") from e