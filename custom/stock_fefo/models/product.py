from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    removal_strategy_id = fields.Many2one(
        'product.removal', 'Force Removal Strategy',
        help="Set a specific removal strategy that will be used regardless of the source location for this product category")


class ProductProduct(models.Model):
    _inherit = "product.product"

    def get_lot_id(self, config, lot_names):
        self.ensure_one()
        config_id = self.env['pos.config'].browse(config)
        location = config_id.picking_type_id.default_location_src_id
        quants = self.env['stock.quant']._gather(self, location, strict=False)
        for quant in quants:
            quatity_order = sum(x[1] for x in lot_names if x[0] == quant.lot_id.name)
            if quatity_order < quant.available_quantity:
                if quant and quant.filtered(lambda x: x.quantity > 0):
                    quant = quant.filtered(lambda x: x.quantity > 0)
                    lot_name = quant[0].lot_id.name
                    return lot_name
        return False
