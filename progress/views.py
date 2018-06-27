import datetime, pytz
from datetime 					    import timedelta, datetime
from django.db.models               import F, ExpressionWrapper, DateField, DateTimeField
from django.utils                   import timezone
from django.contrib.auth.models     import User
from django.contrib.auth.decorators import login_required
from django.shortcuts 		        import render
from jchart                         import Chart
from jchart.config                  import Axes, DataSet, rgba, ScaleLabel, Tick, Title
from .models                        import Progress
from deklination.models             import GenderReviewScore


@login_required
def index(request):
    context = {}
    context['page_subtitle'] = 'Progress - '
    card1 = {
        'disabled': False, 
        'title': 'Items Reviewed',  
        'text': "See how many new items you studied each day, how many you reviewed each day, and how many are due for review to reinforce them in you memory.",
        'icon': 'chart-bar',
        'chart': 'progress:review_chart',
        'chart_user': request.user, 
        'chart_delta': 7,
        'button_id': 'begin_reviewed',
        'button_text': 'View &raquo;',
        'url': 'progress:reviewed'
        }
    card2 = {
        'disabled': False,  
        'title': 'Items Learned',  
        'text': 'See how many items you are learning, how many you can remember over the short-term, and how many you have committed to long-term memory.',
        'icon': 'chart-bar',
        'chart': 'progress:learned_chart',
        'chart_user': request.user,
        'chart_delta': 7,
        'button_id': 'begin_learned',
        'button_text': 'View &raquo;',
        'url': 'progress:learned'
        }
    context['card_deck'] = [card1, card2]
    if request.user.is_authenticated():
        progress = ProgressTracker()
        context['next_review'] = progress.get_next_review(request.user)
        context['dek_reviews'] = progress.get_review_count(request.user, 'DG')
    return render(request, 'progress/index.html', context)

    
@login_required
def reviewed(request):
    context = {}
    context['page_subtitle'] = 'Items Reviewed - Progress - '
    progress = ProgressTracker()
    context['dek_reviews'] = progress.get_review_count(request.user, 'DG')
    #if request.method == POST:
    #    quality = int(request.POST['quality'])
    return render(request, 'progress/reviewed.html', context)


@login_required
def learned(request):
    context = {}
    context['page_subtitle'] = 'Items Learned - Progress - '
    progress = ProgressTracker()
    context['dek_reviews'] = progress.get_review_count(request.user, 'DG')
    return render(request, 'progress/learned.html', context)


class ProgressTracker:
    def update_progress(self, user, quiz, quality, new_delta, short_delta, long_delta):
        today = timezone.now()
        local_datetime = timezone.localtime(today).replace(hour=0, minute=0, second=0, microsecond=0)
        local_date = local_datetime.date()
        progress, created = Progress.objects.get_or_create(user = user, quiz = quiz, review_date = local_date)
        if created:
            previous = Progress.objects.filter(user = user, quiz = quiz, review_date__lt = local_date).order_by('-review_date')
            if len(previous) > 0:
                progress.new_count = previous[0].new_count
                progress.short_count = previous[0].short_count
                progress.long_count = previous[0].long_count
        progress.new_count += new_delta
        progress.short_count += short_delta
        progress.long_count += long_delta
        quality_count = [0, 0, 0, 0, 0, 0]
        quality_count[quality] = 1
        progress.quality_0 += quality_count[0]
        progress.quality_1 += quality_count[1]
        progress.quality_2 += quality_count[2]
        progress.quality_3 += quality_count[3]
        progress.quality_4 += quality_count[4]
        progress.quality_5 += quality_count[5]
        progress.save()

    def get_review_count(self, user, quiz):
        local_time = timezone.now()
        if (quiz == 'DG') or (quiz == 'ALL'):
            reviews = GenderReviewScore.objects.filter(user = user)
        else:
            reviews = None
        if len(reviews) > 0:
            overdue = 0
            first_review = True
            for review in reviews:
                if review.interval == 0:
                    time_due = timezone.localtime(review.review_date) + timedelta(minutes = 10)
                else:
                    time_due = timezone.localtime(review.review_date) + timedelta(days = review.interval)
                if time_due < local_time:
                    overdue += 1
            return overdue
        else:
            return 0


    """
    You have x reviews due now.
    Your next review is due at ...
    """
    def get_next_review(self, user):
        local_time = timezone.now()
        reviews = GenderReviewScore.objects.filter(user = user)
        if len(reviews) > 0:
            overdue = 0
            first_review = True
            for review in reviews:
                # Positive = due in future
                # Negative = due in past
                if review.interval == 0:
                    time_due = timezone.localtime(review.review_date) + timedelta(minutes = 10)
                else:
                    time_due = timezone.localtime(review.review_date) + timedelta(days = review.interval)
                if time_due < local_time:
                    overdue += 1
                else:
                    if (first_review == True) or (time_due < min_time_due):
                        first_review = False
                        min_time_due = time_due
                        if review.interval == 0:
                            next_review_due = review.review_date + timedelta(minutes = 10)
                        else:
                            next_review_due = review.review_date + timedelta(days = review.interval)
            if overdue > 0:
                if overdue > 1:
                    return "You have " + str(overdue) + " items due for review. "
                else:
                    return "You have " + str(overdue) + " item due for review. "
            else:
                return "Your next item is due for review on " + timezone.localtime(next_review_due).strftime("%b %e, %Y at %r") + ". "
        else:
            return ""



