from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    custom_product_creation_setting = fields.Boolean(
        string="Custom Product Creation Setting",
        compute='_compute_custom_product_creation_setting',
        store=False,
        readonly=True,
    )
    allow_custom_product_on_so = fields.Boolean(
        string="Allow Custom Product on Sales Order",
        help="If enabled, allows custom product creation for this sales order.",
    )

    @api.depends('company_id')
    def _compute_custom_product_creation_setting(self):
        for order in self:
            order.custom_product_creation_setting = self.env['ir.config_parameter'].sudo().get_param(
                'pd_dynamic_bom.custom_product_creation', 'False'
            ).lower() == 'true'

    @api.onchange('custom_product_creation_setting')
    def _onchange_custom_product_creation_setting(self):
        if not self.custom_product_creation_setting:
            self.allow_custom_product_on_so = False
        else:
            self.allow_custom_product_on_so = True

    def create(self, vals_list):
        if not isinstance(vals_list, list):
            vals_list = [vals_list]
        for vals in vals_list:
            if 'allow_custom_product_on_so' not in vals:
                custom_product_setting = self.env['ir.config_parameter'].sudo().get_param(
                    'pd_dynamic_bom.custom_product_creation', 'False'
                ).lower() == 'true'
                vals['allow_custom_product_on_so'] = custom_product_setting
        return super().create(vals_list)

    def write(self, vals):
        if 'allow_custom_product_on_so' in vals and not self.custom_product_creation_setting:
            vals['allow_custom_product_on_so'] = False
        return super().write(vals)



    def action_view_mrp_production(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('mrp.action_mrp_production_form')
        action['domain'] = [('origin', '=', self.name)]
        return action

    def action_view_mrp_production_in_progress(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('mrp.action_mrp_production_form')
        action['domain'] = [
            ('origin', '=', self.name),
            ('state', 'in', ['confirmed', 'progress', 'to_close'])
        ]
        return action

    def action_view_mrp_production_done(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('mrp.action_mrp_production_form')
        action['domain'] = [
            ('origin', '=', self.name),
            ('state', '=', 'done')
        ]
        return action
