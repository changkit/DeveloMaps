#!/usr/bin/python2.5
#
# Copyright 2011 Scott Reed

""" Main Event Handler for DeveloMaps """

__author__ = 'scott.ellison.reed@gmail.com'

import os
import os.path
import logging
from django.utils import simplejson
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from geo import geotypes
from geo.geomodel import GeoModel


# Display About.html
class ShowAbout(webapp.RequestHandler):
    def get(self):
        header = GetHeader("../templates/header.html")
        path = os.path.join(os.path.dirname(__file__), '../templates/about.html')
        self.response.out.write(template.render(path,
                                                { "header" : header }))


# Go to Feedback
class ShowFeedBack(webapp.RequestHandler):
    def get(self):
        header = GetHeader("../templates/header.html")
        path = os.path.join(os.path.dirname(__file__), '../templates/feedback.html')
        self.response.out.write(template.render(path,
                                                { "header" : header }))


# Send the add project form to the client
class SendProjForm(webapp.RequestHandler):
    def get(self):
        template_values = {}

        org_id = int(self.request.get('id'))

        # Check that id exists
        org = Organization.gql("where __key__ = KEY('Organization', %s)" %
                               self.request.get('id'))

        # Send header
        header = GetHeader("../templates/header_plain.html")
        template_values["header"] = header

        if not org:
            path = os.path.join(os.path.dirname(__file__), '../templates/bad_proj.html')
            self.response.out.write(template.render(path, template_values))
            return
    
        # Send org id
        template_values["org_id"] = org_id

        # Send tags
        tag_list = open("../text/tags.txt","r").read().splitlines()
        template_values["tag_list"] = tag_list

        path = os.path.join(os.path.dirname(__file__), '../templates/addproj.html')
        self.response.out.write(template.render(path, template_values))        


# Serve an Image
class ShowImage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'image/jpeg'
            
        query = Location.gql("where __key__ = KEY('Location',%s)" %
                             self.request.get("img_id"))
        oquery = Organization.gql("where __key__ = KEY('Organization',%s)" %
                                  self.request.get("img_id"))
        proj_info = query.get()
        org_info = oquery.get()
        if (not proj_info) and (not org_info):
            return

        img_type = self.request.get("img_type")

        if img_type == "logo":
            if org_info:
                self.SendPic(org_info.logo)
            else:
                self.SendPic(proj_info.org.logo)
        elif image_type == "img1":
            self.SendPic(this, proj_info.img1)
        elif image_type == "img2":
            self.SendPic(this, proj_info.img2)

    # If an image file exists, send it.
    # Otherwise, send "X No Image"
    def SendPic(self, picfile):
        if picfile:
            self.response.headers["Content-Type"] = "image/png"
            self.response.out.write(picfile)
        else:
            self.response.out.write("X No Image")


# Organization Storage Class
# Tracks information about Groups and their projects
class Organization(db.Model):
    name = db.StringProperty(multiline=False)
    description = db.StringProperty(multiline=True)
    logo = db.BlobProperty()
    img1 = db.BlobProperty()
    img2 = db.BlobProperty()
    tags = db.StringListProperty()
    email = db.EmailProperty()
    phone = db.PhoneNumberProperty()
    address = db.PostalAddressProperty()
    lat = db.FloatProperty()
    lng = db.FloatProperty()
    website = db.LinkProperty()
    admins = db.ListProperty(users.User)


# Location Storage Class
# Tracks latitude, longitude, project title, and
# project description.
#class Location(db.Model):
class Location(GeoModel):
    org = db.ReferenceProperty(Organization,
                               required=True,
                               collection_name='projects')
    lat = db.FloatProperty()
    lng = db.FloatProperty()
    title = db.StringProperty(multiline=False)
    description = db.StringProperty(multiline=True)
    logo = db.BlobProperty()
    img1 = db.BlobProperty()
    img2 = db.BlobProperty()
    tags = db.StringListProperty()
    email = db.EmailProperty()
    phone = db.PhoneNumberProperty()
    address = db.PostalAddressProperty()
    website = db.LinkProperty()


class UpdateProj(webapp.RequestHandler):
    def get(self):
        proj_id = int(self.request.get('proj_id'))
        proj_info = Location.gql("where __key__ = KEY('Location',%s)" %
                                 proj_id).get()
        if not proj_info:
            return

        header = GetHeader("../templates/header_plain.html")

        # Read in Tags
        tag_list = open("../text/tags.txt","r").read().splitlines()

        path = os.path.join(os.path.dirname(__file__), '../templates/update_proj.html')
        self.response.out.write(template.render(path,
                                                { "header" : header,
                                                  "proj" : proj_info,
                                                  "tag_list" : tag_list }))


