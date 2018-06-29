# Deutsch Grammatik
A website for practicing German grammar using spaced repetition.
[Try it out](http://www.erikshelley.com/deutschgrammatik/).

[![Coverage](coverage.svg)](http://codecov.io/github/nedbat/coveragepy?branch=master)

## Motivation
Spaced repetition flash card software is helpful for learning vocabulary but it is not ideal for learning grammar.
I decided to build a spaced repetition system for learning grammar rules that varies the content of the flash
card for a given rule each time it is seen while keeping the content applicable for that rule.

## Grammar Topics
- [x] Deklination (Declension)
  - [x] Identify Gender
  - [ ] Identify Case
  - [ ] Identify Declension
- [ ] Konjugation (Conjugation)
  - [ ] Topics TBD
- [ ] Wortstellung (Word Order)
  - [ ] Topics TBD

## Features
- [x] Spaced Repetition for Rules and Exceptions
- [x] Progress Tracking For Signed In Users (Items Reviewed, Items Learned, Reviews Due)
- [x] Responsive Design (Mobile Friendly)
- [x] 5,000 Most Commonly Used German Nouns
- [x] 44 Gender Rules Covering ~60% of the 5,000 Nouns
- [ ] Sample Sentences for Identifying Cases and Declension
- [ ] Automatic Detection of Obvious Cases in Sample Sentences
- [ ] Ability to Manually Confirm Ambiguous Cases in Sample Sentences
- [ ] Save Time Zone Information per User
- [ ] Future Work: Conjugation and Word Order

## Screenshots

<details>
  <summary>Guest User</summary>
  <a href="screenshots/guest-homepage.png"><img alt="Home Page" src="screenshots/guest-homepage_thumb.png"></a>
  <a href="screenshots/guest-deklination.png"><img alt="Deklination" src="screenshots/guest-deklination_thumb.png"></a>
  <a href="screenshots/guest-genderquiz-question.png"><img alt="Gender Quiz Question" src="screenshots/guest-genderquiz-question_thumb.png"></a>
  <a href="screenshots/guest-genderquiz-answer.png"><img alt="Gender Quiz Answer" src="screenshots/guest-genderquiz-answer_thumb.png"></a>
  <a href="screenshots/guest-genderquiz-dictionary.png"><img alt="Gender Quiz Dictionary" src="screenshots/guest-genderquiz-dictionary_thumb.png"></a>
</details>

<details>
  <summary>Authorized User</summary>
  <a href="screenshots/user-homepage.png"><img alt="Home Page Reviews Due" src="screenshots/user-homepage_thumb.png"></a>
  <a href="screenshots/user-homepage-nextreviewdue.png"><img alt="Home Page Next Review" src="screenshots/user-homepage-nextreviewdue_thumb.png"></a>
  <a href="screenshots/user-deklination.png"><img alt="Deklination" src="screenshots/user-deklination_thumb.png"></a>
  <a href="screenshots/user-genderquiz-question.png"><img alt="Gender Quiz Question" src="screenshots/user-genderquiz-question_thumb.png"></a>
  <a href="screenshots/user-genderquiz-answer-correct.png"><img alt="Gender Quiz Correct Answer" src="screenshots/user-genderquiz-answer-correct_thumb.png"></a>
  <a href="screenshots/user-genderquiz-answer-incorrect.png"><img alt="Gender Quiz Incorrect Answer" src="screenshots/user-genderquiz-answer-incorrect_thumb.png"></a>
  <a href="screenshots/user-genderquiz-answer-exception.png"><img alt="Gender Quiz Exception Answer" src="screenshots/user-genderquiz-answer-exception_thumb.png"></a>
  <a href="screenshots/user-genderquiz-answer-norule.png"><img alt="Gender Quiz NoRule Answer" src="screenshots/user-genderquiz-answer-norule_thumb.png"></a>
  <a href="screenshots/user-progress.png"><img alt="Progress" src="screenshots/user-progress_thumb.png"></a>
  <a href="screenshots/user-progress-reviewed.png"><img alt="Progress" src="screenshots/user-progress-reviewed_thumb.png"></a>
  <a href="screenshots/user-progress-learned.png"><img alt="Progress" src="screenshots/user-progress-learned_thumb.png"></a>
</details>

<details>
  <summary>Mobile</summary>
  <a href="screenshots/user-genderquiz-dictionary-mobile.png"><img alt="Gender Quiz Dictionary Mobile" src="screenshots/user-genderquiz-dictionary-mobile_thumb.png"></a>
  <a href="screenshots/user-genderquiz-dictionary-mobile-rotated.png"><img alt="Gender Quiz Dictionary Mobile" src="screenshots/user-genderquiz-dictionary-mobile-rotated_thumb.png"></a>
</details>

## How to Use
For the moment this project is not meant to be downloaded and installed.
Instead a [working version](http://www.erikshelley.com/deutschgrammatik/) is available for use.

## Frameworks/Tools Used
* [Django](https://www.djangoproject.com/)
* [Bootstrap](https://getbootstrap.com/)
* [Django-JChart](https://github.com/matthisk/django-jchart)
* [Font Awesome](https://fontawesome.com/)

## License
The code in this project is licensed under the [GNU General Public License v3.0](LICENSE).

