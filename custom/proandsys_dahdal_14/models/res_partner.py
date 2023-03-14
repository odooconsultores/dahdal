from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_region = fields.Many2one(domain=[('region', '=', True)])
    state_id = fields.Many2one(domain=[('region', '=', False)])
