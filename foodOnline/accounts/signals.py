from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import User, UserProfile


@receiver(post_save, sender=User)
def post_save_create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        print('Create User Profile')
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
            print("User Updated")
        except:
            UserProfile.objects.create(user=instance)
            print("User Profile didn't exist. Created new profile")
        

