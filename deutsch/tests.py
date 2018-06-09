from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.cache import cache
from django.conf import settings
import unittest
import re


def create_user(self, admin):
    self.username = "test_admin"
    self.password = User.objects.make_random_password()
    user, created = User.objects.get_or_create(username=self.username)
    user.set_password(self.password)
    user.first_name = "First"
    user.last_name = "Last"
    user.is_staff = admin
    user.is_superuser = admin
    user.is_active = True
    user.save()
    self.user = user


class TestAdminPanel_UnAuthorized(TestCase):
    def test_spider_admin_unauthorized(self):
        #print "\nTest: UnAuthorized Admin"
        create_user(self, False)
        self.client.login(username=self.username, password=self.password)
        admin_pages = [
            "/admin/",
            "/admin/auth/",
            "/admin/auth/group/",
            "/admin/auth/group/add/",
            "/admin/auth/user/",
            "/admin/auth/user/add/",
            "/admin/password_change/",
            "/admin/deklination/",
            "/admin/deklination/noun/",
            "/admin/deklination/genderquizscore/",
            "/admin/deklination/genderquizscore/132/change/",
            "/admin/logout/"
        ]
        for page in admin_pages:
            #print "UnAuth" + page
            resp = self.client.get(page, follow=True)
            assert resp.status_code == 200
            assert "<!DOCTYPE html" in resp.content
            assert "name=\"username\"" in resp.content


class TestAdminPanel_Authorized(TestCase):
    fixtures = ['testdb.json']

    def test_spider_admin(self):
        #print "\nTest: Authorized Admin"
        create_user(self, True)
        self.client.login(username=self.username, password=self.password)
        admin_pages = [
            "/admin/",
            "/admin/auth/",
            "/admin/auth/group/",
            "/admin/auth/group/add/",
            "/admin/auth/user/",
            "/admin/auth/user/add/",
            "/admin/password_change/",
            "/admin/deklination/",
            "/admin/deklination/noun/",
            "/admin/deklination/genderquizscore/",
            "/admin/deklination/genderquizscore/132/change/",
            "/admin/logout/"
        ]
        for page in admin_pages:
            #print "Auth" + page
            resp = self.client.get(page, follow=True)
            assert resp.status_code == 200
            assert "<!DOCTYPE html" in resp.content
            if page == "/admin/auth/user/add/":
                assert "name=\"username\"" in resp.content
            else:
                assert "name=\"username\"" not in resp.content

class TestHomePage_Guest(TestCase):
    def test_guest_homepage(self):
        #print "\nTest: Guest Homepage"
        resp = self.client.get("/", follow=True)
        assert "Sign Up" in resp.content
        assert "Sign In" in resp.content
        assert "Deklination</h4>" in resp.content
        assert "Konjugation</h4>" in resp.content
        assert "Wortstellung</h4>" in resp.content
        expected_regex = re.compile(r"<nav .+?Hello Guest.+?Sign Up.+?</nav>", re.MULTILINE|re.DOTALL)
        unittest.TestCase.assertRegexpMatches(self, resp.content, expected_regex)

class TestHomePage_Authorized(TestCase):
    def test_authorized_homepage(self):
        #print "\nTest: Authorized Homepage"
        create_user(self, False)
        self.client.login(username=self.username, password=self.password)
        resp = self.client.get("/", follow=True)
        assert "Sign Up" not in resp.content
        assert "Sign In" not in resp.content
        assert "Deklination</h4>" in resp.content
        assert "Konjugation</h4>" in resp.content
        assert "Wortstellung</h4>" in resp.content
        expected_regex = re.compile(r"<nav .+?Hello First Last.+?Sign Out.+?</nav>", re.MULTILINE|re.DOTALL)
        unittest.TestCase.assertRegexpMatches(self, resp.content, expected_regex)


