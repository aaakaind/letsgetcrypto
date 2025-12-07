from decimal import Decimal
from typing import Optional
from django.db import models


class WatchlistItem(models.Model):
    """Model to store user's cryptocurrency watchlist with comprehensive metadata"""
    
    # Basic identification
    coin_id = models.CharField(max_length=100, db_index=True, unique=True)
    coin_name = models.CharField(max_length=200)
    coin_symbol = models.CharField(max_length=20, db_index=True)
    
    # Timestamps
    added_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)
    
    # Price tracking
    last_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    
    # Additional metadata for extended cryptocurrency support
    market_cap = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    volume_24h = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    price_change_24h = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    circulating_supply = models.DecimalField(max_digits=30, decimal_places=8, null=True, blank=True)
    total_supply = models.DecimalField(max_digits=30, decimal_places=8, null=True, blank=True)
    max_supply = models.DecimalField(max_digits=30, decimal_places=8, null=True, blank=True)
    
    # Additional metadata
    description = models.TextField(blank=True, null=True)
    website_url = models.URLField(max_length=500, blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    
    # User preferences
    is_favorite = models.BooleanField(default=False, db_index=True)
    alert_enabled = models.BooleanField(default=False)
    alert_price_threshold = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    
    class Meta:
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['coin_symbol', '-added_at']),
            models.Index(fields=['is_favorite', '-added_at']),
            models.Index(fields=['-last_updated']),
        ]
    
    def __str__(self) -> str:
        return f"{self.coin_name} ({self.coin_symbol.upper()})"
    
    def get_price_change_percentage(self) -> Optional[float]:
        """Get price change as a percentage"""
        if self.price_change_24h is not None:
            return float(self.price_change_24h)
        return None
    
    def update_price_data(self, price: Decimal, market_cap: Optional[Decimal] = None, 
                         volume_24h: Optional[Decimal] = None, 
                         price_change_24h: Optional[Decimal] = None) -> None:
        """Update price and related data"""
        self.last_price = price
        if market_cap is not None:
            self.market_cap = market_cap
        if volume_24h is not None:
            self.volume_24h = volume_24h
        if price_change_24h is not None:
            self.price_change_24h = price_change_24h
        self.save()
