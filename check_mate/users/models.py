from django.db import models
from django_resized import ResizedImageField

# Create your models here.
class Roles(models.Model):

    '''This model will save the type of user our system will have apart from Admin'''
    #only for Instructor, and Student (Instructor id is 1 and Student is 2)

    role_id = models.IntegerField(null=False,blank=False,default = 0,unique = True)
    role_name = models.CharField(max_length = 30, null = False, blank = False)

    #This function will return the name of the role object when called.
    def __str__(self) -> str:
        return str(self.role_name)
    
    class Meta:
        #verbose name shows the name of the table according to the given one, otherwise
        #would have shown the name of the class on Admin panel. I gave both the name same.
        verbose_name = "Roles"
        #It will store the entities in the table in descending order
        ordering = ['-role_id']

class School_Users(models.Model):

    '''This model will hold all the users of our system other than admins'''
    #only for  Instructor and Student (Student can be TA)

    user_id = models.CharField(max_length = 20,null=False,blank=False,unique = True)
    user_role = models.ManyToManyField(Roles)  
    user_first_name = models.CharField(max_length = 50,null=True,blank=True)
    user_middle_name = models.CharField(max_length = 50,null=True,blank=True)
    user_last_name = models.CharField(max_length = 50,null=True,blank=True)
    user_email = models.EmailField(null = True,blank = True)
    user_phone_number = models.CharField(null=True,blank=True,max_length=16)
    user_profile_picture=models.ImageField(null=True,blank=True,upload_to='School_User/user_profile_pictures/')
    user_otp_verified = models.BooleanField(null=True,blank=True,default = False)

    #This function will return the id of the user object when called.
    def __str__(self) -> str:
        return str(self.user_id)
    
    class Meta:

        #gave a different name on the admin panel rather then setting class name on admin
        #as default
        verbose_name = "Registered Members"

class Course(models.Model):

    '''This model will hold the course details'''

    students = models.ManyToManyField(School_Users)
    instructor = models.ForeignKey(School_Users,on_delete=models.CASCADE,related_name = "instructor")
    teaching_assistant = models.ForeignKey(School_Users,on_delete=models.CASCADE,related_name = "teaching_assistant")
    course_code = models.CharField(max_length = 50,null=True,blank=True,default="")
    course_name = models.CharField(max_length = 200,null=True,blank=True,default="")
    course_section = models.IntegerField(null=True,blank=True,default = 0)
    course_picture = ResizedImageField(size=[500, 300], upload_to=f'Courses/{str(course_code)}/course_cover_picture/', blank=True, null=True)
    course_description = models.TextField(null=True,blank=True,default="")

    def __str__(self) -> str:
        return str(self.course_code)
    
    class Meta:

        verbose_name = "Courses"
