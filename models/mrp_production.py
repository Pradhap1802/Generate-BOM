from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # Store base SO dimensions on MO for traceability and multi-level recursion
    so_length_in_inches = fields.Float(string='SO Length (in)')
    so_width_in_inches = fields.Float(string='SO Width (in)')

    @api.model_create_multi
    def create(self, vals_list):
        """ On MO creation:
        1. For top-level MOs: Get dimensions from SO Line
        2. For child MOs: Get dimensions and update quantity based on parent MO's BOM line
        """
        for vals in vals_list:
            if vals.get('origin'):
                # Check if origin is a MO
                parent_mo = self.env['mrp.production'].search([('name', '=', vals.get('origin'))], limit=1)
                if parent_mo:
                    # Copy dimensions from parent MO
                    vals['so_length_in_inches'] = parent_mo.so_length_in_inches
                    vals['so_width_in_inches'] = parent_mo.so_width_in_inches
                    
                    # Find the BOM line in parent MO that corresponds to this component
                    parent_bom_line = parent_mo.bom_id.bom_line_ids.filtered(
                        lambda l: l.product_id.id == vals.get('product_id')
                    )
                    if parent_bom_line:
                        # If formula is applied, calculate dynamic quantity
                        if parent_bom_line.apply_formula:
                            qty = parent_mo._get_dynamic_quantity(parent_bom_line, 
                                                              parent_mo.so_length_in_inches,
                                                              parent_mo.so_width_in_inches)
                            vals['product_qty'] = qty * parent_mo.product_qty
                        else:
                            # Use static quantity from BOM line
                            vals['product_qty'] = parent_bom_line.product_qty * parent_mo.product_qty
                else:
                    # If not a MO, check if it's a SO
                    sol = self.env['sale.order.line'].search([
                        ('order_id.name', '=', vals['origin']),
                        ('product_id', '=', vals.get('product_id'))
                    ], limit=1)
                    if sol:
                        vals['so_length_in_inches'] = sol.length_in_inches
                        vals['so_width_in_inches'] = sol.width_in_inches
                    
        productions = super().create(vals_list)
        for production in productions:
            production._update_component_quantities_on_moves()
        return productions
    def write(self, vals):
        res = super().write(vals)
        if 'move_raw_ids' in vals or 'bom_id' in vals or 'product_qty' in vals or 'so_length_in_inches' in vals or 'so_width_in_inches' in vals:
            self._update_component_quantities_on_moves()
        return res

    def _get_dynamic_quantity(self, bom_line, length, width):
        """
        Calculates the quantity for a single BOM line based on the dynamic formula.
        This is the specific implementation of your requested `_compute_dynamic_qty`.
        """
        self.ensure_one()
        if not bom_line.apply_formula:
            return bom_line.product_qty

        # Your formula: (SO.Length - Line.Deduction) + (SO.Width - Line.Deduction)
        computed_qty = (length - bom_line.length_in_inches) + (width - bom_line.width_in_inches)
        
        _logger.info(
            f"Dynamic BOM calculation for product '{bom_line.product_id.display_name}': "
            f"(Length:{length} - Ded:{bom_line.length_in_inches}) + "
            f"(Width:{width} - Ded:{bom_line.width_in_inches}) = {computed_qty}"
        )

        return computed_qty if computed_qty > 0 else 0

    def _update_component_quantities_on_moves(self):
        self.ensure_one()
        length = self.so_length_in_inches
        width = self.so_width_in_inches

        if not self.bom_id.is_custom or (length == 0 and width == 0):
            return

        for move in self.move_raw_ids:
            bom_line = self.env['mrp.bom.line'].search([('bom_id', '=', self.bom_id.id), ('product_id', '=', move.product_id.id)], limit=1)
            if bom_line and bom_line.apply_formula:
                dynamic_qty_per_unit = self._get_dynamic_quantity(bom_line, length, width)
                new_calculated_qty = dynamic_qty_per_unit * self.product_qty
                if move.product_uom_qty != new_calculated_qty:
                    move.write({'product_uom_qty': new_calculated_qty})

    def _get_moves_raw_values(self):
        """
        Overrides the move generation to inject the dynamic quantities.
        This method is called recursively by Odoo for sub-assemblies.
        """
        moves = super()._get_moves_raw_values()

        # Get the effective dimensions from the current MO.
        # These dimensions are passed down from the SO or parent MO.
        length = self.so_length_in_inches
        width = self.so_width_in_inches

        if not self.bom_id.is_custom or (length == 0 and width == 0):
            return moves

        _logger.info(f"Applying dynamic BOM logic for MO {self.name} with L={length}, W={width}")

        for move in moves:
            bom_line = self.env['mrp.bom.line'].browse(move.get('bom_line_id'))
            # If the BOM line has a dynamic formula, we override the quantity provided by the super() call.
            if bom_line and bom_line.apply_formula:
                # Calculate the dynamic quantity needed for a single unit of the final product.
                dynamic_qty_per_unit = self._get_dynamic_quantity(bom_line, length, width)
                
                # The super() call already provides a quantity scaled by the production quantity,
                # but it's based on the static bom_line.product_qty.
                # We replace it with our own calculation, also scaled by the production quantity.
                move['product_uom_qty'] = dynamic_qty_per_unit * self.product_qty

        return moves