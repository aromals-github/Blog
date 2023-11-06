from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import re

User = get_user_model

def create_jwt_token(user:User):
    refresh    = RefreshToken.for_user(user)
    token      = {"access":str(refresh.access_token),"refresh":str(refresh)}
    return token


def is_valid_phone_number(phone_number):
    '''
        this is to check if the user given phone number is valid or not (basic funtion)    
    '''
        
    pattern = r'^[789]\d{9}$'
    if re.match(pattern,phone_number):
        return True
    else:
        return False