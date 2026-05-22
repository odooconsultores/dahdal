# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import http
import requests
import json
import logging
from odoo.exceptions import UserError
from odoo.addons.l10n_cl_enviame.controllers.main import WebsiteSaleDeliverySend
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)

def _get_values_your_env(firma_state):
    config = request.env['ir.config_parameter'].sudo()
    if firma_state == 'test':
        return {
            'url_price': 'https://facturacion.enviame.io/api/v1/prices',
            'delivery_url': 'https://stage.api.enviame.io/api/s2/v2/companies/{0}/deliveries'
            .format(config.get_param('id_company')),
            'pickup_url': 'https://stage.api.enviame.io/api/s2/v2/companies/{0}/pickups'
            .format(config.get_param('id_company')),
            'api_key': config.get_param('api_key'),
            'warehouse_code': config.get_param('warehouse_code'),
            'n_package': config.get_param('n_package'),
        }
    else:
        return {
            'api_key': config.get_param('api_key'),
            'url_price': 'https://facturacion.enviame.io/api/v1/prices',
            'delivery_url': 'https://api.enviame.io/api/s2/v2/companies/{0}/deliveries'
            .format(config.get_param('id_company')),
            'pickup_url': 'https://api.enviame.io/api/s2/v2/companies/{0}/pickups'
            .format(config.get_param('id_company')),
            'warehouse_code': config.get_param('warehouse_code'),
            'n_package': config.get_param('n_package'),
        }

class WebsiteSale(WebsiteSale):

    def _get_data_api_enviame(self,order,config):
        value = self.return_values_your_env()
        header = {
            "x-api-key": value.get('x-api-key') if value.get('x-api-key') else config.get_param('api_key'),
            "Accept": "application/json"
        }
        weight = 0
        for sale in order.order_line.filtered(lambda x: x.is_delivery is False):
            weight += sale.product_id.weight * sale.product_uom_qty

        options = '?weight=' + str(weight) + '&from_place=' + str(order.warehouse_id.partner_id.city) +\
                    '&to_place=' + str(order.partner_shipping_id.state_id.name)
        # _logger.info('\n\n\n url enviame: %s \n\n\n' % options)
        response = value.get('url_price')+options
        _logger.info('RESPONSE:%s',response)
        r = requests.get(response, headers=header)
        data = json.loads(r.text.encode('utf8'))
        _logger.info('DATA:%s',data)
        return data



    def _get_shop_payment_values(self, order, **kwargs):
        values = super()._get_shop_payment_values(order, **kwargs)
        default_acquirer = request.env.ref('payment_webpay_plus.payment_acquirer_transbank')
        config = request.env['ir.config_parameter'].sudo()
        if default_acquirer in values['acquirers']:
            values['acquirers'].remove(default_acquirer)
            values['acquirers'].insert(0, default_acquirer)
        if values.get('deliveries',False):
            data = self._get_data_api_enviame(order,config)
            deliveries = values.get('deliveries')
            carriers = [{'name':delivery.get('carrier',False),'price':delivery.get('services',[])[0].get('price',0.0)} for delivery in data.get('data', [])]
            for carrier in carriers:
                carrier_req = deliveries.filtered( lambda c: c.delivery_request.code == carrier.get('name'))
                if carrier_req:
                    carrier_req.amount = carrier.get('price') * 1.01

        return values


class WebsiteDeliverySend(WebsiteSaleDeliverySend):

    def return_values_your_env(self):
        config = request.env['ir.config_parameter'].sudo().get_param('state_env')
        url = _get_values_your_env(config)
        return url
    
    def _get_data_api_enviame(self,order,config):
        value = self.return_values_your_env()
        header = {
            "x-api-key": value.get('x-api-key') if value.get('x-api-key') else config.get_param('api_key'),
            "Accept": "application/json"
        }

        for sale in order.order_line.filtered(lambda x: x.is_delivery is False):
            weight += sale.product_id.weight * sale.product_uom_qty

        options = '?weight=' + str(weight) + '&from_place=' + str(order.warehouse_id.partner_id.city) +\
                    '&to_place=' + str(order.partner_shipping_id.state_id.name)
        # _logger.info('\n\n\n url enviame: %s \n\n\n' % options)
        response = value.get('url_price')+options
        _logger.info('RESPONSE:%s',response)
        r = requests.get(response, headers=header)
        data = json.loads(r.text.encode('utf8'))
        _logger.info('DATA:%s',data)
        return data


    def _update_website_sale_delivery_return(self, order, **post):
        # reewrite all method
        config = request.env['ir.config_parameter'].sudo()
        weight = 0.0
        carrier = request.env['delivery.carrier'].sudo().browse(int(post['carrier_id']))
        # carriers  = request.env['delivery.carrier'].sudo().search([('active','=',True)])
        if order and carrier.is_send and config.get_param('is_env'):
            
            data = self._get_data_api_enviame(order ,config)
            _logger.info('DATA:%s',data)
            # deliverys = [{'name':delivery.get('carrier',False),'price':delivery.get('services',[])[0].get('price',0.0)} for delivery in data.get('data', [])]
            for t in data.get('data', []):
                if carrier.delivery_request.code == t['carrier']:
                    amount_delivery = t['services'][0]['price']
                    amount_delivery_untax = amount_delivery * 1.01 # monto sin impuesto
                    order.amount_delivery = amount_delivery * 1.01 * 1.19 # monto de entrega con impuesto
                    amount_untaxed = amount_tax = 0
                    carrier.fixed_price = amount_delivery_untax 
                    for line in order.order_line:
                        amount_untaxed += line.price_subtotal if not line.is_delivery else 0
                        amount_tax += line.price_tax if not line.is_delivery else 0
                    order.amount_untaxed = amount_untaxed + amount_delivery_untax
                    order.amount_tax = amount_tax + (amount_delivery_untax * 0.19)
                    order.amount_total = amount_untaxed + amount_delivery_untax + order.amount_tax
            # for  delivery in deliverys:
            #     carrier_req = carriers.filtered( lambda c: c.delivery_request.code == delivery.get('name'))
            #     if carrier_req:
            #         carrier_req.fixed_price = delivery.get('price') * 1.01
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

