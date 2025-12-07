from typing import List, Optional, Tuple
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from .models import WatchlistItem


@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    """Admin interface for WatchlistItem model"""
    
    list_display: List[str] = [
        'coin_name',
        'coin_symbol',
        'last_price',
        'price_change_24h',
        'market_cap',
        'is_favorite',
        'alert_enabled',
        'added_at',
        'last_updated'
    ]
    
    list_filter: List[str] = [
        'is_favorite',
        'alert_enabled',
        'added_at',
        'last_updated'
    ]
    
    search_fields: List[str] = [
        'coin_id',
        'coin_name',
        'coin_symbol',
        'description'
    ]
    
    readonly_fields: List[str] = [
        'coin_id',
        'added_at',
        'last_updated'
    ]
    
    fieldsets: List[Tuple[Optional[str], dict]] = [
        ('Basic Information', {
            'fields': ('coin_id', 'coin_name', 'coin_symbol', 'description')
        }),
        ('Price Data', {
            'fields': ('last_price', 'price_change_24h', 'market_cap', 'volume_24h')
        }),
        ('Supply Information', {
            'fields': ('circulating_supply', 'total_supply', 'max_supply'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('website_url', 'image_url'),
            'classes': ('collapse',)
        }),
        ('User Preferences', {
            'fields': ('is_favorite', 'alert_enabled', 'alert_price_threshold')
        }),
        ('Timestamps', {
            'fields': ('added_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    ]
    
    ordering: List[str] = ['-added_at']
    
    
    actions: List[str] = ['mark_as_favorite', 'unmark_as_favorite', 'enable_alerts', 'disable_alerts']
    
    @admin.action(description='Mark selected items as favorite')
    def mark_as_favorite(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Mark items as favorite"""
        updated = queryset.update(is_favorite=True)
        self.message_user(request, f'{updated} items marked as favorite.')
    
    @admin.action(description='Unmark selected items as favorite')
    def unmark_as_favorite(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Unmark items as favorite"""
        updated = queryset.update(is_favorite=False)
        self.message_user(request, f'{updated} items unmarked as favorite.')
    
    @admin.action(description='Enable alerts for selected items')
    def enable_alerts(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Enable alerts"""
        updated = queryset.update(alert_enabled=True)
        self.message_user(request, f'Alerts enabled for {updated} items.')
    
    @admin.action(description='Disable alerts for selected items')
    def disable_alerts(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Disable alerts"""
        updated = queryset.update(alert_enabled=False)
        self.message_user(request, f'Alerts disabled for {updated} items.')

