from odoo import models, fields, api

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def _get_product_attribute_values(self, product_or_template):
        """
        Helper method to extract attributes and values from a product.product or product.template.
        Returns a dictionary: {attribute_name: [value1, value2, ...]}
        """
        attributes_and_values = {}
        # Ensure we are working with a valid recordset
        if not product_or_template or not product_or_template.exists():
            return attributes_and_values

        if product_or_template._name == 'product.template':
            attribute_lines = product_or_template.attribute_line_ids
        elif product_or_template._name == 'product.product':
            # For product.product, get attributes from its product.template
            attribute_lines = product_or_template.product_tmpl_id.attribute_line_ids
        else:
            return attributes_and_values

        for attribute_line in attribute_lines:
            attribute_name = attribute_line.attribute_id.name
            # Collect names of attribute values
            values = [val.name for val in attribute_line.value_ids]
            attributes_and_values[attribute_name] = values
        return attributes_and_values

    def generate_variants_action(self):
        self.ensure_one()
        
        finished_product_template = self.product_tmpl_id
        
        if not finished_product_template:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': "Warning",
                    'message': "No Finished Product Template found for this BoM.",
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        finished_product_attributes_and_values = self._get_product_attribute_values(finished_product_template)
        


        # Search for semi-finished and raw material products that match attributes
        # Exclude the finished product itself
        matching_products = self.env['product.product'].search([
            ('product_tmpl_id', '!=', finished_product_template.id), # Exclude variants of the finished product
        ])

        found_matches = []
        for candidate_product in matching_products:
            candidate_attributes_and_values = self._get_product_attribute_values(candidate_product)
            
            is_match = False
            for fp_attr, fp_vals in finished_product_attributes_and_values.items():
                if fp_attr in candidate_attributes_and_values:
                    if any(val in candidate_attributes_and_values[fp_attr] for val in fp_vals):
                        is_match = True
                        break
            
            if is_match:
                found_matches.append(candidate_product)
        
        if found_matches:

            
            # Create BOM lines for matching products
            created_bom_lines_count = 0
            skipped_bom_lines_count = 0
            for product_to_add in found_matches:
                # Check if a BOM line for this product already exists
                existing_bom_line = self.bom_line_ids.filtered(lambda l: l.product_id == product_to_add)
                # Determine the attribute values for the finished product combination
                finished_product_attribute_values = self.env['product.template.attribute.value']
                for ptav_component in product_to_add.product_template_attribute_value_ids:
                    # Find the corresponding attribute value on the finished product's template
                    corresponding_ptav_fp = self.env['product.template.attribute.value'].search([
                        ('attribute_id', '=', ptav_component.attribute_id.id),
                        ('product_attribute_value_id', '=', ptav_component.product_attribute_value_id.id),
                        ('product_tmpl_id', '=', self.product_tmpl_id.id),
                    ], limit=1)
                    if corresponding_ptav_fp:
                        finished_product_attribute_values += corresponding_ptav_fp

                if not existing_bom_line:
                    self.env['mrp.bom.line'].create({
                        'bom_id': self.id,
                        'product_id': product_to_add.id,
                        'product_qty': 1.0, # Default quantity, can be made configurable
                        'product_uom_id': product_to_add.uom_id.id,
                        'bom_product_template_attribute_value_ids': [(6, 0, finished_product_attribute_values.ids)],
                    })
                    created_bom_lines_count += 1
                else:
                    skipped_bom_lines_count += 1
            
            message_parts = []
            if created_bom_lines_count > 0:
                message_parts.append("BOM lines updated successfully based on matching attributes.")
                if skipped_bom_lines_count > 0:
                    message_parts.append(f"({skipped_bom_lines_count} existing lines skipped).")
            elif skipped_bom_lines_count > 0:
                message_parts.append(f"No new BOM lines created. {skipped_bom_lines_count} existing lines skipped.")
            else:
                message_parts.append("No new BOM lines created.") # Should ideally not happen if found_matches is true
            
            message = " ".join(message_parts)
            notification_type = 'info'

        else:
            message = "No matching Semi-Finished/Raw Material Products found."
            notification_type = 'warning'

            
        # Return action to reload the current form view
        return {
            'type': 'ir.actions.act_window',
            'name': "BOM Line Generation: " + message, # Use the message in the action name
            'res_model': 'mrp.bom',
            'res_id': self.id,
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'current',
        }