#!/usr/bin/env python
# -*- coding: utf-8 -*-

# encoding=utf8
import sys
import os
import jinja2
import webapp2
from models import Guests
from HTMLParser import HTMLParser

reload(sys)
sys.setdefaultencoding('utf8')


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("index.html")

    def post(self):
        name = self.request.get("name")
        surname = self.request.get("surname")
        email = self.request.get("email")
        message = strip_tags(self.request.get("message"))

        if not name:
            name = "neznanec"
        if not surname:
            surname = "neznanec"
        if not message:
            params = {"notice": "Sporočilo je obvezno!", "class": "warning"}
        else:
            guests = Guests(name=name, surname=surname, email=email, message=message)
            guests.put()

            params = {"notice": "Uspešno ste vnesli sporočilo", "classConfirm": "confirm"}

            return self.render_template("conformation.html", params=params)

        return self.render_template("index.html", params=params)


class GuestsListHandler(BaseHandler):
    def get(self):
        list = Guests.query().fetch()

        params = {"list": list}

        return self.render_template("list.html", params=params)


class MessageHandler(BaseHandler):
    def get(self, guest_id):
        single_guest = Guests.get_by_id(int(guest_id))

        params = {"single_guest": single_guest}

        return self.render_template("message.html", params=params)

    def post(self, guest_id):
        name = self.request.get("name")
        surname = self.request.get("surname")
        email = self.request.get("email")
        message = strip_tags(self.request.get("message"))

        single_guest = Guests.get_by_id(int(guest_id))

        single_guest.name = name
        single_guest.surname = surname
        single_guest.email = email
        single_guest.message = message

        if not single_guest.name:
            single_guest.name = "neznanec"
        if not single_guest.surname:
            single_guest.surname = "neznanec"
        if not single_guest.message:
            params = {"notice": "Sporočilo je obvezno!", "class": "warning"}
        else:
            single_guest.put()
            params = {"notice": "Zapis je bil popravljen!",  "classConfirm": "confirm"}

        return self.render_template("conformation.html", params=params)


class ReadHandler(BaseHandler):
    def get(self, guest_id):
        single_guest = Guests.get_by_id(int(guest_id))

        params = {"single_guest": single_guest}

        return self.render_template("read.html", params=params)


class DeleteMessageHandler(BaseHandler):
    def get(self, guest_id):
        single_guest = Guests.get_by_id(int(guest_id))
        params = {"single_guest": single_guest}
        return self.render_template("delete.html", params=params)

    def post(self, guest_id):
        single_guest = Guests.get_by_id(int(guest_id))
        single_guest.key.delete()

        params = {"notice": "Sporočilo je izbrisano!", "class": "warning"}

        return self.render_template("conformation.html", params=params)


class ConformationHandler(BaseHandler):
    def get(self):
        return self.render_template("conformation.html")


app = webapp2.WSGIApplication([
    webapp2.Route('/list', MainHandler),
    webapp2.Route('/', GuestsListHandler),
    webapp2.Route('/message/<guest_id:\d+>', MessageHandler),
    webapp2.Route('/read/<guest_id:\d+>', ReadHandler),
    webapp2.Route('/delete/<guest_id:\d+>', DeleteMessageHandler),
    webapp2.Route('/confirm', ConformationHandler),
], debug=True)
