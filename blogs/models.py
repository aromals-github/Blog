from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser,BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from datetime import date
from django.utils.translation import gettext_lazy as _
from .utils import is_valid_phone_number
from django.conf import settings



class UserManager(BaseUserManager):
    
    use_in_migrations = True
    
    def create_user(self,phone_number,password):

        valid_status = is_valid_phone_number(phone_number)
        
        if valid_status:
            if not phone_number:
                raise ValueError("User requires a phone number to create an account.")
            # if not username :
            #     raise ValueError("User must have unique username.")
            
            user = self.model(
                phone_number = phone_number,
            )
            user.set_password(password)
            user.save()
            return user
        else:
            raise ValueError("Invalid Number!!!")
    

    def create_superuser(self,phone_number,password):

        valid_status = is_valid_phone_number(phone_number=phone_number)
        if valid_status:
            user    =  self.create_user(
                                        phone_number = phone_number,
                                        password = password,
                                )
            
            user.is_admin       = True
            user.is_staff       = True
            user.is_superuser   = True
            user.save()
            return user
        else:
            raise ValueError("Invalid Number!!!")

    

    
class Users(AbstractBaseUser,PermissionsMixin):

    email           = models.EmailField(_('email'), unique = True, blank= True, null=True)
    first_name      = models.CharField(_('first_name'), max_length = 100, blank = True)
    last_name       = models.CharField(_('last_name'), max_length = 100, blank = True)
    username        = models.CharField(_('nickname'), max_length = 100, unique= True,null=True,blank=True)
    phone_number    = models.CharField(max_length=30, blank=True, null=True,unique=True)
    address         = models.CharField(_('user address'), max_length=500, blank=True)
    city            = models.CharField(_('user city'), max_length=250, blank=True)
    state           = models.CharField(_('user state'), max_length=250, blank=True)
    created_on      = models.DateTimeField(_('user created on'), auto_now_add=True)
    updated_on      = models.DateTimeField(_('user updated on'), auto_now=True)
    date_of_birth   = models.DateField("Date in ( MM/DD/YYYY )",null= True,blank=False,auto_now=False,auto_now_add=False)

    is_superuser    = models.BooleanField(default=False)
    is_staff        = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=True)
    is_admin        = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD      = 'phone_number'
    # REQUIRED_FIELDS     = ['username']
    
    def has_perm(self,perm,obj = None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
    def __str__(self):
        return self.get_full_name()
    
    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name
    
    def age(self):

        '''
        Returns the age of the user
        '''
        
        today  = date.today() 
        try:
            birthday = self.date_of_birth.replace(year=today.year)
        except ValueError:
            birthday = self.date_of_birth.replace(year=today.year,day=self.DOB.day-1)
    
        if birthday > today:
            return today.year - self.date_of_birth.year - 1
        else :
            return today.year -self.date_of_birth.year
    class Meta:
        verbose_name_plural = "Users"


class Blogs(models.Model):

    blog_owner      = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    blog_question   = models.CharField(max_length=1024, blank=True, null=True,unique=True)
    blog_likes      = models.IntegerField(null=True,blank=True,default=0)
    created_on      = models.DateTimeField(_('user created on'), auto_now_add=True)

    def __str__(self):
        return self.blog_question
    
    class Meta:
        verbose_name_plural = "Blogs"

class BlogsDetails(models.Model):

    blog        = models.ForeignKey(Blogs,null=True,blank=True,on_delete=models.SET_NULL)
    blog_answer = models.CharField(blank=True,max_length=1024,blank =True)
    reader     = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    created_on  = models.DateTimeField(_('user created on'), auto_now_add=True)
    like        = models.BooleanField(null=True,blank=True,default=False)

    def __str__(self):
        return self.blog
    class Meta:
        verbose_name_plural = "Blog Details"