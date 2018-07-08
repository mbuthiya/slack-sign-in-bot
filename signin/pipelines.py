from django.contrib.auth.models import User
from team_signin.models import SlackProfile
from django.shortcuts import redirect
from datetime import datetime
from signin.settings import PYTZ_ZONE
import pytz
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

'''
{'ok': True, 'access_token': 'xoxp-391861030260-392023068708-392463225890-ccdc989736b908d5af4e18fb89d1f5e9',
 'scope': 'identity.basic,identity.email',
  'user': {'name': 'dev hax', 'id': 'UBJ0P20LU', 'email': 'd3veloper.hax@gmail.com'},
   'team': {'id': 'TBHRB0W7N'}}
'''


def create_user(api_data):
    user=User(username=api_data['team']['id']+':'+api_data['user']['id'],
        email=api_data['user']['email'])
    #this is only to allow us to use django auth backend otherwise it has no effect on security
    user.set_password(api_data['access_token'])
    user.save()
    tz=pytz.timezone(settings.PYTZ_ZONE)
    c_time=datetime.now(tz)
    profile=SlackProfile(user=user,
                            team_id=api_data['team']['id'],
                            user_sid=api_data['user']['id'],
                            username=api_data['user']['name'],
                            access_token=api_data['access_token'],
                            date_created=c_time.date(),
                            last_login=c_time.date())
    profile.save()
    return user,profile

def register_user(request, api_data):
    if api_data['ok']:
        try:
            user=User.objects.get(
                username=api_data['team']['id']+':'+api_data['user']['id']
                )
            profile=SlackProfile.objects.get(user_sid=api_data['user']['id'])
            tz=pytz.timezone(settings.PYTZ_ZONE)
            c_time=datetime.now(tz)
            profile.last_login=c_time.date()
            profile.save()
            request.created_user = user

        except ObjectDoesNotExist:
            user,profile=create_user(api_data)
            request.user = user

    return request,api_data


def debug_oauth_request(request, api_data):
    print(api_data)
    return request, api_data