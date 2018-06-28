# -*- coding: utf-8 -*-
from __future__                                     import unicode_literals

from django.contrib.auth.models                     import User
from django.core.cache                              import cache
from django.conf                                    import settings
from django.contrib.staticfiles.testing             import StaticLiveServerTestCase
from django.test                                    import TestCase, Client

import copy, datetime, math, os, pytz, re, time, unittest, unicodecsv as csv

from contextlib                                     import contextmanager

from selenium.webdriver.firefox.webdriver           import WebDriver
from selenium.webdriver.support.ui                  import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support                     import expected_conditions

from .models                                        import Noun, Rule, GenderReviewScore
from deutsch.tests                                  import TestUserManagement, SeleniumClass


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
    expected_regex = re.compile(r"<nav .+?Hello First.+?Sign Out.+?</nav>", re.MULTILINE|re.DOTALL)
    unittest.TestCase.assertRegexpMatches(self, resp.content.encode('utf-8'), expected_regex)


class TestDeklination(TestCase):
    def check_quiz_options(self, resp):
        assert "Identify Gender</h5>" in resp.content
        assert "Identify Case</h5>" in resp.content
        assert "Identify Declension</h5>" in resp.content

    def test_deklination_guest(self):
        print '\nTest: Deklination Guest'
        resp = self.client.get("/deklination/", follow=True)
        check_universal_items(resp)
        check_guest_items(self, resp)
        self.check_quiz_options(resp)

    def test_deklination_authorized(self):
        print '\nTest: Deklination Authorized'
        username = 'test_deklination_authorized'
        password = User.objects.make_random_password()
        tum = TestUserManagement()
        tum.create_user(username, password, False)
        self.client.login(username=username, password=password)
        resp = self.client.get("/deklination/", follow=True)
        check_universal_items(resp)
        check_authorized_items(self, resp)
        self.check_quiz_options(resp)

class TestGenderQuizEmptyDB(TestCase):
    def test_gender_quiz_empty(self):
        print '\nTest: Gender Quiz Empty DB'
        resp = self.client.get("/deklination/gender_quiz/", follow=True)
        

class TestGenderQuiz(SeleniumClass):
    def test_guest_e2e(self):
        print '\nUI Test: Gender Quiz Guest E2E'
        tda = TestDeklinationActions(self.selenium, self.live_server_url, self.wait_for_page_load)
        tda.navigate_to_quiz()
        for i in range(6):
            tda.verify_question_elements()
            tda.select_correct_answer()
            tda.verify_guest_correct_answer_elements()
            tda.guest_next_question()
        for i in range(6):
            tda.verify_question_elements()
            tda.select_incorrect_answer()
            tda.verify_guest_incorrect_answer_elements()
            tda.guest_next_question()
        
        # look for non-existant alert (test coverage)
        tda.accept_alert()


    def test_authorized_e2e(self):
        print '\nUI Test: Gender Quiz Authorized E2E'
        username = 'test_authorized_e2e'
        password = User.objects.make_random_password()
        tum = TestUserManagement()
        tum.create_user(username, password, False)
        tda = TestDeklinationActions(self.selenium, self.live_server_url, self.wait_for_page_load)
        tda.navigate_to_quiz()
        tda.login(username, password)

        # correct answer options - do five to get to the first noun without a rule (Jahr)
        for i in range(5):
            tda.verify_question_elements()
            tda.select_correct_answer()
            tda.verify_authorized_correct_answer_elements()
            tda.authorized_next_question(i%3+3)                    # quality
            tda.genderreviewscore_verification(i%3+3, 0, 0, 2.5)   # quality, interval, consecutive_correct, easiness_factor

        # try refreshing page
        tda.selenium.refresh()
        tda.accept_alert()

        # interval from 1 to 2, review overdue learned item
        tda.make_last_due_and_review(5)

        # interval from 2 to SM2 update
        tda.make_last_due_and_review(5)

        # bring status from short to long 
        tda.make_last_due_and_review(5)

        # bring status from long to short
        # hit path reviewing noun with interval = 0
        tda.make_last_due_and_review(0)
        tda.make_last_due_and_review(0)
        
        # incorrect answer options
        for i in range(3):
            tda.verify_question_elements()
            tda.select_incorrect_answer()
            tda.verify_authorized_incorrect_answer_elements()
            tda.authorized_next_question(i)                    # quality
            tda.genderreviewscore_verification(i, 0, 0, 2.5)   # quality, interval, consecutive_correct, easiness_factor

        # try refreshing page
        tda.selenium.refresh()
        tda.accept_alert()

        # unlearned from more than five minutes ago
        tda.make_last_due_and_review(0)

        # move easiness_factor below 1.3 to test min limit
        for i in range(3):
            tda.make_last_due_and_review(0)

        # hit path reviewing rule with interval > 0
        tda.make_last_due_and_review(5)
        tda.make_last_due_and_review(5)

        # something like 29 reviews are needed to get to first rule exception (code coverage)
        for i in range(22):
            tda.select_correct_answer()
            tda.authorized_next_question(4)                    # quality


