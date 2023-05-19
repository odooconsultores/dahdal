# -*- coding: utf-8 -*-

from odoo import models


class Website(models.Model):
    _inherit = 'website'

    def _get_pricelist_available(self, req, show_visible=False):
        prices = super()._get_pricelist_available(req, show_visible=show_visible)
        partner = self.env.user.partner_id
        partner_pl = partner.property_product_pricelist
        return partner_pl or self.env.ref('product.list0') or prices
