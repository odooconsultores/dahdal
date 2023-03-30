from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    web_description = fields.Text(string="Descripcion Web",
                                  help="Breve reseña del producto que se mostrará en el sitio web")
