from django.db import models


# Create your models here

#This model will look for any error made during the system and record those to easily debug those
class System_Errors(models.Model):
    
    date_time=models.DateTimeField(null=False,blank=False)
    error_name=models.CharField(null=False,blank=False,max_length=500)
    error_occured_for = models.TextField(null=True,blank=True)
    error_traceback=models.TextField(null=False,blank=False,max_length=3000)
    error_fix_status=models.BooleanField(null=False,blank=False,default=False)
    
    class Meta:
        verbose_name="System Errors"

    def __str__(self) -> str:
        return str(self.date_time)