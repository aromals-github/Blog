
from rest_framework import  serializers
from .models import *
from rest_framework.authtoken.models import Token


class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model           = Users
        fields          = ("phone_number",'password')
        extra_kwargs    = {'passwords': {'write_only':True, 'required':True}}

    def create(self,validated_data):
        user            = Users.objects.create_user(**validated_data)
        return user
    
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model           = Users
        fields          = (
                            "first_name",
                            "lastname",
                            "phone_number",
                            "address",
                            "city",
                            "state",
                            "date_of_birth"
                           )
class BlogSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Blogs
        fields = ['blog_owner', 'blog_question', 'blog_likes']

class BlogsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogsDetails
        fields = '__all__'