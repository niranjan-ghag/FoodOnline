from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification
from django.core.exceptions import ValidationError
from datetime import date, datetime, time

# Create your models here.

class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile',on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.vendor_name
    
    def is_open(self):
        today_date = date.today()
        today = today_date.isoweekday()

        current_opening_hours = OpeningHour.objects.filter(vendor=self, days=today)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        # current_time = datetime.now().time()

        is_open = None
        for i in current_opening_hours:
            if not i.is_closed:
                start = str(datetime.strptime(i.from_hours,'%I:%M %p').time())
                end = str(datetime.strptime(i.to_hours,'%I:%M %p').time())
                if current_time > start and current_time < end:
                    is_open = True
                    break
                else:
                    is_open =False
                # start = datetime.strptime(i.from_hours,'%I:%M %p').time()
                # end = datetime.strptime(i.to_hours,'%I:%M %p').time()
                # if start >= current_time and end <= current_time:
                #     is_open = True
                #     break
                # else:
                #     is_open =False

        return is_open
    
    def save(self, *args, **kwargs):
        if self.pk:
            orig = Vendor.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {'user': self.user, 'is_approved': self.is_approved,'to_email': self.user.email}
                if self.is_approved:
                    # Send Notification email
                    mail_subject="Congratulations! Your Resturant has been approved!"
                    send_notification(mail_subject, mail_template, context)
                else:
                    # Send Notification email
                    mail_subject="We are Sorry! You are not eligible for publishing your Resturant on OnlineFoood!"
                    send_notification(mail_subject, mail_template, context)
        return super(Vendor, self).save(*args, **kwargs)
    
# DAYS = [(1,'Monday')]

class OpeningHour(models.Model):
    DAYS = (
        (1,'Monday'),
        (2,'Tuesday'),
        (3,'Wednesday'),
        (4,'Thursday'),
        (5,'Friday'),
        (6,'Saturday'),
        (7,'Sunday'),
        )
    time_slots = [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) for h in range(0,24) for m in (0,30)]
    # HOUR_OF_DAY_24 = 
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    days = models.IntegerField(choices=DAYS)
    from_hours = models.CharField(choices=time_slots, max_length=10, blank=True)
    to_hours = models.CharField(choices=time_slots, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('days', '-from_hours')
        unique_together = ('vendor','days','from_hours','to_hours')
    
    def __str__(self):
        return self.get_days_display()

    def clean(self):
        """Ensure from_hours is not the same as to_hours."""
        if self.from_hours or self.to_hours:
            if self.from_hours == self.to_hours:
                raise ValidationError({'to_hours': 'Opening and closing times cannot be the same.'})
    
    def save(self, *args, **kwargs):
        """Validate before saving the model."""
        self.clean()  # Calls clean() to check constraints
        super().save(*args, **kwargs)