def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(days=n)


class ReviewChart(Chart):
    chart_type = 'bar'
    title = Title(display = True, text = 'Deklension', fontSize = 16)
    legend = { 'display': True, 'position': 'bottom' }
    scales = { 'xAxes': [{ 'stacked': True }], 
               'yAxes': [{ 'stacked': True,
                           'ticks': { 'min': 0 },
                           'scaleLabel': ScaleLabel(display = True, fontStyle = 'bold', labelString = 'Items Per Day') }] }

    def get_labels(self, username, delta):
        labels = []
        today = timezone.now()
        for single_datetime in daterange(today - timedelta(days=int(delta)), today + timedelta(days=int(delta)+1)):
            local_datetime = timezone.localtime(single_datetime).replace(hour=0, minute=0, second=0, microsecond=0)
            local_date = local_datetime.date()
            month = local_date.strftime('%b')
            day = int(local_date.strftime('%d'))
            ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
            labels.append(month + ' ' + str(ordinal(day)))
        return labels

    def get_datasets(self, username, delta):
        user = User.objects.get(username = username)
        today = timezone.now()
        local_datetime = timezone.localtime(today).replace(hour=0, minute=0, second=0, microsecond=0)
        local_date = local_datetime.date()
        new_data = []
        review_data = []
        due_data = []

        due_dates = {}
        new_dates = {}
        scores = GenderReviewScore.objects.filter(user = user)
        for score in scores:
            first_review = timezone.localtime(score.first_review).date()
            if first_review in new_dates:
                new_dates[first_review] += 1
            else:
                new_dates[first_review] = 1

            last_review = timezone.localtime(score.review_date).date()
            due_date = last_review + timedelta(days=score.interval)
            if due_date < local_date:
                due_date = local_date
            if due_date in due_dates:
                due_dates[due_date] += 1
            else:
                due_dates[due_date] = 1

        for single_datetime in daterange(today - timedelta(days=int(delta)), today + timedelta(days=int(delta)+1)):
            single_date = single_datetime.date()
            local_date = timezone.localtime(single_datetime).date()
            utc_date = single_datetime.astimezone(pytz.UTC).date()
            past_reviews = Progress.objects.filter(user = user, quiz = 'DG', review_date = local_date)
            if len(past_reviews) > 0:
                progress = past_reviews[0]
                if local_date in new_dates:
                    count = progress.quality_0 + progress.quality_1 + progress.quality_2 + progress.quality_3 + progress.quality_4 + progress.quality_5 - new_dates[local_date]
                else:
                    count = progress.quality_0 + progress.quality_1 + progress.quality_2 + progress.quality_3 + progress.quality_4 + progress.quality_5
                review_data.append(count)
            else:
                review_data.append(0)

            if local_date in new_dates:
                new_data.append(new_dates[local_date])
            else:
                new_data.append(0)

            if local_date in due_dates:
                due_data.append(due_dates[local_date])
            else:
                due_data.append(0)

        # https://www.canva.com/learn/100-color-combinations/
        #new_hex    = '90AFC5'
        #review_hex = '336B87'
        #due_hex    = '763626'
        #new_hex    = 'F1F3CE'
        #review_hex = '1E656D'
        #due_hex    = 'F62A00'
        #new_hex = '6EB5C0'
        #rev_hex = 'E2E8E4'
        #due_hex = 'FFCCBB'
        #new_hex = 'FAEFD4'
        #rev_hex = 'A0B084'
        #due_hex = 'A57C65'
        new_hex = 'CDBEA7'
        rev_hex = 'C29545'
        due_hex = '882426'
        new_rgb = 'rgba(' + ','.join(map(str, tuple(int(new_hex[i:i+2], 16) for i in (0, 2 ,4))))
        rev_rgb = 'rgba(' + ','.join(map(str, tuple(int(rev_hex[i:i+2], 16) for i in (0, 2 ,4))))
        due_rgb = 'rgba(' + ','.join(map(str, tuple(int(due_hex[i:i+2], 16) for i in (0, 2 ,4))))

        return [
                DataSet(label='New   ', data=new_data,    borderWidth=1, borderColor=new_rgb+',1.0)', backgroundColor=new_rgb+',0.5)'),
                DataSet(label='Review', data=review_data, borderWidth=1, borderColor=rev_rgb+',1.0)', backgroundColor=rev_rgb+',0.5)'),
                DataSet(label='Due   ', data=due_data,    borderWidth=1, borderColor=due_rgb+',1.0)', backgroundColor=due_rgb+',0.5)'),
                ]

