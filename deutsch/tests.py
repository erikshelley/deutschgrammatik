# -*- coding: utf-8 -*-
#from __future__ import unicode_literals

from django.conf                                    import settings
from django.contrib.staticfiles.testing             import StaticLiveServerTestCase
from django.contrib.auth.models                     import User
from django.core.cache                              import cache
from django.test                                    import TestCase, Client
from django.test.client                             import RequestFactory

import copy, datetime, math, os, pytz, re, time, unittest, unicodecsv as csv

from contextlib                                     import contextmanager

from selenium.webdriver.firefox.webdriver           import WebDriver
from selenium.webdriver.support.ui                  import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

from views                                          import error_400, error_403, error_404, error_500

class TestUserManagement:
    def create_user(self, username, password, admin):
        user, created = User.objects.get_or_create(username=username)
        user.set_password(password)
        user.first_name = 'First'
        user.last_name = 'Last'
        user.is_staff = admin
        user.is_superuser = admin
        user.is_active = True
        user.save()

class SeleniumClass(StaticLiveServerTestCase):
    fixtures = ['testdb.json']
    serialized_rollback = True

    @contextmanager
    def wait_for_page_load(cls, timeout=30):
        old_page = cls.selenium.find_element_by_tag_name('html')
        yield
        WebDriverWait(cls.selenium, timeout).until(staleness_of(old_page))

    @classmethod
    def setUpClass(cls):
        super(SeleniumClass, cls).setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(1)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumClass, cls).tearDownClass()


class TestAdminPanel_UnAuthorized(TestCase):
    def test_spider_admin_unauthorized(self):
        print '\nTest: UnAuthorized Admin'
        username = 'test_spider_admin_unauthorized'
        password = User.objects.make_random_password()
        tum = TestUserManagement()
        tum.create_user(username, password, False)
        self.client.login(username=username, password=password)
        admin_pages = [
            '/admin/',
            '/admin/auth/',
            '/admin/auth/group/',
            '/admin/auth/group/add/',
            '/admin/auth/user/',
            '/admin/auth/user/add/',
            '/admin/password_change/',
            '/admin/deklination/',
            '/admin/deklination/noun/',
            '/admin/deklination/noun/846/',
            '/admin/deklination/nounrule/',
            '/admin/deklination/nounrule/4256/',
            '/admin/deklination/rule/',
            '/admin/deklination/rule/1/',
            '/admin/deklination/genderreviewscore/',
            '/admin/deklination/genderreviewscore/12/',
            '/admin/deklination/genderreviewscore/16/',
            '/admin/progress/progress/',
            '/admin/progress/progress/16/',
            '/admin/logout/'
        ]
        for page in admin_pages:
            #print 'UnAuth' + page
            resp = self.client.get(page, follow=True)
            assert resp.status_code == 200
            assert '<!DOCTYPE html' in resp.content
            assert 'name="username"' in resp.content


class TestAdminPanel_Authorized(TestCase):
    fixtures = ['testdb.json']

    def test_spider_admin(self):
        print '\nTest: Authorized Admin'
        username = 'test_spider_admin'
        password = User.objects.make_random_password()
        tum = TestUserManagement()
        tum.create_user(username, password, True)
        self.client.login(username=username, password=password)
        admin_pages = [
            '/admin/',
            '/admin/auth/',
            '/admin/auth/group/',
            '/admin/auth/group/add/',
            '/admin/auth/user/',
            '/admin/auth/user/add/',
            '/admin/password_change/',
            '/admin/deklination/',
            '/admin/deklination/noun/',
            '/admin/deklination/noun/846/',
            '/admin/deklination/nounrule/',
            '/admin/deklination/nounrule/4256/',
            '/admin/deklination/rule/',
            '/admin/deklination/rule/1/',
            '/admin/deklination/genderreviewscore/',
            '/admin/deklination/genderreviewscore/12/',
            '/admin/deklination/genderreviewscore/16/',
            '/admin/progress/progress/',
            '/admin/progress/progress/16/',
            '/admin/logout/'
        ]
        for page in admin_pages:
            #print 'Auth' + page
            resp = self.client.get(page, follow=True)
            assert resp.status_code == 200
            assert '<!DOCTYPE html' in resp.content
            if page == '/admin/auth/user/add/':
                assert 'name="username"' in resp.content
            else:
                assert 'name="username"' not in resp.content

class TestHomePage_Guest(TestCase):
    def test_guest_homepage(self):
        print '\nTest: Guest Homepage'
        resp = self.client.get('/', follow=True)
        assert 'Sign Up' in resp.content
        assert 'Sign In' in resp.content
        assert 'Deklination</strong>' in resp.content
        assert 'Konjugation</strong>' in resp.content
        assert 'Wortstellung</strong>' in resp.content
        expected_regex = re.compile(r'<nav .+?Hello Guest.+?Sign Up.+?</nav>', re.MULTILINE|re.DOTALL)
        unittest.TestCase.assertRegexpMatches(self, resp.content, expected_regex)

class TestHomePage_Authorized(TestCase):
    def test_authorized_homepage(self):
        print '\nTest: Authorized Homepage'
        username = 'test_authorized_homepage'
        password = User.objects.make_random_password()
        tum = TestUserManagement()
        tum.create_user(username, password, False)
        self.client.login(username=username, password=password)
        resp = self.client.get('/', follow=True)
        assert 'Sign Up' not in resp.content
        assert 'Sign In' not in resp.content
        assert 'Deklination</strong>' in resp.content
        assert 'Konjugation</strong>' in resp.content
        assert 'Wortstellung</strong>' in resp.content
        expected_regex = re.compile(r'<nav .+?Hello First.+?Sign Out.+?</nav>', re.MULTILINE|re.DOTALL)
        unittest.TestCase.assertRegexpMatches(self, resp.content, expected_regex)

