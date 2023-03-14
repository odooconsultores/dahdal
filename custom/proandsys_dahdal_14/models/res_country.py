# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    region = fields.Boolean(string="Region", help="Si está marcado entonces es una Región. De lo contrario es una comuna")


class ResCountry(models.Model):
    _inherit = 'res.country'

    def get_website_sale_states(self, mode='billing'):
        res = super().get_website_sale_states(mode=mode)

        states = self.env['res.country.state'].search([('country_id', '=', self.id), ('region', '=', False)])
        res = res & states
        return res
