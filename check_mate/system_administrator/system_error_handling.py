from django.contrib.auth .models import User
import logging
from datetime import datetime
from .models import System_Errors
from check_mate.settings import DEBUG
from django.core.mail import send_mail,EmailMultiAlternatives
from django.conf import settings

class ErrorHandling:

    '''This class is for saving any error that has occured in our system so that we can easiy
        know what error occured at what time'''
    
    logger=logging.getLogger(__name__)
    
    def save_system_errors(user,error_name,error_traceback):

        '''This function saves the error in database when occurs and notifies devs if debugging is False'''
        try:
            new_error=System_Errors.objects.create(
                date_time=datetime.now(),
                error_name=error_name,
                error_traceback=error_traceback,
                error_occured_for = user
            )
            new_error.save()
            if(DEBUG):
                pass
            else:
                #send email to devlopers
                pass        
        except:
            ErrorHandling.logger.error("An error occurred for user, {user} , at {datetime}".format(datetime=datetime.now()), exc_info=True)
