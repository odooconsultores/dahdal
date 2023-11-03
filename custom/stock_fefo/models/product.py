from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    removal_strategy_id = fields.Many2one(
        'product.removal', 'Force Removal Strategy',
        help="Set a specific removal strategy that will be used regardless of the source location for this product category")


class ProductProduct(models.Model):
    _inherit = "product.product"

    def get_lot_id(self, config):
        self.ensure_one()
        config_id = self.env['pos.config'].browse(config)
        location = config_id.picking_type_id.default_location_src_id
        quant = self.env['stock.quant']._gather(self, location, strict=False)
        if quant:
            lot_name = quant[0].lot_id.name
            return lot_name
        return False
