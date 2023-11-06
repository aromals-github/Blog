from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken,OutstandingToken
from rest_framework.request import Request
from django.contrib.auth import authenticate


from rest_framework.request import Request
from .models import *
from .serializers import *
from .utils import create_jwt_token,is_valid_phone_number
from .constants import DEFAULT_EXCEPTION_MSG
class UserResgistration(APIView):

    '''
        This class is used for registering new users . 
    '''

    permission_classes = []

    def post(self,request:Request):
        try:
            phone_number  = request.data.get("phone_number")

            if phone_number:
                valid = is_valid_phone_number(phone_number)

                if valid:
                    user_data           = request.data
                    serializer          = RegistrationSerializer(data = user_data)

                    if serializer.is_valid():
                        serializer.save()
                        context = "Your account is created successfully, Please login to continue."
                        return Response(
                                {"msg":context},
                                status=status.HTTP_201_CREATED
                            )
                    else:
                        return Response(
                            {"error":serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                return Response(
                        {"msg":"invalid phone number"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response({
                    "msg": "Phone number should be given"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"msg":DEFAULT_EXCEPTION_MSG},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserLogin(APIView):

    '''
        This class is used to login  users to their accounts.
    '''

    permission_classes = []

    def post(self,request:Request):

        try:
            phone_number        = request.data.get('phone_number')
            password            = request.data.get('password')

            if not (phone_number or password):
                return Response(
                    {'msg':"phone number and password is must for login"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user        = authenticate(phone_number=phone_number,password=password)
            
            if user is not None:
                token       = create_jwt_token(user=user)
                context     =  ({
                    "msg":"succesfull",
                    "tokens":token
                })
                return Response(
                    context,status=status.HTTP_200_OK
                    )
            else:
                check_PhoneNumber= Users.objects.filter(phone_number=phone_number).first()
                if not check_PhoneNumber:
                    return Response(
                        {"msg":"invalid phone number"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                return Response(
                    {"msg":"incorrect password"},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            
        except Exception as e:
            return Response(
                {"msg":DEFAULT_EXCEPTION_MSG},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
            
class UserLogout(APIView):

    '''
        This class is used to Logout users from there account.
        If in data 'all' is passed all refresh tokens for all devices will be invalid i.e;
        user will be logged out from all devices.
    '''
    
    authentication_classes = (JWTAuthentication,)
    permission_classes     = (IsAuthenticated,)

    def post(self, request,*args, **kwargs):

        try:
            if self.request.data.get('all'):
                token: OutstandingToken

                for token in OutstandingToken.objects.filter(user=request.user):
                    _, _ = BlacklistedToken.objects.get_or_create(token=token)
                return Response(
                    {"msg": "all refresh tokens blacklisted"},
                    status.HTTP_400_BAD_REQUEST
                    )
            refresh_token = self.request.data.get('refresh')

            if not refresh_token:
                return Response(
                    {"msg": "refresh token not found"},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            
            token = RefreshToken(token=refresh_token)
            token.blacklist()
            return Response(
                {"msg": "user logged out "},
                status=status.HTTP_200_OK
                )
        
        except Exception as e:
            return Response(
                {"msg":DEFAULT_EXCEPTION_MSG},
                status=status.HTTP_400_BAD_REQUEST
                )


class PostBlog(APIView):

    '''
    class useed to create a blog post and 
    view the post
    '''

    authentication_classes = (JWTAuthentication,)
    permission_classes     = (IsAuthenticated,)

    def post(self,request):

        try :
            user =  request.user
            question = request.data.get("question")
            data = request.data
            if not question:
                return Response({
                    "msg": "a question must be entered"
                },status=status.HTTP_400_BAD_REQUEST)
            serializer = BlogSerializer(blog_owner=user,data=data)

            if serializer.is_valid():
                # Valid data, create a new blog post
                serializer.save(blog_owner=user)
                return Response({
                    "msg": "Blog post created successfully."
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "errors":serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response(
                {
                    "msg":DEFAULT_EXCEPTION_MSG},
                status=status.HTTP_400_BAD_REQUEST
                )
    
    def get(self,request):

        try :
            only_blog = request.query_params.get("id")
            if only_blog:
                blog = Blogs.objects.filter(pk=only_blog).first()
                if blog:
                    serializer = BlogSerializer(blog)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "msg":"no blog found with the given ID"
                    },status=status.HTTP_400_BAD_REQUEST)
            else:
                blogs = Blogs.objects.all().order_by("-created_on")
                serializer = BlogSerializer(blogs,many=True)
        except:
            return Response(
                {
                    "msg":DEFAULT_EXCEPTION_MSG},
                status=status.HTTP_400_BAD_REQUEST
                )
        
class BlogLikes(APIView):
    '''
    class used to like the post and unlike
    '''
    authentication_classes = (JWTAuthentication,)
    permission_classes     = (IsAuthenticated,)


    def post(self,request,pk):

        try:
            blog = Blogs.objects.filter(pk=pk).first()
            blog_details = BlogsDetails.objects.get_or_create(blog=blog,reader=request.user)
            like = request.query_params.get("like")

            if blog:
                if like == "1":
                    if blog_details.like == False :
                        present_likes = blog.blog_likes
                        blog.blog_likes = present_likes + 1
                        blog_details.like = True
                        blog.save()
                        blog_details.save()
                        return Response({
                            "msg":"Post liked"
                        },status=status.HTTP_200_OK)
                    else:
                        return Response({
                            "msg": "you already liked the post"
                        },status=status.HTTP_200_OK)
                elif like == "0":
                    if blog_details:
                        present_likes = blog.blog_likes
                        blog.blog_likes = present_likes - 1
                        blog_details.like = False
                        blog.save()
                        blog_details.save()
                        return Response(
                            {"msg":"you dislike the post"
                             },status =status.HTTP_200_OK)
                    return Response(status=200)
            return Response({
                "msg": "No blog found with given ID"
            },status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(
                {
                    "msg":DEFAULT_EXCEPTION_MSG},
                status=status.HTTP_400_BAD_REQUEST
                )
        

class BlogAnswer(APIView):
    
    ''''
    class used to write an answer to thw blog post
    '''

    authentication_classes = (JWTAuthentication,)
    permission_classes     = (IsAuthenticated,)

    def post(self,request,pk):

        try:
            blog = Blogs.objects.filter(pk=pk).first()
            blog_details = BlogsDetails.objects.get_or_create(blog=blog,reader=request.user).first()
            answer = request.query_params.get("answer")
            if blog_details:
                blog_details.answer = answer
                blog_details.save()
                return Response({
                    "msg":"answer is recorded"
                },status=status.HTTP_200_OK)

        except:
            return Response(
                {
                    "msg":DEFAULT_EXCEPTION_MSG},
                status=status.HTTP_400_BAD_REQUEST
                )
    
    def get(self,request,pk):

        try:
            blog = Blogs.objects.filter(pk=pk).first().order_by("-created_on")
            blog_details = BlogsDetails.objects.filter(blog=blog)
            serializer_one = BlogSerializer(blog)
            serializer_two = BlogsDetailsSerializer(blog_details,many=True)
            context = {
                "blog":serializer_one.data,
                "blogs details" :serializer_two.data
            }
            return Response({
                "data":context
            },status=status.HTTP_200_OK)
        except:
            return Response(
                {
                    "msg":DEFAULT_EXCEPTION_MSG},
                status=status.HTTP_400_BAD_REQUEST
                )

