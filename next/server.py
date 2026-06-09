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


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
LOCAL_PART_RE = re.compile(r"^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+$")
DOMAIN_LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
MAX_EMAIL_LENGTH = 254
MAX_LOCAL_PART_LENGTH = 64


def normalize_email(email):
    return email.strip().lower()


def has_valid_email_dots(email):
    parts = email.split("@", 1)
    if len(parts) != 2:
        return False

    local, domain = parts
    if local.startswith(".") or local.endswith(".") or ".." in local:
        return False

    return all(label for label in domain.split(".")) and ".." not in domain


def has_valid_local_part(email):
    parts = email.split("@", 1)
    if len(parts) != 2:
        return False

    local = parts[0]
    return bool(
        local
        and len(local) <= MAX_LOCAL_PART_LENGTH
        and LOCAL_PART_RE.match(local)
    )


def has_valid_domain_labels(email):
    parts = email.split("@", 1)
    if len(parts) != 2:
        return False

    labels = parts[1].split(".")
    return all(
        label
        and len(label) <= 63
        and not label.startswith("-")
        and not label.endswith("-")
        and DOMAIN_LABEL_RE.match(label)
        for label in labels
    )


def is_valid_email(email):
    return bool(
        email
        and len(email) <= MAX_EMAIL_LENGTH
        and EMAIL_RE.match(email)
        and has_valid_local_part(email)
        and has_valid_email_dots(email)
        and has_valid_domain_labels(email)
    )


class SignUp(db.Model):
    """A single blog entry."""
    email = db.TextProperty()
    added= db.DateTimeProperty(auto_now_add=True)

class HomeHandler(base.BaseHandler):
	def get(self):
		self.render("home.html")
		
class SignUpHandler(base.BaseHandler):
	def post(self):
		email = normalize_email(self.get_argument('email', ''))
		if not is_valid_email(email):
			self.set_status(400)
			self.write("invalid email")
			return

		s = SignUp()
		s.email = email
		s.put()
		self.write("ok")

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
