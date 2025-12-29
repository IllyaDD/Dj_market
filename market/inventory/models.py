from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser

class Product(models.Model):
    class Unit(models.TextChoices):
        LITRE = 'l', 'litre'
        KILOGRAM = 'kg', 'kilogram'
        M2 = 'm2', 'm²'
        PIECE = 'pcs', 'piece'
        PACK = 'pack', 'pack'

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=10, choices=Unit.choices)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ratings')
    value = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating({self.product_id}, {self.user_id})={self.value}"


class Cart(models.Model):
    class Status(models.TextChoices):
        IN_CART = 'in_cart', 'In Cart'
        PURCHASED = 'purchased', 'Purchased'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, validators=[MinValueValidator(0.01)])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_CART)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product', 'status')
        indexes = [
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"Cart({self.user.username}, {self.product.name}, {self.quantity})"
