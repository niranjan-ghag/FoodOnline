from django.db import models

from accounts.models import User
from menu.models import FoodItem

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateField(auto_now_add=True)

    # def __unicode__(self):
    #     print("--self.user--",self.user)
    #     return self.user

    def __str__(self):
        return f"{self.user.email}"