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
  [![Home Page](guest-homepage_thumb.png)](screenshots/guest-homepage.png)
  [![Deklination](guest-deklination_thumb.png)](screenshots/guest-deklination.png)
  [![Gender Quiz Question](guest-genderquiz-question_thumb.png)](screenshots/guest-genderquiz-question.png)
  [![Gender Quiz Answer](guest-genderquiz-answer_thumb.png)](screenshots/guest-genderquiz-answer.png)
  [![Gender Quiz Dictionary](guest-genderquiz-dictionary_thumb.png)](screenshots/guest-genderquiz-dictionary.png)
</details>

<details>
  <summary>Authorized User</summary>
  [![Home Page Reviews Due](user-homepage_thumb.png)](screenshots/user-homepage.png)
  [![Home Page Next Review](user-homepage-nextreviewdue_thumb.png)](screenshots/user-homepage-nextreviewdue.png)
  [![Deklination](user-deklination_thumb.png)](screenshots/user-deklination.png)
  [![Gender Quiz Question](user-genderquiz-question_thumb.png)](screenshots/user-genderquiz-question.png)
  [![Gender Quiz Correct Answer](user-genderquiz-answer-correct_thumb.png)](screenshots/user-genderquiz-answer-correct.png)
  [![Gender Quiz Incorrect Answer](user-genderquiz-answer-incorrect_thumb.png)](screenshots/user-genderquiz-answer-incorrect.png)
  [![Gender Quiz Exception Answer](user-genderquiz-answer-exception_thumb.png)](screenshots/user-genderquiz-answer-exception.png)
  [![Gender Quiz NoRule Answer](user-genderquiz-answer-norule_thumb.png)](screenshots/user-genderquiz-answer-norule.png)
  [![Progress](user-progress_thumb.png)](screenshots/user-progress.png)
  [![Progress](user-progress-reviewed_thumb.png)](screenshots/user-progress-reviewed.png)
  [![Progress](user-progress-learned_thumb.png)](screenshots/user-progress-learned.png)
</details>

<details>
  <summary>Mobile</summary>
  [![Gender Quiz Dictionary Mobile](user-genderquiz-dictionary-mobile_thumb.png)](screenshots/user-genderquiz-dictionary-mobile.png)
  [![Gender Quiz Dictionary Mobile](user-genderquiz-dictionary-mobile-rotated_thumb.png)](screenshots/user-genderquiz-dictionary-mobile-rotated.png)
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

