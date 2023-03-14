from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleDahdal(WebsiteSale):

    def _get_mandatory_fields_shipping(self, country_id=False):
        res = super()._get_mandatory_fields_shipping(country_id)
        res.remove('zip')
        return res

    def _get_mandatory_fields_billing(self, country_id=False):
        res = super()._get_mandatory_fields_billing(country_id)
        res.remove('zip')
        return res

    def _get_country_related_render_values(self, kw, render_values):
        # always country Chile
        mode = render_values['mode']
        country = request.env['res.country'].search(['|', ('code', '=', 'cl'), ('name', 'ilike', 'Chile')], limit=1)

        res = {
            'country': country,
            'country_states': country.get_website_sale_states(mode=mode[1]),
            'countries': country.get_website_sale_countries(mode=mode[1]),
        }
        return res
