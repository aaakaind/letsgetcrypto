from django.urls import path
from . import views

app_name = 'crypto_api'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Health check endpoints
    path('health/', views.health_check, name='health_check'),
    path('readiness/', views.readiness_check, name='readiness_check'),
    path('liveness/', views.liveness_check, name='liveness_check'),
    
    # Crypto data endpoints
    path('price/<str:symbol>/', views.get_crypto_price, name='crypto_price'),
    path('history/<str:symbol>/', views.get_crypto_history, name='crypto_history'),
    path('market/', views.get_market_overview, name='market_overview'),
    
    # Search and watchlist endpoints
    path('search/', views.search_crypto, name='search_crypto'),
    path('watchlist/', views.get_watchlist, name='get_watchlist'),
    path('watchlist/add/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/<str:coin_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
]