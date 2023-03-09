# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import http
import requests
import json
import logging
from odoo.exceptions import UserError
from odoo.addons.l10n_cl_enviame.controllers.main import WebsiteSaleDeliverySend

class WebsiteDeliverySend(WebsiteSaleDeliverySend):

    def _update_website_sale_delivery_return(self, order, **post):
        res = super(WebsiteDeliverySend, self)._update_website_sale_delivery_return(order, **post)
        Monetary = request.env['ir.qweb.field.monetary']
        config = request.env['ir.config_parameter'].sudo()
        carrier = request.env['delivery.carrier'].sudo().browse(int(post['carrier_id']))
        if order and carrier.is_send and config.get_param('is_env'):
            amount_delivery = order.amount_delivery + 1  # return the changes on l10n_cl_enviame
            amount_delivery_untax = amount_delivery * 1.01
            order.amount_delivery = amount_delivery * 1.01 * 1.19
            amount_untaxed = amount_tax = 0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal if not line.is_delivery else 0
                amount_tax += line.price_tax if not line.is_delivery else 0
            order.amount_untaxed = amount_untaxed + amount_delivery_untax
            order.amount_tax = amount_tax + (amount_delivery_untax * 0.19)
            order.amount_total = amount_untaxed + amount_delivery_untax + order.amount_tax
            res.update({
                'new_amount_delivery': Monetary.value_to_html(order.amount_delivery, {'display_currency': order.currency_id}),
                'new_amount_untaxed': Monetary.value_to_html(order.amount_untaxed, {'display_currency': order.currency_id}),
                'new_amount_tax': Monetary.value_to_html(order.amount_tax, {'display_currency': order.currency_id}),
                'new_amount_total': Monetary.value_to_html(order.amount_total, {'display_currency': order.currency_id}),
            })

        return res
