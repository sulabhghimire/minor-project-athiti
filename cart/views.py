from django.contrib.auth.models import User
from django.db.models.query_utils import subclasses
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import to_language
import requests, jason
from django.views.generic import View

from django.http import JsonResponse

from .cart import Cart
from listings.models import Listing, Booking
from listings.forms import AvailabilityForm

import datetime
from datetime import date
from django.contrib import messages
from listings.booking_functions.availability import check_availability
from decimal import Decimal
from django.contrib.auth.decorators import user_passes_test

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import EmailMultiAlternatives, message
from core import settings

import threading

class EmailThread(threading.Thread):

    def __init__(self, email, messages, filename, pdf):
        self.email      = email
        self.messages   = messages
        self.filename   = filename
        self.pdf        = pdf
        threading.Thread.__init__(self)

    def run(self):
        self.email.attach_alternative(self.messages, "text/html")
        self.email.attach(self.filename, self.pdf, 'application/pdf')
        self.email.send(fail_silently=False)


@login_required
@user_passes_test(lambda user: user.guest)
def cart_display(request):
    cart = Cart(request)
    context = {
        'cart' : cart
    }
    return render(request, 'cart/cart.html', context)

@login_required
@user_passes_test(lambda user: user.guest)
def add_to_cart(request, pk):
    if request.method == 'POST':
        listing   = Listing.objects.get(id = pk)
        check_in  = date.fromisoformat(request.POST['check_in'])
        check_out = date.fromisoformat(request.POST['check_out'])
        days      = (check_out-check_in).days
        rooms     = Listing.objects.filter(id=pk)
        available_rooms = []
        if check_in < date.today():
            messages.info(request, f'You can\'t checkin in past.')
        elif check_out < date.today():
            messages.info(request, f'You can\'t checkout in past.')
        elif check_out< check_in:
            messages.info(request, f'Check Out Date can\'t be earlier than Check In date.')    
        else:
            for room in rooms:
                if check_availability(room.id, check_in, check_out):
                    available_rooms.append(room)
            
            if len(available_rooms)>0:
                check_in  = str(check_in)
                check_out = str(check_out)
                cart      = Cart(request)
                cart.add(listing, check_in, check_out, days)
                return redirect('display_cart')
            else:
                messages.success(request, f'Room is not available.')
        form    = AvailabilityForm(request.POST)
        obj     = Listing.objects.get(id = pk)
        return render(request, 'listings/listing_details.html', {'form': form, 'object':obj})

@login_required
def delete_cart(request, pk):
    cart    = Cart(request)
    cart.delete(pk)
    context = {
        'cart' : cart
    }
    return redirect('display_cart')

class GenerateInvoice(View):
    def get(self, request, pk, uid, *args, **kwargs):
        try:
            booking = Booking.objects.get(id = pk, uuid=uid)  
        except:
            return HttpResponse("505 Not Found")
        data = {
            'order_id'                : booking.uuid,
            'room_host_id'            : booking.room_host_id,
            'room_host_full_name'     : booking.room_host_full_name,
            'user_id'                 : booking.user_id,
            'user_email'              : booking.user_email,
            'user_full_name'          : booking.user_full_name,
            'room_id'                 : booking.room_id,
            'room_host_email'         : booking.room_host_email,
            'room_host_phone'         : booking.room_host_phone,
            'room_city'               : booking.room_city,
            'room_exact_address'      : booking.room_exact_address,
            'idx'                     : booking.idx,
            'check_in'                : booking.check_in,
            'check_out'               : booking.check_out,
            'total_amount'            : booking.total_amount,
            'sum_amount'              : booking.sum_amount,
            'tax_amount'              : booking.tax_amount,
            'service_charge_amount'   : booking.service_charge_amount,
            'date'                    : booking.date_booked,
            'days'                    : (booking.check_out - booking.check_in).days,
            'status'                  : booking.booking_progres,
        }
        pdf = render_to_pdf('cart/payments/invoice.html', data)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" %(data['order_id'])
            content = "inline; filename='%s'" %(filename)
            content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")

