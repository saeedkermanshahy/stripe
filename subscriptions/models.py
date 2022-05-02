from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

# Create your models here.
class StripeCustomer(models.Model):

    user = models.OneToOneField(User, verbose_name=_("User"), on_delete=models.CASCADE)
    stripeCustomerId = models.CharField(
        verbose_name=_("Stripe Customer ID"), max_length=255
    )
    stripeSubscriptionId = models.CharField(
        verbose_name=_("Stripe Subscription ID"), max_length=255
    )

    class Meta:
        verbose_name = _("StripeCustomer")
        verbose_name_plural = _("StripeCustomers")

    def __str__(self):
        return self.user.username