review_chart = ReviewChart()


class LearnedChart(Chart):
    chart_type = 'bar'
    title = Title(display = True, text = 'Deklension', fontSize = 16)
    legend = { 'display': True, 'position': 'bottom' }
    scales = { 'xAxes': [{ 'stacked': True }], 
               'yAxes': [{ 'stacked': True,
                           'ticks': { 'min': 0 },
                           'scaleLabel': ScaleLabel(display = True, fontStyle = 'bold', labelString = 'Total Items') }] }

    def get_labels(self, username, delta):
        labels = []
        today = timezone.now()
        for single_datetime in daterange(today - timedelta(days=int(delta)*2), today + timedelta(days=1)):
            local_datetime = timezone.localtime(single_datetime).replace(hour=0, minute=0, second=0, microsecond=0)
            local_date = local_datetime.date()
            month = local_date.strftime('%b')
            day = int(local_date.strftime('%d'))
            ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
            labels.append(month + ' ' + str(ordinal(day)))
        return labels

    def get_datasets(self, username, delta):
        user = User.objects.get(username = username)
        today = timezone.now()
        """
        Find latest progress entry for user (per quiz) before first date
        Set new, short, and long counts
        Carry counts over day-by-day until another progress entry exists then update
        """
        new_data = []
        short_data = []
        long_data = []
        new_count = 0
        short_count = 0
        long_count = 0
        start_datetime = today.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=int(delta)*2)
        previous_progress = Progress.objects.filter(user = user, quiz = 'DG', review_date__lt = start_datetime)
        if len(previous_progress) > 0:
            new_count = previous_progress[0].new_count
            short_count = previous_progress[0].short_count
            long_count = previous_progress[0].long_count
        for single_datetime in daterange(today - timedelta(days=int(delta)*2), today + timedelta(days=1)):
            local_datetime = timezone.localtime(single_datetime).replace(hour=0, minute=0, second=0, microsecond=0)
            local_date = local_datetime.date()
            progress = Progress.objects.filter(user = user, quiz = 'DG', review_date = local_date)
            if len(progress) > 0:
                new_count = progress[0].new_count
                short_count = progress[0].short_count
                long_count = progress[0].long_count
            new_data.append(new_count)
            short_data.append(short_count)
            long_data.append(long_count)

        # https://www.canva.com/learn/100-color-combinations/
        #new_hex   = '90AFC5'
        #short_hex = '336B87'
        #long_hex  = '2A3132'
        #new_hex   = 'F1F3CE'
        #short_hex = '1E656D'
        #long_hex  = '00293C'
        #new_hex   = 'E2E8E4'
        #short_hex = '6EB5C0'
        #long_hex  = '006C84'
        #new_hex   = 'FAEFD4'
        #short_hex = 'A0B084'
        #long_hex  = '688B8A'
        new_hex   = 'CDBEA7'
        short_hex = 'C29545'
        long_hex  = '323030'
        new_rgb   = 'rgba(' + ','.join(map(str, tuple(int(  new_hex[i:i+2], 16) for i in (0, 2 ,4))))
        short_rgb = 'rgba(' + ','.join(map(str, tuple(int(short_hex[i:i+2], 16) for i in (0, 2 ,4))))
        long_rgb  = 'rgba(' + ','.join(map(str, tuple(int( long_hex[i:i+2], 16) for i in (0, 2 ,4))))
        return [
                DataSet(label='New  ', data=new_data,   borderWidth=1, borderColor=new_rgb+',1.0)',   backgroundColor=new_rgb+',0.5)'),
                DataSet(label='Short', data=short_data, borderWidth=1, borderColor=short_rgb+',1.0)', backgroundColor=short_rgb+',0.5)'),
                DataSet(label='Long ', data=long_data,  borderWidth=1, borderColor=long_rgb+',1.0)',  backgroundColor=long_rgb+',0.5)'),
                ]

learned_chart = LearnedChart()


