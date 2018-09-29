import webapp2
import models
from models import Meet_Up
from models import MUser
from models import MeetUpAndUser
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
import datetime
import time
import jinja2
import os

jinja_current_dir = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class LogInHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    # If the user is logged in...
    if user:
      email_address = user.nickname()
      mUser = MUser.get_by_id(user.user_id())
      signout_link_html = '<a href="%s">sign out</a>' % (
          users.create_logout_url('/'))
      # If the user has previously been to our site, we greet them!
      if mUser:
        afterlogin_html = jinja_current_dir.get_template("templates/afterlogin.html")
        the_dict= {
            "SignOut": users.create_logout_url('/')
        }
        self.response.write(afterlogin_html.render(the_dict))

      # If the user hasn't been to our site, we ask them to sign up
      #this store's users first and last name in database
      else:
          userBoolean = False
          for userr in models.MUser.query().fetch():
              if userr.UserID == user.user_id():
                  userBoolean = True

          if userBoolean == False:
              mUser = MUser(
                UserID = user.user_id(),
                UserEmail = user.nickname()
                 )
              mUser.put()

          self.response.write(''' Welcome to our site, %s! <br> ''' % (email_address))
          afterlogin_html = jinja_current_dir.get_template("templates/afterlogin.html")
          the_dict= {
             "SignOut": users.create_logout_url('/')
             }
          self.response.write(afterlogin_html.render(the_dict))
    else:
      linkToSignIn_template = jinja_current_dir.get_template("templates/linkToSignIn.html")
      var_dict = {
        "signin_Url": users.create_login_url('/')
      }
      self.response.write(linkToSignIn_template.render(var_dict))


  def post(self):
    user = users.get_current_user()
    if not user:
      # You shouldn't be able to get here without being logged in
      self.error(500)
      return
    mUser = MUser(
        UserID = user.user_id(),
        UserEmail = user.nickname()
        )
    mUser.put()
    # meetUp_html = jinja_current_dir.get_template("templates/meetUp.html")
    # self.response.write(meetUp_html.render())

class AfterLoginHandler(webapp2.RequestHandler):
    def get(self):
        afterlogin_html = jinja_current_dir.get_template("templates/afterlogin.html")
        self.response.write(afterlogin_html.render())
    def post(self):
        pass

class upComingMeetUpHandler(webapp2.RequestHandler):
    def get(self):
        upComingMeetUp_html = jinja_current_dir.get_template("templates/upComing_MeetUp.html")
        MeetUpAndPeople_list = models.MeetUpAndUser.query().fetch()
        user_key = users.get_current_user().user_id()
        user_list = models.MUser.query().fetch()
        MeetUp_list = models.Meet_Up.query().fetch()
        current_date = datetime.datetime.now()

        upComingMU_list = []
        for meetUpAndPeople in MeetUpAndPeople_list:
            for user in user_list:
                if user.UserID == user_key:
                    if user.key == meetUpAndPeople.dbPeopleId:
                        for meetUp in MeetUp_list:
                            if meetUp.key == meetUpAndPeople.dbMeetUpId:
                                if meetUp.dbMeetUpDate > current_date:
                                    upComingMU_list.append(meetUp)
                                elif meetUp.dbMeetUpDate == current_date:
                                    pass
        UpComingList_len = len(upComingMU_list)

        my_dict = {'upComingMU_list': upComingMU_list,
                    'UpComingList_len' : UpComingList_len}
        self.response.write(upComingMeetUp_html.render(my_dict))
    def post(self):
        pass

