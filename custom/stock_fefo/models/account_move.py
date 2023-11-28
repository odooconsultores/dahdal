from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    lot_ids = fields.Many2many(
        'stock.production.lot', string='Lot/Serial Number', index=True, store=True,
        ondelete='restrict', check_company=True, compute="_compute_lot_id")

    @api.depends('product_id', 'move_id', 'move_id.pos_order_ids')
    def _compute_lot_id(self):
        for line in self:
            lot_id = False
            inv = line.move_id
            if inv.move_type in ['out_invoice', 'out_refund']:
                lines = inv.mapped('pos_order_ids.lines')
                if lines:
                    pack_lots = lines.filtered(lambda l: l.product_id == line.product_id).mapped('pack_lot_ids.lot_name')
                    lot_id = self.env['stock.production.lot'].search([
                        ('product_id', '=', line.product_id.id),
                        ('name', 'in', pack_lots),
                    ])
            line.lot_ids = lot_id
