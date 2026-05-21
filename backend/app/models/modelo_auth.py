from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"
    username:      str
    user_id:       int
    role:          str

class RefreshTokenResponse(BaseModel):
    refresh_token: str