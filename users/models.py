from django.db import models
from django.contrib.auth.models import AbstractUser 
# Create your models here.

class User(AbstractUser):
    
    ADMIN = 'admin'
    SHOPKEEPER = 'shopkeeper'
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('shopkeeper', 'shopkeeper'),
    ]
    
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='shopkeeper')
    
    
    
    def is_admin(self):
        return self.role == self.ADMIN
    
    def is_shopkeeper(self):
        return self.role == self.SHOPKEEPER
    
    def __str__(self):
        return f"{self.username} - {self.role}"
    
    
class Products(models.Model):
    name = models.CharField(max_length=100)
    cost_price = models.DecimalField(max_digits=8, decimal_places=2)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def profit_per_unit(self):
        """Calculates the profit per unit sold"""
        return self.price - self.cost_price
    
    def __str__(self):
        return self.name

class Sale(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField()  
    selling_price = models.DecimalField(max_digits=8, decimal_places=2)  # New Field
    customer_details = models.CharField(max_length=70)
    mode_of_payment = models.CharField(max_length=20)
    sale_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.product.stock >= self.quantity:
            self.product.stock -= self.quantity  # Reduce stock
            self.product.save()
            super().save(*args, **kwargs)
        else:
            raise ValueError("Not enough stock available")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} on {self.sale_date}"

    def total_price(self):
        return self.selling_price * self.quantity  # Total revenue

    @property
    def total_profit(self):
        """Calculates profit dynamically (Revenue - Cost)"""
        return self.quantity * (self.selling_price - self.product.cost_price)
