from config import config
import jwt # used for encoding and decoding jwt tokens
from fastapi import HTTPException, Request # used to handle error handling
from datetime import datetime, timedelta # used to handle expiry time for tokens
from db import schemes

class Auth():
    SECRET_KEY = config("SECRET_KEY", cast=str)
    ALGORITHM = config("ALGORITHM", cast=str)
    ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)
    REFRESH_TOKEN_EXPIRE_HOURS = config("REFRESH_TOKEN_EXPIRE_HOURS", cast=int)

    @classmethod
    def get_access_token(self, username):
        payload = {
            'exp' : datetime.utcnow() + timedelta(days=0, minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat' : datetime.utcnow(),
            'scope': 'access_token',
            'sub' : username
        }
        return jwt.encode(
            payload, 
            self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )
    
    @classmethod
    def get_refresh_token(self, username):
        payload = {
            'exp' : datetime.utcnow() + timedelta(days=0, hours=self.REFRESH_TOKEN_EXPIRE_HOURS),
            'iat' : datetime.utcnow(),
            'scope': 'refresh_token',
            'sub' : username
        }
        return jwt.encode(
            payload, 
            self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )
    
    @classmethod
    def get_token_pair(self, username):
        Tokens = schemes.Tokens(access_token=self.get_access_token(username), refresh_token=self.get_refresh_token(username))
        return Tokens
    
    @classmethod
    def get_token_from_header(self, request: Request):
        token = request.headers.get("Authorization")
        if token is None:
            raise HTTPException(status_code=400, detail="Token missing")
        try:
            token = token.split(' ')[-1]
        except:
            raise HTTPException(status_code=400, detail="Invalid token")
        return token
    
    @classmethod
    def identify_access_token(self, token):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if (payload['scope'] == 'access_token'):
                return payload['sub']   
            raise HTTPException(status_code=401, detail='Scope for the token is invalid')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')
    
    @classmethod
    def identify_refresh_token(self, token):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if (payload['scope'] == 'refresh_token'):
                return payload['sub']   
            raise HTTPException(status_code=401, detail='Scope for the token is invalid')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')
    
    @classmethod
    def refresh_tokens(self, refresh_token):
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if (payload['scope'] == 'refresh_token'):
                username = payload['sub']
                Tokens = schemes.Tokens(access_token=self.get_access_token(username), refresh_token=self.get_refresh_token(username))
                return Tokens
            raise HTTPException(status_code=401, detail='Invalid scope for token')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Refresh token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid refresh token')
