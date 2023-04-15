from odoo import http, fields
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleDahdal(WebsiteSale):

    def _get_mandatory_fields_shipping(self, country_id=False):
        res = super()._get_mandatory_fields_shipping(country_id)
        if 'zip' in res:
            res.remove('zip')
        return res

    def _get_mandatory_fields_billing(self, country_id=False):
        res = super()._get_mandatory_fields_billing(country_id)
        if 'zip' in res:
            res.remove('zip')
        return res

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        country = request.env['res.country'].search(['|', ('code', '=', 'cl'), ('name', 'ilike', 'Chile')], limit=1)
        kw.update({'country_id': str(country.id)})
        return super().address(**kw)

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

    @http.route(['/shop/cart'], type='http', auth="public", website=True, sitemap=False)
    def cart(self, access_token=None, revive='', **post):
        if post.get('return_id'):
            order = request.env['sale.order'].sudo().browse(int(post['return_id']))
            order.action_draft()
            # Important: without this the order disappears from the website
            order.sudo().transaction_ids.write({'state': 'draft'})
            request.session['sale_order_id'] = order.id
            values = {
                'website_sale_order': order,
                'date': fields.Date.today(),
                'suggested_products': [],
                'access_token': order.access_token,
            }
            return request.render("website_sale.cart", values)
        return super().cart(access_token, revive, **post)
