import os
from binascii import hexlify
import pytz
from datetime import datetime
from django.conf import settings
from team_signin.models import Eventmesssage,SignInRecords,SlackProfile

def generate_token():
    return hexlify(os.urandom(int(settings.TOKEN_LENGTH/2))).decode('utf-8')

def get_ctime_obj():
    tz=pytz.timezone(settings.PYTZ_ZONE)
    c_time=datetime.now(tz)
    return c_time

def manage_message_event(event_message):
    state=Eventmesssage.validate_unique(event_message.get('client_msg_id'))
    if state:
        event_ms=Eventmesssage(client_msg_id=event_message.get('client_msg_id'),
                        user=event_message.get('user'),
                        text=event_message.get('text'),
                        channel=event_message.get('channel'),
                        event_ts=event_message.get('event')
        )
        event_ms.save()
        return state
    return state

def valid_token(profile,token):
    c_time=get_ctime_obj()
    r=SignInRecords.objects.filter(profile=profile,token=token,date_str=str(c_time.strftime("%Y-%m-%d")))
    return r if r else False

def check_user(user_id):
    return SlackProfile.is_user(user_id)
