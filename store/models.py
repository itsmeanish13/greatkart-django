from django.db import models
from django.urls import reverse


# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_image = models.ImageField(upload_to='photos/products', blank=True)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    category = models.ForeignKey('category.Category', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'
    
    def get_url(self):
        
        return reverse('product_detail', args=[self.category.slug, self.slug])
    
    def __str__(self):
        return self.product_name

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)
    
variation_category_choice = (   
    ('color', 'color'),
    ('size', 'size'),
)
    
class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100,choices=variation_category_choice) #category of variation
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)
    
    objects = VariationManager()
    
    class Meta:
        verbose_name = 'variation'
        verbose_name_plural = 'variations'
    
    def __str__(self):
        return f"{self.variation_category}: {self.variation_value}"