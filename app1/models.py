from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

# Create your models here.


class Contact(models.Model):
    s_no = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=20)
    Email = models.EmailField(max_length=50)
    Contact = models.CharField(max_length=10)
    Subject = models.CharField(max_length=50)
    Message = models.TextField()
    timeStamp = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return 'Message from ' + self.Name

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    slug = models.SlugField( null=True, blank=True)
    product_name = models.CharField(max_length=50)
    product_price = models.IntegerField()

    image = models.ImageField(upload_to="media")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    num_days = models.IntegerField(null=True)
    price_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return str(self.pk)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # set default value for price
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='images/', null=True, blank=True)

    def __str__(self):
        return f'{self.product} ({self.quantity})'
