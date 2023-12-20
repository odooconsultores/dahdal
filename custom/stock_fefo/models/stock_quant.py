from odoo import fields, models, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _get_removal_strategy(self, product_id, location_id):
        if product_id.removal_strategy_id:
            return product_id.removal_strategy_id.method
        return super()._get_removal_strategy(product_id, location_id)
