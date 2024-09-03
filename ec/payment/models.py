from django.db import models

# Create your models here.
class Payments(models.Model):
    MerchantRequestID = models.CharField(max_length=64)
    resultCode = models.IntegerField()
    resultDesc = models.TextField()
    receiptNumber = models.CharField(max_length=18,null=True,blank=True)
    amount = models.FloatField(null=True,blank=True)
    transactionDate = models.DateTimeField(null=True,blank=True)
    phoneNumber = models.CharField(max_length=16,null=True,blank=True)

    def __str__(self) -> str:
        return str(self.receiptNumber)
