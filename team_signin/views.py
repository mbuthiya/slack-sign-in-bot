from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from slackclient import SlackClient                               
from signin import utils
from team_signin import utils
from team_signin.models import SignInRecords,SlackProfile

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings,'SLACK_BOT_USER_TOKEN', None)                                     
Client = SlackClient(SLACK_BOT_USER_TOKEN)




class Events(APIView):
    def __init__(self):
        self.commands_text='''\n
Valid Bot Commands
==============================================
1. sign in - get an authentication token
2. sign in time - review your sign in time today
3. records - get link to see roll call table
4. help - see this help message
---Note that your commands are recorded in a relational database
'''
        self.valid_commands={"sign in":self.signin,"sign in time":self.signin_time,"records":self.roll_table,"help":self.help_text}
        self.valid_commands_list=[i for i,x in tuple(self.valid_commands.items())]


    def post(self, request, *args, **kwargs):

        slack_message = request.data

        #check token
        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        #url verification for slack events api
        if slack_message.get('type') == 'url_verification':        
            return Response(data=slack_message,status=status.HTTP_200_OK) 

        if 'event' in slack_message:                              
            event_message = slack_message.get('event')  

            #store messages to prevent self reply
            state=utils.manage_message_event(event_message)
            if not state:
                return Response(status=status.HTTP_200_OK) 

            # dont reply to bot's own message
            if event_message.get('subtype') == 'bot_message':     
                return Response(status=status.HTTP_200_OK)   

            # process user's message
            self.user_id = event_message.get('user')  
            # a vuln may be here ):   
            self.user_text = str(event_message.get('text'))                     
            self.user_channel = event_message.get('channel')
            self.bot_text='' 

            #check if user is registered
            is_registered=self.check_user()
            if not is_registered:
                self.send_text()
                return Response(status=status.HTTP_200_OK)
                  
            if self.user_text.lower() not in self.valid_commands_list or self.user_text.lower()=="help":
                self.valid_commands['help']()
                return Response(status=status.HTTP_200_OK)
            
            #reply to command 
            else:
                self.valid_commands[self.user_text.lower()]()
                return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_200_OK)

    
    def check_user(self):
        is_registered=utils.check_user(self.user_id)
        if not is_registered:
            self.bot_text='you are not registed click this link to register {} no sign up form :simple_smile:'.format(settings.MYSITE_URL)
        return is_registered
        

    def send_text(self):
        Client.api_call(method='chat.postMessage',        
                            channel=self.user_channel,                  
                            text=self.bot_text)

    def signin(self):
        self.bot_text=process_tokens_requests(self.user_id)
        self.send_text()

    def signin_time(self):
        self.bot_text=request_time_in(self.user_id)
        self.send_text()
    
    def roll_table(self):
        self.bot_text='go to this url: {}'.format(settings.MYSITE_URL+'/table-records')
        self.send_text()

    def help_text(self):
        self.bot_text=self.commands_text
        self.send_text()
            
        


def process_tokens_requests(user_ids):
    #we assume we process requests from a single workspace only
    profile=SlackProfile.objects.get(user_sid=user_ids)
    c_time=utils.get_ctime_obj()
    state=SignInRecords.is_signed_in(str(c_time.strftime("%Y-%m-%d")),profile)
    
    if state:
        r=SignInRecords.get_record_by_date_profile(str(c_time.strftime("%Y-%m-%d")),profile)
        return "You are already signed in and authenticated"
    
    elif state==False:
        r=SignInRecords.get_record_by_date_profile(str(c_time.strftime("%Y-%m-%d")),profile)
        auth_token=r.token
        return 'Already sent an authentication token, click on this link to authenticate your physical location: {}'.format(settings.MYSITE_URL+'/auth-token/'+auth_token)
    elif state==None:
        auth_token=utils.generate_token()
        record=SignInRecords(profile=profile,
                            date_str=str(c_time.strftime("%Y-%m-%d")),
                            token=auth_token,
                            is_authenticated=False)
        record.save()
        
        return 'Click on this link to authenticate your physical location: {}'.format(settings.MYSITE_URL+'/auth-token/'+auth_token)
        
                
def request_time_in(user_ids):
    profile=SlackProfile.objects.get(user_sid=user_ids)
    c_time=utils.get_ctime_obj()
    state=SignInRecords.is_signed_in(str(c_time.strftime("%Y-%m-%d")),profile)

    if state:
        r=SignInRecords.get_record_by_date_profile(str(c_time.strftime("%Y-%m-%d")),profile)
        message='{}'.format(r.time_description,r.token)
        return message

    elif state==False:
        r=SignInRecords.get_record_by_date_profile(str(c_time.strftime("%Y-%m-%d")),profile)
        return 'Not authenticated yet, click on this link to authenticate your physical location: {}'.format(settings.MYSITE_URL+'/auth-token/'+auth_token)

    elif state==None:
        return "You do not have an authenticated token, please request for one"

        
        


    
