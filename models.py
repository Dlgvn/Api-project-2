from pydantic import BaseModel
from typing import Optional

class SongCreate(BaseModel):
    artist_name: str
    track_name: str
    track_id: str
    year: int
    genre: str

class SongUpdate(BaseModel):
    artist_name: Optional[str] = None
    track_name: Optional[str] = None
    track_id: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

class SongResponse(BaseModel):
    id: int
    artist_name: str
    track_name: str
    track_id: str
    year: int
    genre: str

class FavoriteCreate(BaseModel):
    song_id: int

class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    song_id: int
    song_details: SongResponse