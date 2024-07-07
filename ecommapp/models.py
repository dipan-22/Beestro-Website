from django.db import models
from .constants import PaymentStatus
# Create your models here.
class category(models.Model):
    name=models.CharField(max_length=100,default='',blank=False,null=False)
    status=models.BooleanField(default=True)

    def __str__(self):
        return self.name

class product(models.Model):
    name=models.CharField(max_length=100,default='',blank=False,null=False)
    price=models.IntegerField(default=0, null=False, blank=False)
    short_description=models.TextField()
    long_description=models.TextField(blank=True,null=True)
    product_catogory=models.ForeignKey(category,on_delete=models.CASCADE)
    quantity=models.CharField(max_length=50)
    slug=models.SlugField(primary_key=True)
    active=models.BooleanField(default=True)

    
    def __str__(self):
        return self.name
    
class product_image(models.Model):
    single_product=models.ForeignKey(product,on_delete=models.CASCADE)
    image=models.ImageField(upload_to='product_images/',null=True)
    active=models.BooleanField(default=True)   

    def __str__(self):
        return self.single_product.name    
    
class SIGN(models.Model):
    name=models.CharField(max_length=100)
    address=models.CharField(max_length=100)
    email=models.EmailField(max_length=200,primary_key=True)
    phone=models.IntegerField(null=True,blank=True)
    username=models.CharField(max_length=100)
    password=models.CharField(max_length=100)


class Order(models.Model):
    name = models.CharField(("Customer Name"), max_length=254, blank=False, null=False)
    amount = models.FloatField(("Amount"), null=False, blank=False)
    status = models.CharField(
        ("Payment Status"),
        default=PaymentStatus.PENDING,
        max_length=254,
        blank=False,
        null=False,
    )
    provider_order_id = models.CharField(
        ("Order ID"), max_length=40, null=False, blank=False
    )
    payment_id = models.CharField(
        ("Payment ID"), max_length=36, null=False, blank=False
    )
    signature_id = models.CharField(
        ("Signature ID"), max_length=128, null=False, blank=False
    )

    def __str__(self):
        return f"{self.id}-{self.name}-{self.status}"#fstring
        
    def mark_as_paid(self):
        self.status = PaymentStatus.SUCCESS
        self.save()		