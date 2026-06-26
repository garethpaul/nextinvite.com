#!/usr/bin/env python
#
# Copyright 2013 NextInvite
#
import functools
import hashlib
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

try:
    from urllib.parse import parse_qs
except ImportError:
    from urlparse import parse_qs


LOCAL_PART_RE = re.compile(r"^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+$")
DOMAIN_LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
MAX_EMAIL_LENGTH = 254
MAX_LOCAL_PART_LENGTH = 64
MAX_SIGNUP_BODY_BYTES = 4096


def normalize_email(email):
    return email.strip().lower()


def signup_body_argument(request_body, name):
    try:
        if isinstance(request_body, bytes):
            request_body = request_body.decode("ascii")
        values = parse_qs(request_body, keep_blank_values=True).get(name, [])
    except (TypeError, UnicodeDecodeError, ValueError):
        return ""
    return values[-1] if values else ""


def has_signup_form_content_type(headers):
    content_type = headers.get("Content-Type", "")
    return content_type.split(";", 1)[0].strip().lower() == (
        "application/x-www-form-urlencoded"
    )


def signup_key_name(email):
    normalized_email = normalize_email(email)
    digest = hashlib.sha256(normalized_email.encode("utf-8")).hexdigest()
    return "signup-" + digest


def has_valid_email_shape(email):
    parts = email.split("@")
    if len(parts) != 2:
        return False

    local, domain = parts
    return bool(local and domain and "." in domain)


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


def has_valid_top_level_domain(email):
    parts = email.split("@", 1)
    if len(parts) != 2:
        return False

    labels = parts[1].split(".")
    if not labels:
        return False

    top_level_label = labels[-1]
    return len(top_level_label) >= 2 and any(
        character.isalpha()
        for character in top_level_label
    )


def is_valid_email(email):
    return bool(
        email
        and len(email) <= MAX_EMAIL_LENGTH
        and has_valid_email_shape(email)
        and has_valid_local_part(email)
        and has_valid_email_dots(email)
        and has_valid_domain_labels(email)
        and has_valid_top_level_domain(email)
    )


class SignUp(db.Model):
    """A single blog entry."""
    email = db.TextProperty()
    added= db.DateTimeProperty(auto_now_add=True)


def persist_signup(email, signup_model=SignUp):
	normalized_email = normalize_email(email)
	return signup_model.get_or_insert(
		signup_key_name(normalized_email),
		email=normalized_email,
	)


def xsrf_cookie_settings(environment=None):
	values = os.environ if environment is None else environment
	server_software = values.get("SERVER_SOFTWARE", "")
	is_development = server_software.startswith("Development")
	return {"secure": not is_development, "httponly": True}

class HomeHandler(base.BaseHandler):
	def get(self):
		self.render("home.html")
		
class SignUpHandler(base.BaseHandler):
	def post(self):
		request_body = self.request.body or ""
		if len(request_body) > MAX_SIGNUP_BODY_BYTES:
			self.send_error(413)
			return
		if not has_signup_form_content_type(self.request.headers):
			self.send_error(400)
			return

		email = normalize_email(signup_body_argument(request_body, 'email'))
		if not is_valid_email(email):
			self.send_error(400)
			return

		persist_signup(email)
		self.write("ok")

settings = {
    "blog_title": u"Next invite",
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "xsrf_cookies": True,
    "xsrf_cookie_kwargs": xsrf_cookie_settings(),
    "debug": False,
}
application = tornado.wsgi.WSGIApplication([
    (r"/", HomeHandler),
    (r"/signup", SignUpHandler),
], **settings)


def main():
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == "__main__":
    main()