class MailInvoice(View):
    def get(self, request, pk, uid, *args, **kwargs):
        try:
            booking = Booking.objects.get(id = pk, uuid=uid)  
        except:
            return HttpResponse("505 Not Found")
        invoice_data = {
            'order_id'                : booking.uuid,
            'room_host_id'            : booking.room_host_id,
            'room_host_full_name'     : booking.room_host_full_name,
            'user_id'                 : booking.user_id,
            'user_email'              : booking.user_email,
            'user_full_name'          : booking.user_full_name,
            'room_id'                 : booking.room_id,
            'room_host_email'         : booking.room_host_email,
            'room_host_phone'         : booking.room_host_phone,
            'room_city'               : booking.room_city,
            'room_exact_address'      : booking.room_exact_address,
            'idx'                     : booking.idx,
            'check_in'                : booking.check_in,
            'check_out'               : booking.check_out,
            'total_amount'            : booking.total_amount,
            'sum_amount'              : booking.sum_amount,
            'tax_amount'              : booking.tax_amount,
            'service_charge_amount'   : booking.service_charge_amount,
            'date'                    : booking.date_booked,
            'days'                    : (booking.check_out - booking.check_in).days,
            'status'                  : booking.booking_progres,
        }
        template = get_template('cart/payments/invoice.html')
        html  = template.render(invoice_data)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
        pdf = result.getvalue()
        filename = 'Invoice_' + invoice_data['idx'] + '.pdf'
        mail_subject = 'Recent Booking Details'
        context_dict = {
            'user': self.request.user,
            'order_id' : booking.uuid,
        }
        template = get_template('cart/payments/emailinvoice.html')
        message  = template.render(context_dict)
        to_email = self.request.user.email
        email = EmailMultiAlternatives(
            mail_subject,
            "About your bookings through Athiti",   
            settings.EMAIL_HOST_USER,
            [to_email]
        )
        EmailThread(email, message, filename, pdf).start()
        return redirect('guests-booking')

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

class KhaltiVerifyView(View):
    def get(self, request, *args, **kwargs):
        sucess                  = False
        token                   = request.GET.get("token")
        total_amount            = Decimal(request.GET.get("total_amount"))
        tax_amount              = Decimal(request.GET.get("tax_amount"))
        service_charge_amount   = Decimal(request.GET.get("service_charge_amount"))
        room_id                 = int(request.GET.get("room_id"))
        check_in_date           = datetime.datetime.strptime(request.GET.get("check_in"), '%Y-%m-%d')
        check_out_date          = datetime.datetime.strptime(request.GET.get("check_out"), '%Y-%m-%d')
        url = "https://khalti.com/api/v2/payment/verify/"
        payload = {
            "token": token,
            "amount": total_amount
        }
        headers = {
            "Authorization": "Key test_secret_key_bb60d301993b40ff9bbc89b0328e4d7a"
        }
        response            = requests.post(url, payload, headers = headers)
        resp_dict           = response.json()
        room_name           = Listing.objects.get(id=room_id)
        if resp_dict.get("idx"):
            sucess          = True
            booking         = Booking.objects.create(
                user_id                 = self.request.user.pk,
                user_email              = self.request.user.email,
                user_full_name          = self.request.user.full_name,
                room_id                 = room_name.pk,
                room_host_id            = room_name.user.pk,
                room_host_full_name     = room_name.user.full_name,
                room_host_email         = room_name.user.email,
                room_host_phone         = room_name.user.phone_number,
                room_city               = str(room_name.city),
                room_exact_address      = room_name.exact_address,
                idx                     = resp_dict.get("idx"),
                check_in                = check_in_date.date(),
                check_out               = check_out_date.date(),
                total_amount            = (total_amount)/100,
                sum_amount              = (total_amount)/100-tax_amount-service_charge_amount,
                tax_amount              = tax_amount,
                service_charge_amount   = service_charge_amount,
            )
            delete_cart(request, room_id)
            invoice_data    = {
                'order_id'                : booking.uuid,
                'room_host_id'            : room_name.user.pk,
                'room_host_full_name'     : room_name.user.full_name,
                'user_id'                 : self.request.user.pk,
                'user_email'              : self.request.user.email,
                'user_full_name'          : self.request.user.full_name,
                'room_id'                 : room_name.pk,
                'room_host_email'         : room_name.user.email,
                'room_host_phone'         : room_name.user.phone_number,
                'room_city'               : room_name.city,
                'room_exact_address'      : room_name.exact_address,
                'idx'                     : resp_dict.get("idx"),
                'check_in'                : check_in_date.date(),
                'check_out'               : check_out_date.date(),
                'total_amount'            : (total_amount)/100,
                'sum_amount'              : (total_amount)/100-tax_amount-service_charge_amount,
                'tax_amount'              : tax_amount,
                'service_charge_amount'   : service_charge_amount,
                'date'                    : date.today(),
                'days'                    : (check_out_date.date()-check_in_date.date()).days,
                'status'                  : 'Booked'
            }
            template = get_template('cart/payments/invoice.html')
            html  = template.render(invoice_data)
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
            pdf = result.getvalue()
            filename = 'Invoice_' + invoice_data['idx'] + '.pdf'
            mail_subject = 'Recent Booking Details'
            context = {
                'user': self.request.user,
                'order_id' : booking.uuid,
            }
            template = get_template('cart/payments/emailinvoice.html')
            message  = template.render(context)
            to_email = self.request.user.email
            email = EmailMultiAlternatives(
                mail_subject,
                "About your bookings through Athiti",       
                settings.EMAIL_HOST_USER,
                [to_email]
            )
            EmailThread(email, message, filename, pdf).start()
        data    = {
            "sucess": sucess
        }
        return JsonResponse(data)

        