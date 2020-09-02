from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, AuctionListing, Categories, category_options, Bid, UsersAuction, AuctionCategories, Watchlist, Comments
from .forms import ListingForm

def index(request):
    listings = []
    bids = []
    closedListings = []
    closedBids = []
    if 'user' in request.session and request.session['user'] is not None:
        user = User.objects.get(id=request.session['user'])
        
        listings += AuctionListing.objects.filter(active=True).values()
        closedL = AuctionListing.objects.filter(active=False).values()

        for listing in listings:
            bids += Bid.objects.filter(id=listing['currentBid_id']).values_list('bid', flat=True)

        for closedListing in closedL:
            bid = Bid.objects.filter(id=closedListing['currentBid_id']).values_list('bid', flat=True)
            bidder = Bid.objects.filter(id=closedListing['currentBid_id']).get()#.values('bidder')
            
            
            if bidder.bidder == user:
                listings += AuctionListing.objects.filter(id=closedListing['id']).values()
                bids += bid
        
    return render(request, "auctions/index.html", {
        'listings': listings,
        'bids': bids,
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            request.session['user'] = user.id
            request.session.set_expiry(0)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        request.session['user'] = user.id
        request.session.set_expiry(0)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def newListing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            bid = form.cleaned_data['bid']
            image = form.cleaned_data['image']
            category = form.cleaned_data['category']

            userID = request.session['user']
            user = User.objects.get(id=userID)
            bidObj = Bid(bid=bid, bidder=user)
            bidObj.save()
            auctionItem = AuctionListing(title=title, description=description, currentBid=bidObj, image=image)
            auctionItem.save()
            userauction = UsersAuction(user=user, auctionItem=auctionItem)
            userauction.save()

            if category:
                cat = Categories(name=category, listingItem=auctionItem)
                cat.save()
                auctioncategories = AuctionCategories(auctionItem=auctionItem, category=cat)
                auctioncategories.save()

            return HttpResponseRedirect(reverse('index'))

    form = ListingForm
    return render(request, 'auctions/newListing.html', {
        'form': form
    })

def listing(request, id):
    listing = AuctionListing.objects.get(id=id)
    bid = Bid.objects.get(id=listing.currentBid_id)

    comments = Comments.objects.filter(auctionItem=listing).values_list('comment', flat=True)

    watchlist = []
    user = None
    if 'user' in request.session and request.session['user']:
        userID = request.session['user']
        user = User.objects.get(id=userID)
        watchlist = Watchlist.objects.filter(user=user).values_list('auctionItem', flat=True)

    
    userslistings = UsersAuction.objects.filter(user=user).values_list('auctionItem', flat=True)

    if request.method == 'POST':
        #if 'add' in request.POST:
        if request.POST.get('add'):
            Watchlist.objects.create(user=user, auctionItem=listing)
        elif request.POST.get('remove'):
            removedItem = Watchlist.objects.get(auctionItem=listing.id)
            removedItem.delete()
        elif request.POST.get('newBid'):
            newBid = float(request.POST.get('bid'))
            Bid.objects.get(id=listing['currentBid_id']).update(bid=newBid)
            return HttpResponseRedirect(reverse('index'))
        elif request.POST.get('close'):
            AuctionListing.objects.filter(id=id).update(active=False)
        elif request.POST.get('commentBtn'):
            if user:
                Comments.objects.create(user=user, auctionItem=listing, comment=str(request.POST.get('comment')))
                return HttpResponseRedirect(reverse('index'))
        
    return render(request, 'auctions/listing.html', {
        'listing': listing,
        'bid': bid,
        'watchlist': watchlist,
        'userslistings': userslistings,
        'comments': comments
    })

def watchlist(request):
    user = None
    watchlist = []
    bids = []
    if 'user' in request.session and request.session['user']:
        user = User.objects.get(id=request.session['user'])
        watchlistIDs = Watchlist.objects.filter(user=user).values_list('auctionItem', flat=True)
        
        for listingID in watchlistIDs:
            listing = AuctionListing.objects.filter(id=listingID).values()
            watchlist += listing
            bids += Bid.objects.filter(id=listing[0]['currentBid_id']).values_list('bid', flat=True)
        return render(request, 'auctions/watchlist.html', {
            'watchlist': watchlist,
            'bids': bids
        })