class MeetUpHandler(webapp2.RequestHandler):
    def get(self):
        meetUp_html = jinja_current_dir.get_template("templates/meetUp.html")
        SignOut = users.create_logout_url('/')
        my_dict = {'SignOut': SignOut}
        self.response.write(meetUp_html.render(my_dict))
    def post(self):
        meetUp_html = jinja_current_dir.get_template("templates/meetUp.html")
        meetUpTitle = self.request.get('meetUp_name')
        meetUpDate = datetime.datetime.strptime(self.request.get('meetUp_date'), "%Y-%m-%d")
        meetUpTime = datetime.datetime.strptime(self.request.get('meetUp_time'), "%H:%M").time()
        meetUpPlace = self.request.get('meetUp_place')
        meetUp_Friends = self.request.get('meetUp_Friends')

        meetUp = Meet_Up(dbMeetUpName = meetUpTitle, dbMeetUpDate = meetUpDate, dbMeetUpTime = meetUpTime, dbMeetUpPlace= meetUpPlace, dbMeetUpFriends = meetUp_Friends)
        meetUpKey = meetUp.put()

        users_list =  models.MUser.query().fetch()
        User_key = "null"
        for user in users_list:
            if user.UserID == users.get_current_user().user_id():
                User_key = user.key

        content = []
        if ', ' not in meetUp_Friends:
            content.append(meetUp_Friends)
        if ', ' in meetUp_Friends:
            content = meetUp_Friends.split(', ')

        # self.response.write(content)
        self.response.write(content)

        Friend_key = "null"
        for person in content:
            for Fuser in users_list:
                if Fuser.UserEmail == person:
                    Friend_key = Fuser.key
                    meetUp_and_User = MeetUpAndUser(dbPeopleId = Friend_key, dbMeetUpId = meetUpKey)
                    meetUp_and_User.put()

        meetUp_and_User = MeetUpAndUser(dbPeopleId= User_key , dbMeetUpId= meetUpKey)
        meetUp_and_User.put()

        self.redirect('/upComingMeetUp')

class UpcomingEventHandler(webapp2.RequestHandler):
    def get(self):
        upcomingEvent_html = jinja_current_dir.get_template("templates/upComingMU.html")
        MeetUpAndPeople_list = models.MeetUpAndUser.query().fetch()
        user_key = users.get_current_user().user_id()
        user_list = models.MUser.query().fetch()
        MeetUp_list = models.Meet_Up.query().fetch()
        current_date = datetime.datetime.now()
        # my_dict = {
        #     'MeetUpAndPeople_list': MeetUpAndPeople_list,
        #     'user_key': user_key,
        #     'MeetUp_list': MeetUp_list,
        #     'user_list' : user_list,
        #     'current_date' : current_date
        # }

        upComingMU_list = []
        previousMU_list = []

        for meetUpAndPeople in MeetUpAndPeople_list:
            for user in user_list:
                if user.UserID == user_key:
                    if user.key == meetUpAndPeople.dbPeopleId:
                        for meetUp in MeetUp_list:
                            if meetUp.key == meetUpAndPeople.dbMeetUpId:
                                if meetUp.dbMeetUpDate > current_date:
                                    upComingMU_list.append(meetUp)
                                elif meetUp.dbMeetUpDate == current_date:
                                    pass
                                else:
                                    previousMU_list.append(meetUp)

        UpComingList_len = len(upComingMU_list)
        PreviousList_Len = len(previousMU_list)

        my_dict = {'upComingMU_list': upComingMU_list,
                    'previousMU_list': previousMU_list,
                    'PreviousList_Len' : PreviousList_Len,
                    'UpComingList_len' : UpComingList_len
                    }
        self.response.write(upcomingEvent_html.render(my_dict))

class PreviousMeetUp_Handler(webapp2.RequestHandler):
    def get(self):
        previousMeetUp_html = jinja_current_dir.get_template("templates/previousMeetUp.html")
        MeetUpAndPeople_list = models.MeetUpAndUser.query().fetch()
        user_key = users.get_current_user().user_id()
        user_list = models.MUser.query().fetch()
        MeetUp_list = models.Meet_Up.query().fetch()
        current_date = datetime.datetime.now()

        previousMU_list = []
        for meetUpAndPeople in MeetUpAndPeople_list:
            for user in user_list:
                if user.UserID == user_key:
                    if user.key == meetUpAndPeople.dbPeopleId:
                        for meetUp in MeetUp_list:
                            if meetUp.key == meetUpAndPeople.dbMeetUpId:
                                if meetUp.dbMeetUpDate < current_date:
                                    previousMU_list.append(meetUp)

        PreviousList_Len = len(previousMU_list)

        my_dict = {'previousMU_list': previousMU_list,
                    'PreviousList_Len' : PreviousList_Len}
        self.response.write(previousMeetUp_html.render(my_dict))


    def post(self):
        pass

class theMeetHandler(webapp2.RequestHandler):
    def get(self):
        theMeet_html = jinja_current_dir.get_template("templates/theMeet.html")
        self.response.write(theMeet_html.render())


app = webapp2.WSGIApplication([
  ('/', LogInHandler),
  ('/afterLogin', AfterLoginHandler),
  ('/upComingMeetUp', upComingMeetUpHandler),
  ('/theMeet', theMeetHandler),
  ('/previousMeetUp', PreviousMeetUp_Handler),
  ('/meetUp', MeetUpHandler),
  ('/upComing', UpcomingEventHandler)
], debug=True)