class UpdateProjStore(webapp.RequestHandler):
    def post(self):
        proj_id = self.request.get('proj_id')
        if not proj_id:
            raise AssertionError
        proj_info = Location.gql("where __key__ = KEY('Location', %s)" %
                                 proj_id).get()

        if not proj_info:
            return

        proj_info.lat = float(self.request.get('lat'))
        proj_info.lng = float(self.request.get('lng'))

        proj_info.address = db.PostalAddress(self.request.get('proj_addr'))

        proj_info.title = self.request.get('proj_name')
        proj_info.description = self.request.get('proj_desc')

        img1 = self.request.get('img1')
        img2 = self.request.get('img2')

        if img1 != "":
            proj_info.img1 = db.Blob(img1)
        if img2 != "":
            proj_info.img2 = db.Blob(img2)

        # Read in Tags
        tag_list = open("../text/tags.txt","r").read().splitlines()
        for tag in tag_list:
            if self.request.get(tag) == "yes" and tag not in proj_info.tags:
                proj_info.tags.append(tag)

        try:
            proj_info.website = db.Link(self.request.get('proj_site'))
        except:
            proj_info.website = None
        
        try:
            proj_info.phone = db.PhoneNumber(self.request.get('proj_phone'))
        except:
            proj_info.phone = None

        try:
            proj_info.email = db.Email(self.request.get('proj_email'))
        except:
            proj_info.email = None

        proj_info.put()
        self.redirect('/account')


class UpdateOrg(webapp.RequestHandler):
    def get(self):
        header = GetHeader("../templates/header_plain.html")

        org_id = int(self.request.get('org_id'))
        org_info = Organization.gql("where __key__ = KEY('Organization',%s)" %
                                org_id).get()
        if not org_info:
            return
        path = os.path.join(os.path.dirname(__file__), '../templates/update_org.html')
        self.response.out.write(template.render(path,
                                                { "header" : header,
                                                  "org" : org_info }))


# Store a new Organization into the Organization class
class OrgStore(webapp.RequestHandler):
    def post(self):
        """
        org_id = int(self.request.get('org_id'))
        org = Organization.gql("where __key__ = KEY('Organization',%s)" %
                               org_id).get()

        """

        org = Organization();
        
        org.name = self.request.get('org_name')
        org.address = db.PostalAddress(self.request.get('addr'))

        org.lat = float(self.request.get('lat'))
        org.lng = float(self.request.get('lng'))

        org.description = self.request.get('content')
        
        # Store images as Blobs
        logo = self.request.get('logo')
        org.logo = db.Blob(logo)
        img1 = self.request.get('img1')
        img2 = self.request.get('img2')

        if img1 != "":
            org.img1 = db.Blob(img1)
        if img2 != "":
            org.img2 = db.Blob(img2)
            
        try:
            org.website = db.Link(self.request.get('site'))
        except:
            org.website = None
        
        try:
            org.phone = db.PhoneNumber(self.request.get('phone'))
        except:
            org.phone = None

        try:
            org.email = db.Email(self.request.get('email'))
        except:
            org.email = None

        # Assume user is logged in here!
        org.admins.append(users.get_current_user())
        org.put()
        self.redirect('/add_proj?id=%s' % org.key().id())


# Store a new Organization into the Organization class
class UpdateOrgStore(webapp.RequestHandler):
    def post(self):
        org_id = int(self.request.get('org_id'))
        org = Organization.gql("where __key__ = KEY('Organization',%s)" %
                               org_id).get()
        if not org:
            return

        org.name = self.request.get('org_name')
        org.address = db.PostalAddress(self.request.get('addr'))

        org.lat = float(self.request.get('lat'))
        org.lng = float(self.request.get('lng'))

        org.description = self.request.get('content')
        
        # Store images as Blobs
        logo = self.request.get('logo')
        org.logo = db.Blob(logo)
        img1 = self.request.get('img1')
        img2 = self.request.get('img2')

        if img1 != "":
            org.img1 = db.Blob(img1)
        if img2 != "":
            org.img2 = db.Blob(img2)
            
        try:
            org.website = db.Link(self.request.get('site'))
        except:
            org.website = None
        
        try:
            org.phone = db.PhoneNumber(self.request.get('phone'))
        except:
            org.phone = None

        try:
            org.email = db.Email(self.request.get('email'))
        except:
            org.email = None

        # Assume user is logged in here!
        org.admins.append(users.get_current_user())
        org.put()
        self.redirect('/account')


