# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models         import User
from django.core.cache                  import cache
from django.conf                        import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test                        import TestCase, Client

import copy, datetime, math, os, pytz, re, time, unittest, unicodecsv as csv

from contextlib import contextmanager

from selenium.webdriver.firefox.webdriver           import WebDriver
from selenium.webdriver.support.ui                  import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

from .models import Noun, GenderQuizScore


def create_user(self, admin):
    self.username = "test_deklination"
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

def check_universal_items(resp):
    assert resp.status_code == 200
    assert "<!DOCTYPE html" in resp.content

def check_guest_items(self, resp):
    assert "Sign Up" in resp.content
    assert "Sign In" in resp.content
    expected_regex = re.compile(r"<nav .+?Hello Guest.+?Sign Up.+?</nav>", re.MULTILINE|re.DOTALL)
    unittest.TestCase.assertRegexpMatches(self, resp.content.encode('utf-8'), expected_regex)

def check_authorized_items(self, resp):
    assert "Sign Up" not in resp.content
    assert "Sign In" not in resp.content
    expected_regex = re.compile(r"<nav .+?Hello First Last.+?Sign Out.+?</nav>", re.MULTILINE|re.DOTALL)
    unittest.TestCase.assertRegexpMatches(self, resp.content.encode('utf-8'), expected_regex)


class TestDeklination(TestCase):
    def check_quiz_options(self, resp):
        assert "Identify Gender</h4>" in resp.content
        assert "Identify Case</h4>" in resp.content
        assert "Identify Declension</h4>" in resp.content

    def test_deklination_guest(self):
        resp = self.client.get("/deklination/", follow=True)
        check_universal_items(resp)
        check_guest_items(self, resp)
        self.check_quiz_options(resp)

    def test_deklination_authorized(self):
        create_user(self, False)
        self.client.login(username=self.username, password=self.password)
        resp = self.client.get("/deklination/", follow=True)
        check_universal_items(resp)
        check_authorized_items(self, resp)
        self.check_quiz_options(resp)

class TestGenderQuizEmptyDB(TestCase):
    def test_gender_quiz_empty(self):
        resp = self.client.get("/deklination/gender_quiz/", follow=True)
        

"""
http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
class wait_for_page_load(object):
    def __init__(self, browser):
        self.browser = browser

    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html')

    def page_has_loaded(self):
        new_page = self.browser.find_element_by_tag_name('html')
        return new_page.id != self.old_page.id

    def __exit__(self, *_):
        wait_for(self.page_has_loaded)


class testclass(...):
    with wait_for_page_load(self.selenium):
        self.selenium.find_element_by_link_text('my link').click()
"""


class SeleniumClass(StaticLiveServerTestCase):
    fixtures = ['testdb.json']
    serialized_rollback = True
    #available_apps = ['deklination']

    @contextmanager
    def wait_for_page_load(cls, timeout=30):
        old_page = cls.selenium.find_element_by_tag_name('html')
        yield
        WebDriverWait(cls.selenium, timeout).until(staleness_of(old_page))

    @classmethod
    def setUpClass(cls):
        super(SeleniumClass, cls).setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumClass, cls).tearDownClass()


