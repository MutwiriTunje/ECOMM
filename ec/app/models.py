# import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here.



COUNTY_CHOICES = (
('Mombasa','Mombasa'),
('Kwale','Kwale'),
('Kilifi','Kilifi'),
('Tana River','Tana River'),
('Lamu','Lamu'),
('Taita/Taveta','Taita/Taveta'),
('Garissa','Garissa'),
('Wajir','Wajir'),
('Mandera','Mandera'),
('Marsabit','Marsabit'),
('Isiolo','Isiolo'),
('Meru','Meru'),
('Tharaka-Nithi','Tharaka-Nithi'),
('Embu','Embu'),
('Kitui','Kitui'),
('Machakos','Machakos'),
('Makueni','Makueni'),
('Nyandarua','Nyandarua'),
('Nyeri','Nyeri'),
('Kirinyaga','Kirinyaga'),
('Murang’a','Murang’a'),
('Kiambu','Kiambu'),
('Turkana','Turkana'),
('West Pokot','West Pokot'),
('Samburu','Samburu'),
('Trans Nzoia','Trans Nzoia'),
('Uasin Gishu','Uasin Gishu'),
('Elgeyo/Marakwet','Elgeyo/Marakwet'),
('Nandi','Nandi'),
('Baringo','Baringo'),
('Laikipia','Laikipia'),
('Nakuru','Nakuru'),
('Narok','Narok'),
('Kajiado','Kajiado'),
('Kericho','Kericho'),
('Bomet','Bomet'),
('Kakamega','Kakamega'),
('Vihiga','Vihiga'),
('Bungoma','Bungoma'),
('Busia','Busia'),
('Siaya','Siaya'),
('Kisumu','Kisumu'),
('Homa Bay','Homa Bay'),
('Migori','Migori'),
('Kisii','Kisii'),
('Nyamira','Nyamira'),
('Nairobi','Nairobi')

)

CATEGORY_CHOICES=(
    ('CR','Curd'),
    ('ML','Milk'),
    ('LS','Lassi'),
    ('MS','Milkshake'),
    ('PN','Paneer'),
    ('GH','Ghee'),
    ('CZ','Cheese'),
    ('IC','Ice-Creams'),
)

class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    composition = models.TextField(default='')
    prodapp = models.TextField(default='')
    category = models.CharField(choices=CATEGORY_CHOICES,  max_length=2)
    product_image = models.ImageField(upload_to='product')
    def __str__(self):
        return self.title
    
class Customer(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    mobile = models.IntegerField(default=0)
    zipcode = models.IntegerField()
    county = models.CharField(choices=COUNTY_CHOICES,max_length=100)
    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price
    
STATUS_CHOICES = (
    ('Accepted','Accepted'),
    ('Packed','Packed'),
    ('On The Way','On The Way'),
    ('Delivered','Delivered'),
    ('Cancel','Cancel'),
    ('Pending','Pending'),
)

class Payment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount = models.FloatField()
    razorpay_order_id = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_status = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_id = models.CharField(max_length=100,blank=True,null=True)
    paid = models.BooleanField(default=False)


class OrderPlaced(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES, default='Pending')
    payment = models.ForeignKey(Payment,on_delete=models.CASCADE,default="")
    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price