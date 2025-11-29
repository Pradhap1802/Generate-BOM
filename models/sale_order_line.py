from odoo import fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    length_in_inches = fields.Float(
        string="Length(Inches)",
    )
    width_in_inches = fields.Float(
        string="Width(Inches)",
    )