class ViewAccount(webapp.RequestHandler):
    def get(self):
        header = GetHeader("../templates/header_plain.html")
        user = users.get_current_user()
        orgs = Organization.all().filter('admins = ', user).fetch(100)

        template_values = {}
        template_values["header"] = header
        path = os.path.join(os.path.dirname(__file__), '../templates/organization.html')

        if not orgs:
            template_values["orgs"] = "<p>You have not registered any organizations</p>"

        c_values = { "user": user.nickname(),
                     "orgs" : orgs }

        content_template = os.path.join(os.path.dirname(__file__), '../templates/account_view.html')
        content = template.render(content_template,
                                  c_values)
        template_values["content"] = content
        self.response.out.write(template.render(path, template_values))
        self.response.out.write("</body></html>")


class ProjForm(webapp.RequestHandler):
    def get(self):
        org_id = int(self.request.get('id'))
        self.response.out.write("<html><body>")        
        path = os.path.join(os.path.dirname(__file__), '../templates/addproj.html')
        self.response.out.write(template.render(path, 
                                                {'org_id' : org_id }))
        self.response.out.write("</body></html>")


# Store a new row into the Location database.
class ProjStore(webapp.RequestHandler):
    def post(self):

        org_info = Organization.gql("where __key__ = KEY('Organization',%s)" %
                                    self.request.get('org_id')).get()
        if not org_info:
            # Org ID not valid
            return

        loc = Location(org=org_info)

        loc.lat = float(self.request.get('lat'))
        loc.lng = float(self.request.get('lng'))

        # For GeoModel
        loc.location = db.GeoPt(loc.lat, loc.lng)
        loc.update_location()

        loc.address = db.PostalAddress(self.request.get('proj_addr'))

        loc.title = self.request.get('proj_name')
        loc.description = self.request.get('proj_desc')

        img1 = self.request.get('img1')
        img2 = self.request.get('img2')

        if img1 != "":
            loc.img1 = db.Blob(img1)
        if img2 != "":
            loc.img2 = db.Blob(img2)

        # Read in Tags
        tag_list = open("../text/tags.txt","r").read().splitlines()
        for tag in tag_list:
            if self.request.get(tag) == "yes":
                loc.tags.append(tag)

        try:
            loc.website = db.Link(self.request.get('proj_site'))
        except:
            loc.website = None
        
        try:
            loc.phone = db.PhoneNumber(self.request.get('proj_phone'))
        except:
            loc.phone = None

        try:
            loc.email = db.Email(self.request.get('proj_email'))
        except:
            loc.email = None

        loc.put()
        self.redirect('/')


class ShowRegister(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url("/register"))

        header = GetHeader("../templates/header_plain.html")
        path = os.path.join(os.path.dirname(__file__), '../templates/register.html')
        self.response.out.write(template.render(path,
                                                {'header' : header}))        


# Send the Maps API on the client machine the information
# needed to construct a marker - lat, lng, and title.
# Bundle this information into a JSON object.
# JSON = Javascript Object Notation
class SendLoc(webapp.RequestHandler):
    def get(self):
        bbox = self.request.get("bounds").split(",")
        
        lat_min = bbox[0] # South
        lng_min = bbox[1] # West
        lat_max = bbox[2] # North
        lng_max = bbox[3] # East

        bounds = geotypes.Box(float(lat_max),
                              float(lng_max),
                              float(lat_min),
                              float(lng_min))

        #bounds = geotypes.Box(90.0, 180.0, -90.0, -180.0)

        base_query = Location.all()
        
        results = Location.bounding_box_fetch(
            base_query,
            bounds,
            max_results=100)

        #q = ("SELECT * from Location")
        #results = db.GqlQuery(q)

        loc_list = []
        for loc in results:
            loc_list.append({"lat" : loc.lat,
                             "lng" : loc.lng,
                             "title" : loc.title,
                             "tags" : loc.tags,
                             "id" : loc.key().id()})
        json_text = simplejson.dumps(loc_list)
        self.response.out.write(json_text)


