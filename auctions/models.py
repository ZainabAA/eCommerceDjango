from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


category_options = [('fashion', 'fashion'), ('home', 'home'),
                    ('toys', 'toys'), ('electronics', 'electronics')]

class User(AbstractUser):
    pass


class Bid(models.Model):
    bid = models.PositiveIntegerField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bid')


class AuctionListing(models.Model):
    image = models.TextField(blank=True)
    description = models.TextField()
    title = models.TextField()
    currentBid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name='auction')
    active = models.BooleanField(default=True)


class Categories(models.Model):
    name = models.TextField(category_options)
    listingItem = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name='category')


class Comments(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_comment')
    auctionItem = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name='auction_comment')
    comment = models.TextField()


class UsersAuction(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='auctionListing')
    auctionItem = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name='owner')


class AuctionCategories(models.Model):
    auctionItem = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name='categories')
    category = models.ForeignKey(
        Categories, on_delete=models.CASCADE, related_name='auctionItems')


class Watchlist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='watchlist')
    auctionItem = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name='watchlist')
