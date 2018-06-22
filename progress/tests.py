# -*- coding: utf-8 -*-
from __future__                                     import unicode_literals

from django.contrib.auth.models                     import User
from django.core.cache                              import cache
from django.conf                                    import settings
from django.contrib.staticfiles.testing             import StaticLiveServerTestCase
from django.test                                    import TestCase, Client
from django.utils                                   import timezone

import copy, datetime, math, os, pytz, re, time, unittest, unicodecsv as csv

from contextlib                                     import contextmanager

from selenium.webdriver.firefox.webdriver           import WebDriver
from selenium.webdriver.support.ui                  import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support                     import expected_conditions

from .models                                        import Progress
from deutsch.tests                                  import TestUserManagement, SeleniumClass
from deklination.tests                              import TestDeklinationActions


def check_universal_items(resp):
    assert resp.status_code == 200
    assert "<!DOCTYPE html" in resp.content

def check_guest_items(self, resp):
    assert "username" in resp.content

def check_authorized_items(self, resp):
    assert "Sign Up" not in resp.content
    assert "Sign In" not in resp.content
    expected_regex = re.compile(r"<nav .+?Hello First.+?Sign Out.+?</nav>", re.MULTILINE|re.DOTALL)
    unittest.TestCase.assertRegexpMatches(self, resp.content.encode('utf-8'), expected_regex)

def check_authorized_chart_items(self, resp):
    assert "data" in resp.content
    assert "labels" in resp.content
    assert "legend" in resp.content
    assert "scale" in resp.content


class TestProgressEmptyDB(TestCase):
    def test_progress_guest(self):
        print '\nTest: Progress Guest'
        resp = self.client.get("/progress/", follow=True)
        check_universal_items(resp)
        check_guest_items(self, resp)

    def test_deklination_authorized(self):
        print '\nTest: Progress Authorized'
        username = 'test_progress_authorized'
        password = User.objects.make_random_password()
        tum = TestUserManagement()
        tum.create_user(username, password, False)
        self.client.login(username=username, password=password)

        resp = self.client.get("/progress/", follow=True)
        check_universal_items(resp)
        check_authorized_items(self, resp)

        resp = self.client.get("/progress/reviewed/", follow=True)
        check_universal_items(resp)
        check_authorized_items(self, resp)

        resp = self.client.get("/progress/learned/", follow=True)
        check_universal_items(resp)
        check_authorized_items(self, resp)

        resp = self.client.get("/progress/charts/review_chart/" + username + "/")
        check_authorized_chart_items(self, resp)
        expected_regex = re.compile(r'"data": \[(0, ){14}0\],', re.MULTILINE|re.DOTALL)
        unittest.TestCase.assertRegexpMatches(self, resp.content.encode('utf-8'), expected_regex)

        resp = self.client.get("/progress/charts/learned_chart/" + username + "/")
        check_authorized_chart_items(self, resp)
        expected_regex = re.compile(r'"data": \[(0, ){14}0\],', re.MULTILINE|re.DOTALL)
        unittest.TestCase.assertRegexpMatches(self, resp.content.encode('utf-8'), expected_regex)


class TestProgress(SeleniumClass):
    def test_progress(self):
        print '\nUI Test: Progress '
        username = 'test_progress'
        password = User.objects.make_random_password()
        tum = TestUserManagement()
        tum.create_user(username, password, False)
        tda = TestDeklinationActions(self.selenium, self.live_server_url, self.wait_for_page_load)
        tda.navigate_to_quiz()
        tda.login(username, password)
        # New
        tda.select_correct_answer()
        tda.authorized_next_question(5)
        # Short
        tda.select_correct_answer()
        tda.authorized_next_question(5)
        tda.make_last_due_and_review(5)
        # Move progress before start of learned chart
        today = timezone.now()
        local_datetime = timezone.localtime(today).replace(hour=0, minute=0, second=0, microsecond=0)
        local_date = local_datetime.date()
        Progress.objects.filter(user__username = username, quiz = 'DG', review_date = local_date).update(
            review_date = datetime.datetime.now(pytz.timezone('UTC')) - datetime.timedelta(days=21))
        tda.make_last_due_and_review(5)
        # Long
        tda.select_correct_answer()
        tda.authorized_next_question(5)
        tda.make_last_due_and_review(5)
        tda.make_last_due_and_review(5)
        tda.make_last_due_and_review(5)
        # More than one due
        tda.make_last_overdue()
        tda.select_incorrect_answer()
        tda.authorized_next_question(0)
        tda.make_last_due()
        tda.navigate_to_quiz()
        with self.wait_for_page_load(timeout=10):
            self.selenium.find_element_by_xpath('//a[contains(@href, "progress")]').click()
        #time.sleep(10)
        with self.wait_for_page_load(timeout=10):
            self.selenium.find_element_by_xpath('//a[@id="begin_reviewed"]').click()
        with self.wait_for_page_load(timeout=10):
            self.selenium.find_element_by_xpath('//a[contains(@href, "progress")]').click()
        with self.wait_for_page_load(timeout=10):
            self.selenium.find_element_by_xpath('//a[@id="begin_learned"]').click()

