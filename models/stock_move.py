from odoo import models

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_procurement_values(self):
        """
        This method is crucial for recursion.
        It propagates the dynamic dimensions from a parent manufacturing order
        down to the procurement values that will create a child manufacturing order.
        """
        values = super()._prepare_procurement_values()

        # If the move is generated from a manufacturing order, it's a sub-assembly.
        if not self.production_id:
            return values

        parent_mo = self.production_id
        
        # If the parent MO has dynamic dimensions, pass them to the child MO.
        if parent_mo.so_length_in_inches > 0 or parent_mo.so_width_in_inches > 0:
            values.update({
                'so_length_in_inches': parent_mo.so_length_in_inches,
                'so_width_in_inches': parent_mo.so_width_in_inches,
            })
            
        return values