class TestDeklinationActions:
    def __init__(self, selenium, live_server_url, wait_for_page_load):
        self.selenium = selenium
        self.live_server_url = live_server_url
        self.wait_for_page_load = wait_for_page_load

    def get_rule(self):
        elements = self.selenium.find_elements_by_xpath('//form//input[@name="rule"]')
        self.is_rule = False
        if len(elements) > 0:
            rule_text = self.selenium.find_element_by_xpath('//form//input[@name="rule"]').get_attribute('value')
            self.rule = Rule.objects.get(short_name = rule_text)
            self.is_rule = True

    def get_noun(self):
        noun_text = self.selenium.find_element_by_xpath('//a[@id="der-tab"]/div/div[2]').get_attribute('innerHTML').replace("Der ","")
        gender_text = self.selenium.find_element_by_xpath('//div[h5[@class="text-success"]]/ul/li/strong').get_attribute('innerHTML').replace(" " + noun_text,"")
        if gender_text == 'Der':
            gender = 'M'
        elif gender_text == 'Das':
            gender = 'N'
        else:
            gender = 'F'
        self.noun = Noun.objects.get(noun = noun_text, gender = gender)
        self.get_rule()
        
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
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        with self.wait_for_page_load(timeout=10):
            self.selenium.find_element_by_xpath('//a[@id="begin_deklination"]').click()
        with self.wait_for_page_load(timeout=10):
        	self.selenium.find_element_by_xpath('//a[@id="begin_gender"]').click()
        
    def verify_question_elements(self):
        self.get_noun()
        assert self.noun.noun in self.selenium.find_element_by_xpath('//h4[@id="list-title-list"]').get_attribute('innerHTML')
        assert "Der " in self.selenium.find_element_by_xpath('//a[@id="der-tab"]').get_attribute('innerHTML')
        assert "Das " in self.selenium.find_element_by_xpath('//a[@id="das-tab"]').get_attribute('innerHTML')
        assert "Die " in self.selenium.find_element_by_xpath('//a[@id="die-tab"]').get_attribute('innerHTML')

    def select_correct_answer(self):
        self.selenium.find_element_by_xpath('//a[@id="' + self.get_article() + '-tab"]').click()
        time.sleep(0.25)

    def select_incorrect_answer(self):
       	self.selenium.find_element_by_xpath('//a[@id="' + self.get_incorrect_article() + '-tab"]').click()
        time.sleep(0.25)

    def verify_guest_correct_answer_elements(self):
        base_xpath = '//div[@id="' + self.get_article() + '"]'
        assert "show" in self.selenium.find_element_by_xpath(base_xpath).get_attribute('class')
        assert "Correct!" in self.selenium.find_element_by_xpath(base_xpath + '//h5').get_attribute('innerHTML')
        assert self.get_article().title() + " " + self.noun.noun.replace("|"," | ") in self.selenium.find_element_by_xpath(base_xpath + '//li').get_attribute('innerHTML')
        assert "Next Question" in self.selenium.find_element_by_xpath(base_xpath + '//a[@role="button"]').get_attribute('innerHTML')

    def verify_guest_incorrect_answer_elements(self):
        base_xpath = '//div[@id="' + self.get_incorrect_article() + '"]'
        assert "show" in self.selenium.find_element_by_xpath(base_xpath).get_attribute('class')
        assert "Incorrect!" in self.selenium.find_element_by_xpath(base_xpath + '//h5').get_attribute('innerHTML')
        assert self.get_article().title() + " " + self.noun.noun.replace("|"," | ") in self.selenium.find_element_by_xpath(base_xpath + '//li').get_attribute('innerHTML')
        assert "Next Question" in self.selenium.find_element_by_xpath(base_xpath + '//a[@role="button"]').get_attribute('innerHTML')

    def verify_authorized_correct_answer_elements(self):
        base_xpath = '//div[@id="' + self.get_article() + '"]'
        assert "show" in self.selenium.find_element_by_xpath(base_xpath).get_attribute('class')
        assert "Correct!" in self.selenium.find_element_by_xpath(base_xpath + '//h5').get_attribute('innerHTML')
        #assert self.get_article().title() + " " + self.noun.noun.replace("|"," | ") in self.selenium.find_element_by_xpath(base_xpath + '//p').get_attribute('innerHTML')
        assert "How hard was that?" in self.selenium.find_element_by_xpath(base_xpath + '//form//h5').get_attribute('innerHTML')
        assert self.noun.noun in self.selenium.find_element_by_xpath(base_xpath + '//form/input[@name="noun"]').get_attribute('value')
        assert self.noun.english in self.selenium.find_element_by_xpath(base_xpath + '//form/input[@name="english"]').get_attribute('value')
        assert "Difficult" in self.selenium.find_element_by_xpath(base_xpath + '//form//button[@value="3"]').get_attribute('innerHTML')
        assert "Hesitated" in self.selenium.find_element_by_xpath(base_xpath + '//form//button[@value="4"]').get_attribute('innerHTML')
        assert "No Problem" in self.selenium.find_element_by_xpath(base_xpath + '//form//button[@value="5"]').get_attribute('innerHTML')

    def verify_authorized_incorrect_answer_elements(self):
        base_xpath = '//div[@id="' + self.get_incorrect_article() + '"]'
        assert "show" in self.selenium.find_element_by_xpath(base_xpath).get_attribute('class')
        assert "Incorrect!" in self.selenium.find_element_by_xpath(base_xpath + '//h5').get_attribute('innerHTML')
        #assert self.get_article().title() + " " + self.noun.noun.replace("|"," | ") in self.selenium.find_element_by_xpath(base_xpath + '//p').get_attribute('innerHTML')
        assert "Do you know this now?" in self.selenium.find_element_by_xpath(base_xpath + '//form//h5').get_attribute('innerHTML')
        assert self.noun.noun in self.selenium.find_element_by_xpath(base_xpath + '//form/input[@name="noun"]').get_attribute('value')
        assert self.noun.english in self.selenium.find_element_by_xpath(base_xpath + '//form/input[@name="english"]').get_attribute('value')
        assert "Not Really" in self.selenium.find_element_by_xpath(base_xpath + '//form//button[@value="0"]').get_attribute('innerHTML')
        assert "Maybe" in self.selenium.find_element_by_xpath(base_xpath + '//form//button[@value="1"]').get_attribute('innerHTML')
        assert "Definitely" in self.selenium.find_element_by_xpath(base_xpath + '//form//button[@value="2"]').get_attribute('innerHTML')

    def guest_next_question(self):
        with self.wait_for_page_load(timeout=10):
        	self.selenium.find_element_by_xpath('//div[contains(@class, "collapse show")]//a[@role="button"]').click()
        
    def authorized_next_question(self, quality):
        if quality < 3:
            base_xpath = '//div[@id="' + self.get_incorrect_article() + '"]'
        else:
            base_xpath = '//div[@id="' + self.get_article() + '"]'
        with self.wait_for_page_load(timeout=10):
        	self.selenium.find_element_by_xpath(base_xpath + '//form//button[@value="' + str(quality) + '"]').click()

    def get_genderreviewscore(self):
        if self.is_rule:
            self.genderreviewscore = GenderReviewScore.objects.get(rule__short_name = self.rule.short_name, user__username = self.username)
        else:
            self.genderreviewscore = GenderReviewScore.objects.get(noun__noun = self.noun.noun, noun__gender = self.noun.gender, user__username = self.username)

    def genderreviewscore_verification(self, quality, interval, consecutive_correct, easiness_factor):
        self.get_genderreviewscore()
        if quality < 3:
            assert self.genderreviewscore.interval == 0
            assert self.genderreviewscore.consecutive_correct == 0
            assert self.genderreviewscore.review_date <= datetime.datetime.now(pytz.timezone('UTC')) + datetime.timedelta(seconds=5)
            assert round(self.genderreviewscore.easiness_factor, 2) == round(max(1.3, easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))), 2)
        else:
            if interval == 0:
                assert self.genderreviewscore.interval == 1
            elif interval == 1:
                assert self.genderreviewscore.interval == 6
            else:
                assert self.genderreviewscore.interval == math.ceil(interval * easiness_factor)
            assert self.genderreviewscore.consecutive_correct == consecutive_correct + 1
            assert self.genderreviewscore.review_date <= datetime.datetime.now(pytz.timezone('UTC')) + datetime.timedelta(seconds=5)
            assert round(self.genderreviewscore.easiness_factor, 2) == round(easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)), 2)

    def login(self, username, password):
        self.username = username
        self.password = password
        with self.wait_for_page_load(timeout=10):
        	self.selenium.find_element_by_xpath('//main/div/div/p/small/a[contains(text(), "Sign In")]').click()
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(password)
        with self.wait_for_page_load(timeout=10):
        	self.selenium.find_element_by_xpath('//button[@id="signin"]').click()

    def make_card_due(self, genderreviewscore, username, delta):
        if self.is_rule:
            if genderreviewscore.consecutive_correct > 0:
                GenderReviewScore.objects.filter(rule__short_name = genderreviewscore.rule.short_name, user__username = self.username).update(
                    review_date = datetime.datetime.now(pytz.timezone('UTC')) - datetime.timedelta(days=genderreviewscore.interval) - delta)
            else:
                GenderReviewScore.objects.filter(rule__short_name = genderreviewscore.rule.short_name, user__username = self.username).update(
                    review_date = datetime.datetime.now(pytz.timezone('UTC')) - datetime.timedelta(minutes=10) - delta)
        else:
            if genderreviewscore.consecutive_correct > 0:
                GenderReviewScore.objects.filter(noun__noun = genderreviewscore.noun.noun, noun__gender = genderreviewscore.noun.gender, user__username = self.username).update(
                    review_date = datetime.datetime.now(pytz.timezone('UTC')) - datetime.timedelta(days=genderreviewscore.interval) - delta)
            else:
                GenderReviewScore.objects.filter(noun__noun = genderreviewscore.noun.noun, noun__gender = genderreviewscore.noun.gender, user__username = username).update(
                    review_date = datetime.datetime.now(pytz.timezone('UTC')) - datetime.timedelta(minutes=10) - delta)

    def make_last_overdue(self):
        self.get_genderreviewscore()
        self.make_card_due(self.genderreviewscore, self.username, datetime.timedelta(days=2))

    def make_last_due(self):
        self.get_genderreviewscore()
        self.make_card_due(self.genderreviewscore, self.username, datetime.timedelta(minutes=1))

    def make_last_due_and_review(self, quality):
        if self.is_rule:
            scopy = copy.copy(GenderReviewScore.objects.get(rule__short_name = self.rule.short_name, user__username = self.username))
            self.make_card_due(scopy, self.username, datetime.timedelta(minutes=1))
        else:
            scopy = copy.copy(GenderReviewScore.objects.get(noun__noun = self.noun.noun, user__username = self.username))
            self.make_card_due(scopy, self.username, datetime.timedelta(minutes=1))
        self.select_correct_answer()            # this question is not important
        self.authorized_next_question(5)        # this question is not important
        self.get_noun()
        if self.is_rule:
            assert self.rule.short_name == scopy.rule.short_name
        else:
            assert self.noun.noun == scopy.noun.noun
        if quality < 3:
            self.select_incorrect_answer()
        else:
            self.select_correct_answer()
        self.authorized_next_question(quality)  # this questino is the one we care about
        self.genderreviewscore_verification(quality, scopy.interval, scopy.consecutive_correct, scopy.easiness_factor)

    def accept_alert(self):
      try:
        WebDriverWait(self.selenium, 5).until(expected_conditions.alert_is_present(), 'Timed out waiting for alert')
        alert = self.selenium.switch_to_alert()
        alert.accept()
        time.sleep(2)
      except:
        print "No Alert Found"


