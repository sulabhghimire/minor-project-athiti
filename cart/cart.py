from django.conf import settings
from listings.models import Listing
from decimal import Decimal
from cart.models import Taxe
import datetime
from datetime import date
from listings.booking_functions.availability import check_availability


class Cart(object):

    def __init__(self, request):
        self.session    = request.session
        cart            = self.session.get(settings.CART_SESSION_KEY)
        if not cart:
            cart        = self.session[settings.CART_SESSION_KEY] = {}
        self.cart       = cart

    def add(self, listing, check_in, check_out, days):
        listing_id         = listing.id
        self.cart.clear()
        self.cart[listing_id] = {'check_in': check_in, 'check_out' : check_out, 'days': days, 'price': str(listing.price)}
        self.save()

    def save(self):
        self.session.modified   = True

    def delete(self, product_id):
        pid = str(product_id)
        del self.cart[pid]
        self.save()

    def list(self):
        carts   = []
        for product_id in self.cart.keys():
            obj             = Listing.objects.get(id=product_id)
            check_in_date   = datetime.datetime.strptime(self.cart[product_id]['check_in'], '%Y-%m-%d').date()
            check_out_date  = datetime.datetime.strptime(self.cart[product_id]['check_out'], '%Y-%m-%d').date()
            

            available  = check_availability(obj.id, check_in_date, check_out_date)

            if available:
                tmp_cart = {
                    'id'        : product_id,
                    'obj'       : obj,
                    'check_in'  : self.cart[product_id]['check_in'],
                    'check_out' : self.cart[product_id]['check_out'],
                    'days'      : self.cart[product_id]['days'],
                    'price'     : Decimal(self.cart[product_id]['days']*obj.price)
                }
                carts.append(tmp_cart)
        return carts
    
    def sum_amount(self):
        sum = 0
        for product_id in self.cart.keys():
            obj     = Listing.objects.get(id=product_id)
            sum = sum + Decimal(self.cart[product_id]['days']*obj.price)
        return sum
    
    def get_tax_percentage(self):
        obj         = Taxe.objects.get(id=1)
        return obj.tax_percentage

    def get_tax_amount(self):
        obj         = Taxe.objects.get(id=1)
        tax_amount  = Decimal(self.sum_amount() / 100) * obj.tax_percentage
        return tax_amount

    def get_service_tax_percentage(self):
        obj         = Taxe.objects.get(id=1)
        return obj.service_charge_percentage

    def get_service_tax_amount(self):
        obj     = Taxe.objects.get(id=1)
        service_tax_amount  = Decimal(self.sum_amount() / 100) * obj.service_charge_percentage
        return service_tax_amount

    def get_total_amount(self):
        return self.sum_amount() + self.get_tax_amount() + self.get_service_tax_amount()
