from django.contrib import admin

from .models import User, AuctionListing, Bid, Categories, Comments, UsersAuction, AuctionCategories, Watchlist

# Register your models here.
admin.site.register(User)
admin.site.register(AuctionListing)
admin.site.register(Bid)
admin.site.register(Categories)
admin.site.register(Comments)
admin.site.register(UsersAuction)
admin.site.register(AuctionCategories)
admin.site.register(Watchlist)