class TestGenderQuiz(SeleniumClass):
    def test_guest_e2e(self):
        self.navigate_to_quiz()
        for i in range(6):
            self.verify_question_elements()
            self.select_correct_answer()
            self.verify_guest_correct_answer_elements()
            self.guest_next_question()
        for i in range(6):
            self.verify_question_elements()
            self.select_incorrect_answer()
            self.verify_guest_incorrect_answer_elements()
            self.guest_next_question()

    def test_authorized_e2e(self):
        create_user(self, False)
        self.navigate_to_quiz()
        self.login()

        # correct answer options
        for i in range(3):
            self.verify_question_elements()
            self.select_correct_answer()
            self.verify_authorized_correct_answer_elements()
            #print self.noun.noun
            self.authorized_next_question(i+3)                  # quality
            self.genderquizscore_verification(i+3, 0, 0, 2.5)   # quality, interval, consecutive_correct, easiness_factor

        # interval from 1 to 2, review overdue learned item
        self.make_last_due_and_review(5)

        # interval from 2 to SM2 update
        self.make_last_due_and_review(5)
        
        # incorrect answer options
        for i in range(3):
            self.verify_question_elements()
            self.select_incorrect_answer()
            self.verify_authorized_incorrect_answer_elements()
            self.authorized_next_question(i)                    # quality
            self.genderquizscore_verification(i, 0, 0, 2.5)     # quality, interval, consecutive_correct, easiness_factor

        # unlearned from more than five minutes ago
        self.make_last_due_and_review(0)

        # move easiness_factor below 1.3 to test min limit
        for i in range(3):
            self.make_last_due_and_review(0)


    def get_noun(self):
        noun_text = self.selenium.find_element_by_xpath('//a[@id="list-der-list"]').text.replace("Der ","").replace(" | ","|")
        self.noun = Noun.objects.get(noun = noun_text)
        
    def get_article(self):
        self.get_noun()
        if self.noun.gender == 'M':
            return "der"
        elif self.noun.gender == 'N':
            return "das"
        else:
            return "die"

    def get_incorrect_article(self):
        self.get_noun()
        if self.noun.gender == 'M':
            return "das"
        elif self.noun.gender == 'N':
            return "die"
        else:
            return "der"


    def navigate_to_quiz(self):
        #with self.wait_for_page_load(timeout=10):
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        with self.wait_for_page_load(timeout=10):
            self.selenium.find_element_by_xpath('//a[@id="begin_deklination"]').click()
        with self.wait_for_page_load(timeout=10):
        	self.selenium.find_element_by_xpath('//a[@id="begin_gender"]').click()
        
    def verify_question_elements(self):
        assert "Identify Gender" in self.selenium.find_element_by_xpath('//a[@id="list-title-list"]').text
        assert "Der " in self.selenium.find_element_by_xpath('//a[@id="list-der-list"]').text
        assert "Das " in self.selenium.find_element_by_xpath('//a[@id="list-das-list"]').text
        assert "Die " in self.selenium.find_element_by_xpath('//a[@id="list-die-list"]').text
        self.get_noun()
        assert self.noun.english.lower() in self.selenium.find_element_by_xpath('//div[@id="list-title"]/p[1]').text.lower().replace("<br /", "").replace("\n", "|")
        assert "Ranked #" + str(self.noun.rank) in self.selenium.find_element_by_xpath('//div[@id="list-title"]/p[2]').text

    def select_correct_answer(self):
        self.selenium.find_element_by_xpath('//a[@id="list-' + self.get_article() + '-list"]').click()
        time.sleep(0.25)

    def select_incorrect_answer(self):
       	self.selenium.find_element_by_xpath('//a[@id="list-' + self.get_incorrect_article() + '-list"]').click()
        time.sleep(0.25)

    def verify_guest_correct_answer_elements(self):
        base_xpath = '//div[@id="list-' + self.get_article() + '"]'
        assert "show" in self.selenium.find_element_by_xpath(base_xpath).get_attribute('class')
        assert "active" in self.selenium.find_element_by_xpath(base_xpath).get_attribute('class')
        assert "Correct!" in self.selenium.find_element_by_xpath(base_xpath + '/h2').text
        assert self.get_article().title() + " " + self.noun.noun.replace("|"," | ") in self.selenium.find_element_by_xpath(base_xpath + '/p').text
        assert "Next Question" in self.selenium.find_element_by_xpath(base_xpath + '/a[@role="button"]').text

    def verify_guest_incorrect_answer_elements(self):
        base_xpath = '//div[@id="list-' + self.get_incorrect_article() + '"]'
        assert "show" in self.selenium.find_element_by_xpath(base_xpath).get_attribute('class')
        assert "active" in self.selenium.find_element_by_xpath(base_xpath).get_attribute('class')
        assert "Incorrect!" in self.selenium.find_element_by_xpath(base_xpath + '/h2').text
        assert self.get_article().title() + " " + self.noun.noun.replace("|"," | ") in self.selenium.find_element_by_xpath(base_xpath + '/p').text
        assert "Next Question" in self.selenium.find_element_by_xpath(base_xpath + '/a[@role="button"]').text

    def verify_authorized_correct_answer_elements(self):
        base_xpath = '//div[@id="list-' + self.get_article() + '"]'
        assert "show" in self.selenium.find_element_by_xpath(base_xpath).get_attribute('class')
        assert "active" in self.selenium.find_element_by_xpath(base_xpath).get_attribute('class')
        assert "Correct!" in self.selenium.find_element_by_xpath(base_xpath + '/h2').text
        assert self.get_article().title() + " " + self.noun.noun.replace("|"," | ") in self.selenium.find_element_by_xpath(base_xpath + '/p').text
        assert "How easy was that?" in self.selenium.find_element_by_xpath(base_xpath + '/p').text
        assert self.noun.noun in self.selenium.find_element_by_xpath(base_xpath + '/form/input[@name="noun"]').get_attribute('value')
        assert self.noun.english in self.selenium.find_element_by_xpath(base_xpath + '/form/input[@name="english"]').get_attribute('value')
        assert "Difficult" in self.selenium.find_element_by_xpath(base_xpath + '/form/button[@value="3"]').text
        assert "Hesitated" in self.selenium.find_element_by_xpath(base_xpath + '/form/button[@value="4"]').text
        assert "No Problem" in self.selenium.find_element_by_xpath(base_xpath + '/form/button[@value="5"]').text

    def verify_authorized_incorrect_answer_elements(self):
        base_xpath = '//div[@id="list-' + self.get_incorrect_article() + '"]'
        assert "show" in self.selenium.find_element_by_xpath(base_xpath).get_attribute('class')
        assert "active" in self.selenium.find_element_by_xpath(base_xpath).get_attribute('class')
        assert "Incorrect!" in self.selenium.find_element_by_xpath(base_xpath + '/h2').text
        assert self.get_article().title() + " " + self.noun.noun.replace("|"," | ") in self.selenium.find_element_by_xpath(base_xpath + '/p').text
        assert "Do you remember it now?" in self.selenium.find_element_by_xpath(base_xpath + '/p').text
        assert self.noun.noun in self.selenium.find_element_by_xpath(base_xpath + '/form/input[@name="noun"]').get_attribute('value')
        assert self.noun.english in self.selenium.find_element_by_xpath(base_xpath + '/form/input[@name="english"]').get_attribute('value')
        assert "Not Really" in self.selenium.find_element_by_xpath(base_xpath + '/form/button[@value="0"]').text
        assert "Maybe" in self.selenium.find_element_by_xpath(base_xpath + '/form/button[@value="1"]').text
        assert "Definitely" in self.selenium.find_element_by_xpath(base_xpath + '/form/button[@value="2"]').text

    def guest_next_question(self):
        with self.wait_for_page_load(timeout=10):
        	self.selenium.find_element_by_xpath('//div[@id="nav-tabContent"]/div[@class="tab-pane fade active show"]/a[@role="button"]').click()
        
    def authorized_next_question(self, quality):
        #print str(quality) + " : " + self.noun.noun
        if quality < 3:
            base_xpath = '//div[@id="list-' + self.get_incorrect_article() + '"]'
        else:
            base_xpath = '//div[@id="list-' + self.get_article() + '"]'
        with self.wait_for_page_load(timeout=10):
        	self.selenium.find_element_by_xpath(base_xpath + '/form/button[@value="' + str(quality) + '"]').click()

    def genderquizscore_verification(self, quality, interval, consecutive_correct, easiness_factor):
        genderquizscore = GenderQuizScore.objects.get(noun__noun = self.noun.noun, user__username = self.username)
        if quality < 3:
            self.assertEqual(genderquizscore.interval, 0)
            self.assertEqual(genderquizscore.consecutive_correct, 0)
            assert genderquizscore.review_date <= datetime.datetime.now(pytz.timezone('UTC')) + datetime.timedelta(seconds=5)
            self.assertEqual(round(genderquizscore.easiness_factor, 2), round(max(1.3, easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))), 2))
        else:
            if interval == 0:
                self.assertEqual(genderquizscore.interval, 1)
            elif interval == 1:
                self.assertEqual(genderquizscore.interval, 6)
            else:
                self.assertEqual(genderquizscore.interval, math.ceil(interval * easiness_factor))
            self.assertEqual(genderquizscore.consecutive_correct, consecutive_correct + 1)
            assert genderquizscore.review_date <= datetime.datetime.now(pytz.timezone('UTC')) + datetime.timedelta(seconds=5)
            self.assertEqual(round(genderquizscore.easiness_factor, 2), round(easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)), 2))

    def login(self):
        with self.wait_for_page_load(timeout=10):
        	self.selenium.find_element_by_xpath('//div[@class="jumbotron pb-2"]/div/p/a[contains(text(), "Sign In")]').click()
           #self.selenium.find_element_by_xpath('//div[@class="jumbotron pb-2"]/div/p/a[text()="Sign In"]').click()
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(self.username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(self.password)
        with self.wait_for_page_load(timeout=10):
        	self.selenium.find_element_by_xpath('//button[@value="login"]').click()

    def make_card_due(self, noun_text, username):
        genderquizscore = GenderQuizScore.objects.get(noun__noun = noun_text, user__username = username)
        if genderquizscore.consecutive_correct > 0:
            GenderQuizScore.objects.filter(noun__noun = noun_text, user__username = username).update(
                review_date = datetime.datetime.now(pytz.timezone('UTC')) - datetime.timedelta(days=genderquizscore.interval) - datetime.timedelta(minutes=1))
        else:
            GenderQuizScore.objects.filter(noun__noun = noun_text, user__username = username).update(
                review_date = datetime.datetime.now(pytz.timezone('UTC')) - datetime.timedelta(minutes=6))

    def make_last_due_and_review(self, quality):
        self.scopy = copy.copy(GenderQuizScore.objects.get(noun__noun = self.noun.noun, user__username = self.username))
        self.make_card_due(self.scopy.noun.noun, self.username)
        self.select_correct_answer()            # this question is not important
        self.authorized_next_question(5)        # this question is not important
        self.get_noun()
        assert self.noun.noun == self.scopy.noun.noun
        if quality < 3:
            self.select_incorrect_answer()
        else:
            self.select_correct_answer()
        self.authorized_next_question(quality)  # this questino is the one we care about
        self.genderquizscore_verification(quality, self.scopy.interval, self.scopy.consecutive_correct, self.scopy.easiness_factor)