# Givin a project ID (sent via XMLHttpRequest from
# the client's Maps API), respond with the corresponding
# row from the Location database table.
class SendData(webapp.RequestHandler):
    def get(self):
        key = int(self.request.get('key'))
        project_data = Location.get_by_id(key) 
        if not project_data:
            return

        if not project_data.phone:
            phone = ""
        else:
            phone = "phone: %s" % project_data.phone

        if not project_data.email:
            email = ""
        else:
            email = "email: %s" % project_data.email

        if not project_data.website:
            website = ""
        else:
            website = "website: %s" % project_data.website

        if((phone == "") and (email == "") and (website == "")):
            contact = ""
        else:
            contact = "<strong>Contact Information</strong><br/>"

        feed_params = {
            "org_name" : project_data.org.name,
            "proj_name" : project_data.title,
            "tags" : ", ".join(project_data.tags),
            "img_id" : project_data.key().id(),
            "description" : project_data.description,
            "contact_info" : contact,
            "website" : website,
            "phone" : phone,
            "email" : email,
            "proj_list" : ["None"]
        }

        path = os.path.join(os.path.dirname(__file__), '../templates/feed.html')
        self.response.out.write(template.render(path, feed_params))


# Return the text of the header
def GetHeader(hfile):
    header_values = {}
    log_text = ""
    user = users.get_current_user()
    if(user):
        log_text = ("<a href=\"%s\">Logout</a>" %
                    users.create_logout_url("/"))
        header_values['nickname'] = ("User: %s" %
                                     user.nickname())
        header_values['account'] = "href=\"/account\">Account"
    else:
        log_text = ("<a href=\"%s\">Login</a>" %
                    users.create_login_url("/"))
        header_values['nickname'] = ""
        header_values['account'] = "href=\"/register\">Register"
        
    header_values['log_text'] = log_text            
    hpath = os.path.join(os.path.dirname(__file__), hfile)
    return template.render(hpath, header_values)


# Main Request Handler. On 
class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if(not user):
            self.redirect("/splash")

        # Values used to qualify HTML
        template_values = {}

        #header = GetHeader("header.html")
        header = GetHeader("../templates/header_member.html")
        template_values["header"] = header
        template_values["footer"] = open("../templates/footer.html").read()

        # Get Tag List
        tag_list = open("../text/tags.txt","r").read().splitlines()
        template_values["tag_list"] = tag_list

        # Send out HTML
        self.response.out.write("<html>")
        path = os.path.join(os.path.dirname(__file__), '../templates/index.html')
        self.response.out.write(template.render(path, template_values))
        self.response.out.write("</body></html>")


class ShowAdmin(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), '../templates/admin.html')
        self.response.out.write(template.render(path, template_values))


class Image(db.Model):
    name = db.StringProperty()
    image = db.BlobProperty()


class AddImage(webapp.RequestHandler):
    def post(self):
        img = Image()
        img.name = self.request.get('name')
        img.image = db.Blob(self.request.get('pic'))
        img.put()
        self.redirect('/admin')


class ViewImage(webapp.RequestHandler):
    def get(self):
        name = self.request.get("name");
        img = Image.gql("where name = :1", name).get()
        if(img):
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(img.image)


class ViewSplash(webapp.RequestHandler):
    def get(self):
        header = GetHeader('../templates/header_splash.html')
        template_values = { "header" : header }
        path = os.path.join(os.path.dirname(__file__), '../templates/splash.html')
        self.response.out.write(template.render(path, template_values))
        

class FedSign(webapp.RequestHandler):
    def get(self):
        self.redirect(users.create_login_url('/'))


class Logout(webapp.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/'))


# /add, /getlocs, and /getdata each correspond to
# a request handler.
application = webapp.WSGIApplication([('/', MainPage),
                                      ('/getlocs', SendLoc),
                                      ('/getdata', SendData),
                                      ('/about', ShowAbout),
                                      ('/feedback', ShowFeedBack),
                                      ('/image', ShowImage),
                                      ('/register', ShowRegister),
                                      ('/add_org', OrgStore),
                                      ('/add_proj', SendProjForm),
                                      ('/store_proj', ProjStore),
                                      ('/account', ViewAccount),
                                      ('/update_proj', UpdateProj),
                                      ('/update_proj_store', UpdateProjStore),
                                      ('/update_org', UpdateOrg),
                                      ('/update_org_store', UpdateOrgStore),
                                      ('/admin', ShowAdmin),
                                      ('/add_image', AddImage),
                                      ('/view_image', ViewImage),
                                      ('/splash', ViewSplash),
                                      ('/fedsign', FedSign),
                                      ('/logout', Logout)],
                                     debug=('Development' in os.environ['SERVER_SOFTWARE']))


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
