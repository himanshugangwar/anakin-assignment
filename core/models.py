from django.db import models

# Create your models here.


PROMOTION_ON_TYPE = (
    ("BRAND", "Brand"),
    ("PRODUCT", "Product"),
    ("RETAIL_STORE", "Retail Store"),
    ("RETAILER", "Retailer"),
    ("CUSTOM", "Custom"),
)


PROMOTION_TYPE = (
    ("FIXED", "Fixed Amount"),
    ("PERCENTAGE", "Percentage of Amount"),
)


ALERT_TYPE = (
    ("PRICE_INCREASE", "Price of product has increased"),
    ("PRICE_DECREASE", "Price of product has decreased"),
)


class Brand(models.Model):
    name = models.CharField(
        max_length=100, blank=False, null=False, unique=True
    )

    def __str__(self):
        return self.name


class ProductDetail(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    description = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name


class RetailStore(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.name


class Retailer(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.name


class Product(models.Model):
    product = models.ForeignKey(ProductDetail, on_delete=models.PROTECT)
    retailer = models.ForeignKey(Retailer, on_delete=models.PROTECT)
    retail_store = models.ForeignKey(RetailStore, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"


class Promotion(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    promotion_type = models.CharField(
        max_length=100, choices=PROMOTION_TYPE, null=False
    )
    promotion_on_type = models.CharField(
        max_length=100, choices=PROMOTION_ON_TYPE, null=False
    )
    value = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    start_date = models.DateField()
    end_date = models.DateField()
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, null=True)
    product = models.ForeignKey(
        ProductDetail, on_delete=models.PROTECT, null=True
    )
    retailer = models.ForeignKey(Retailer, on_delete=models.PROTECT, null=True)
    retail_store = models.ForeignKey(
        RetailStore, on_delete=models.PROTECT, null=True
    )

    def __str__(self):
        return f"PROMOTION: {self.name}"


class Alert(models.Model):
    product = models.ForeignKey(ProductDetail, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True, blank=True)
    alert_type = models.CharField(
        choices=ALERT_TYPE, max_length=50, blank=False
    )
    desc = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Alert: {self.desc}"
