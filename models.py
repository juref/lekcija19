from google.appengine.ext import ndb

class Guests(ndb.Model):
    name = ndb.StringProperty()
    surname = ndb.StringProperty()
    email = ndb.StringProperty()
    message = ndb.TextProperty()
    createDate = ndb.DateTimeProperty(auto_now_add=True)