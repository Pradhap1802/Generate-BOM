from odoo import fields, models, api

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    is_custom = fields.Boolean(
        string="Custom BOM",
        default=False,
    )
    custom_product_creation_setting = fields.Boolean(
        string="Custom Product Creation Setting",
        compute='_compute_custom_product_creation_setting',
        store=False,
        readonly=True,
    )

    @api.depends('company_id')
    def _compute_custom_product_creation_setting(self):
        for bom in self:
            bom.custom_product_creation_setting = self.env['ir.config_parameter'].sudo().get_param(
                'pd_dynamic_bom.custom_product_creation', 'False'
            ).lower() == 'true'