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
    

class Tax(models.Model):
    tax_type = models.CharField(max_length=20, unique=True)
    tax_percentage = models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Tax Percentage (%)')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'tax'

    def __str__(self):
        return self.tax_type