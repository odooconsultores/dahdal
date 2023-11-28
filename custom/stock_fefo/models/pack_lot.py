from odoo import fields, models, api


class PosOrderLineLot(models.Model):
    _inherit = "pos.pack.operation.lot"

    expiration_date = fields.Datetime(string="Expiration Date")

    def _export_for_ui(self, lot):
        return {
            'lot_name': lot.lot_name,
            'expiration_date': lot.expiration_date.date().strftime('%d-%m-%Y'),
        }

    def export_for_ui(self):
        return self.mapped(self._export_for_ui) if self else []
