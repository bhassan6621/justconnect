from google.appengine.ext import ndb

class MUser(ndb.Model):
    UserID = ndb.StringProperty(required=True)
    UserEmail = ndb.StringProperty(required=True)

class Meet_Up(ndb.Model):
    dbMeetUpName = ndb.StringProperty(required=True)
    dbMeetUpDate = ndb.DateTimeProperty(required=True)
    dbMeetUpTime = ndb.TimeProperty(required=True)
    dbMeetUpPlace = ndb.StringProperty(required=True)
    dbMeetUpSpot = ndb.StringProperty(required=False)
    dbMeetUpFriends = ndb.StringProperty(required=False)

class MeetUpAndUser(ndb.Model):
    dbPeopleId = ndb.KeyProperty(MUser)
    dbMeetUpId = ndb.KeyProperty(Meet_Up)
