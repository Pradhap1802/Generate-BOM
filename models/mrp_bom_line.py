from odoo import fields, models, api

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    length_in_inches = fields.Float(
        string="Deduct Length",
    )
    width_in_inches = fields.Float(
        string="Deduct Width",
    )
    apply_formula = fields.Boolean(
        string="Apply Formula",
        default=False,
    )

    @api.onchange('product_id')
    def _onchange_product_id_map_variants(self):
        """
        Automatically sets the 'Apply on Variants' field of a BOM line based on the
        attributes of the selected component variant.
        """
        if not self.product_id or not self.bom_id.product_tmpl_id.attribute_line_ids:
            self.bom_product_template_attribute_value_ids = False # Clear if no product or parent has no variants
            return

        component_attribute_values = self.product_id.product_template_attribute_value_ids
        if not component_attribute_values:
            self.bom_product_template_attribute_value_ids = False # Clear if component is not a variant
            return

        # Get the actual value names (e.g., 'White', 'Black', 'Low-E')
        component_value_names = {val.name for val in component_attribute_values}

        # Find the corresponding attribute values on the BOM's parent product
        parent_template_id = self.bom_id.product_tmpl_id.id
        matching_parent_values = self.env['product.template.attribute.value'].search([
            ('product_tmpl_id', '=', parent_template_id),
            ('name', 'in', list(component_value_names))
        ])

        if matching_parent_values:
            # Link this BOM line to the corresponding parent product variants
            self.bom_product_template_attribute_value_ids = [(6, 0, matching_parent_values.ids)]
        else:
            # If no matches found, this line does not apply to any specific variant
            self.bom_product_template_attribute_value_ids = False
