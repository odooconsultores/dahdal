from odoo import fields, models, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    auto_select_lots = fields.Boolean(string="Lotes automaticos")
