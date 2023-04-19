# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import http
import requests
import json
import logging
from odoo.exceptions import UserError
from odoo.addons.l10n_cl_enviame.controllers.main import WebsiteSaleDeliverySend
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSale(WebsiteSale):

    def _get_shop_payment_values(self, order, **kwargs):
        values = super()._get_shop_payment_values(order, **kwargs)
        default_acquirer = request.env.ref('payment_webpay_plus.payment_acquirer_transbank')
        if default_acquirer in values['acquirers']:
            values['acquirers'].remove(default_acquirer)
            values['acquirers'].insert(0, default_acquirer)
        return values


class WebsiteDeliverySend(WebsiteSaleDeliverySend):


    def _update_website_sale_delivery_return(self, order, **post):
        # reewrite all method
        config = request.env['ir.config_parameter'].sudo()
        weight = 0.0
        carrier = request.env['delivery.carrier'].sudo().browse(int(post['carrier_id']))
        if order and carrier.is_send and config.get_param('is_env'):
            value = self.return_values_your_env()
            header = {
                "x-api-key": value.get('x-api-key') if value.get('x-api-key') else config.get_param('api_key'),
                "Accept": "application/json"
            }

            for sale in order.order_line.filtered(lambda x: x.is_delivery is False):
                weight += sale.product_id.weight * sale.product_uom_qty

            options = '?weight=' + str(weight) + '&from_place=' + str(order.warehouse_id.partner_id.city) +\
                      '&to_place=' + str(order.partner_shipping_id.city)
            # _logger.info('\n\n\n url enviame: %s \n\n\n' % options)
            response = value.get('url_price')+options
            r = requests.get(response, headers=header)
            data = json.loads(r.text.encode('utf8'))
            for t in data.get('data', []):
                # if carrier.delivery_request.code == t['carrier']:
                amount_delivery = t['services'][0]['price']
                amount_delivery_untax = amount_delivery * 1.01
                order.amount_delivery = amount_delivery * 1.01 * 1.19
                amount_untaxed = amount_tax = 0
                for line in order.order_line:
                    amount_untaxed += line.price_subtotal if not line.is_delivery else 0
                    amount_tax += line.price_tax if not line.is_delivery else 0
                order.amount_untaxed = amount_untaxed + amount_delivery_untax
                order.amount_tax = amount_tax + (amount_delivery_untax * 0.19)
                order.amount_total = amount_untaxed + amount_delivery_untax + order.amount_tax
            if order.amount_delivery == 1 or order.amount_delivery == 0.0:
                raise UserError("Disculpe!!! El servicio de envio no esta disponible para esta Comuna")
            for sale in order.order_line.filtered(lambda x: x.is_delivery is True):
                sale.price_unit = order.amount_delivery

        # static call
        Monetary = request.env['ir.qweb.field.monetary']
        carrier_id = int(post['carrier_id']) if post.get('carrier_id') else False
        currency = order.currency_id
        if order:
            return {
                'status': order.delivery_rating_success,
                'error_message': order.delivery_message,
                'carrier_id': carrier_id,
                'is_free_delivery': not bool(order.amount_delivery),
                'new_amount_delivery': Monetary.value_to_html(order.amount_delivery,
                                                              {'display_currency': currency}),
                'new_amount_untaxed': Monetary.value_to_html(order.amount_untaxed, {'display_currency': currency}),
                'new_amount_tax': Monetary.value_to_html(order.amount_tax, {'display_currency': currency}),
                'new_amount_total': Monetary.value_to_html(order.amount_total, {'display_currency': currency}),
            }
        return {}

