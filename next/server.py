#!/usr/bin/env python
#
# Copyright 2013 NextInvite
#
import functools
import markdown
import os
import os.path
import re
import tornado.web
import tornado.wsgi
import unicodedata
import wsgiref.handlers
from google.appengine.api import users
from google.appengine.ext import db
import base

class SignUp(db.Model):
    """A single blog entry."""
    email = db.TextProperty()
    added= db.DateTimeProperty(auto_now_add=True)

class HomeHandler(base.BaseHandler):
	def get(self):
		self.render("home.html")
		
class SignUpHandler(base.BaseHandler):
	def post(self):
		s = SignUp()
		s.email = self.get_argument('email')
		s.put()

settings = {
    "blog_title": u"Next invite",
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "xsrf_cookies": True,
    "debug": os.environ.get("SERVER_SOFTWARE", "").startswith("Development/"),
}
application = tornado.wsgi.WSGIApplication([
    (r"/", HomeHandler),
    (r"/signup", SignUpHandler),
], **settings)


def main():
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == "__main__":
    main()
