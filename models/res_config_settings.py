from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    custom_product_creation = fields.Boolean(
        string="Allow Custom Product Creation",
        config_parameter='pd_dynamic_bom.custom_product_creation',
        help="Allow users to create custom products directly from sale order lines."
    )