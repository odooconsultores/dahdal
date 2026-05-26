# -*- coding:utf-8 -*- 

from odoo import models,fields,api,_  



class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"


    def fixed_rate_shipment(self, order):
        carrier = self._match_address(order.partner_shipping_id)
        res = super(DeliveryCarrier,self).fixed_rate_shipment(order)
        if not carrier:
            return res
        else:
            if self.amount and self.delivery_request:
                res['price'] = self.amount * 1.19
                return res
            else :
                return res