class TestErrorPages(TestCase):
    def test_error_handlers(self):
        print '\nTest: Error Handlers'
        factory = RequestFactory()
        request = factory.get('/')
        response = error_400(request)
        self.assertEqual(response.status_code, 400)
        response = error_403(request)
        self.assertEqual(response.status_code, 403)
        response = error_404(request)
        self.assertEqual(response.status_code, 404)
        response = error_500(request)
        self.assertEqual(response.status_code, 500)
        

class TestRegistration(SeleniumClass):
    def test_valid_signup(self):
        print '\nUI Test: Valid Registration'
        self.signup('username1', 'firstname', 'lastname', 'email@example.com', 'testPass!', 'testPass!')
        self.validate_valid_signup('firstname', 'firstname lastname')
        self.signout()
        self.signup('username2', '', 'lastname', 'email@example.com', 'testPass!', 'testPass!')
        self.validate_valid_signup('username2', 'lastname')
        self.signout()
        self.signup('username3', 'firstname', '', 'email@example.com', 'testPass!', 'testPass!')
        self.validate_valid_signup('firstname', 'firstname')
        self.signout()
        self.signup('username4', '', '', 'email@example.com', 'testPass!', 'testPass!')
        self.validate_valid_signup('username4', 'username4')
        self.signout()
        self.signup('username5', '', '', '', 'testPass!', 'testPass!')
        self.validate_valid_signup('username5', 'username5')

    def test_invalid_signup(self):
        print '\nUI Test: Invalid Registration'
        self.signup('username1', 'firstname', 'lastname', 'email@example.com', 'testPass!', 'testPass!')
        self.validate_valid_signup('firstname', 'firstname lastname')
        self.signout()
        self.signup('username1', '', 'lastname', 'email@example.com', 'testPass!', 'testPass!')
        self.validate_signup_error('id_username_error', 'A user with that username already exists.', 'username1', '', 'lastname', 'email@example.com')
        #self.signup('username2', 'firstname', '', 'email@example.com', 'password', 'password')
        #self.validate_signup_error('id_password2_error', 'This password is too common.', 'username2', 'firstname', '', 'email@example.com')
        self.signup('username2', 'firstname', '', 'email@example.com', 'testPass!', 'wordpass')
        self.validate_signup_error('id_password2_error', "The two password fields didn't match.", 'username2', 'firstname', '', 'email@example.com')
        self.signup('username1', 'firstname', 'lastname', '', 'testPass!', 'wordpass')
        self.validate_signup_error('id_username_error', 'A user with that username already exists.', 'username1', 'firstname', 'lastname', '')
        self.validate_signup_error('id_password2_error', "The two password fields didn't match.", 'username1', 'firstname', 'lastname', '')


    def signup(self, username, firstname, lastname, email, password1, password2):
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        with self.wait_for_page_load(timeout=10):
            self.selenium.find_element_by_xpath('//main//a[contains(text(), "Sign Up")]').click()
        self.selenium.find_element_by_xpath('//input[@id="id_username"]').send_keys(username)
        self.selenium.find_element_by_xpath('//input[@id="id_first_name"]').send_keys(firstname)
        self.selenium.find_element_by_xpath('//input[@id="id_last_name"]').send_keys(lastname)
        self.selenium.find_element_by_xpath('//input[@id="id_email"]').send_keys(email)
        self.selenium.find_element_by_xpath('//input[@id="id_password1"]').send_keys(password1)
        self.selenium.find_element_by_xpath('//input[@id="id_password2"]').send_keys(password2)
        with self.wait_for_page_load(timeout=10):
            self.selenium.find_element_by_xpath('//button[@id="signup"]').click()

    def signout(self):
        self.selenium.find_element_by_xpath('//nav//div[@class="dropdown"]').click()
        time.sleep(0.25)
        self.selenium.find_element_by_xpath('//nav//a[contains(text(), "Sign Out")]').click()
        
    def validate_valid_signup(self, top_nav_name, lead_name):
        assert top_nav_name in self.selenium.find_element_by_xpath('//a[@id="navbarDropdownMenuLink"]').text
        assert lead_name in self.selenium.find_element_by_xpath('//main/div/div/p/small').text

    def validate_signup_error(self, input_id, error_text, username, firstname, lastname, email):
        assert 'There were error(s) with your submission.' in self.selenium.find_element_by_xpath('//div[@id="form_error"]').text
        assert 'text-danger' in self.selenium.find_element_by_xpath('//div[@id="form_error"]').get_attribute('class')
        assert error_text in self.selenium.find_element_by_xpath('//div[@id="' + input_id + '"]').text
        assert username in self.selenium.find_element_by_xpath('//input[@id="id_username"]').get_attribute('value')
        assert firstname in self.selenium.find_element_by_xpath('//input[@id="id_first_name"]').get_attribute('value')
        assert lastname in self.selenium.find_element_by_xpath('//input[@id="id_last_name"]').get_attribute('value')
        assert email in self.selenium.find_element_by_xpath('//input[@id="id_email"]').get_attribute('value')

