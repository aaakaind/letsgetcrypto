from django.db import models


class WatchlistItem(models.Model):
    """Model to store user's cryptocurrency watchlist"""
    
    coin_id = models.CharField(max_length=100, db_index=True)
    coin_name = models.CharField(max_length=200)
    coin_symbol = models.CharField(max_length=20)
    added_at = models.DateTimeField(auto_now_add=True)
    last_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-added_at']
        unique_together = ['coin_id']
    
    def __str__(self):
        return f"{self.coin_name} ({self.coin_symbol.upper()})"
