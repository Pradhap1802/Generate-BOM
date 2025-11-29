# Dynamic BoM

## Overview

This Odoo module enhances the manufacturing process by enabling the dynamic creation or modification of Bills of Materials (BoMs) directly from sales orders. It integrates seamlessly with Odoo's Sales and Manufacturing modules to provide flexible and automated BoM generation based on specific customer requirements.

## Key Features

*   **Dynamic BoM Generation:** Automatically generates or adjusts Bills of Materials based on the specifics of a sales order.
*   **Sales Order Integration:** Extends the sales order interface, potentially adding fields or actions that facilitate the dynamic BoM process.
*   **MRP Integration:** The dynamically created BoMs are integrated into the Manufacturing Resource Planning (MRP) module for production planning and execution.
*   **Configurable Settings:** Provides configuration options to customize the behavior and rules for dynamic BoM creation.

## Workflow

1.  **Sales Order Processing:** A user processes a sales order in Odoo.
2.  **Dynamic BoM Activation:** Based on the products and configurations specified in the sales order, the `pd_dynamic_bom` module's logic is activated.
3.  **BoM Generation/Update:** A Bill of Materials is dynamically generated or updated to match the sales order's requirements.
4.  **Manufacturing Integration:** This dynamic BoM is then utilized by the MRP module to plan and execute the manufacturing process for the ordered items.
5.  **Configuration:** System administrators can define and adjust rules for dynamic BoM creation through dedicated configuration settings.

## Installation

1.  Copy the `pd_dynamic_bom` folder to your Odoo addons directory.
2.  Update the addons list in Odoo.
3.  Install the "Dynamic BoM" module.

## Dependencies

*   `sale_management`
*   `mrp`

## Configuration

Further configuration options may be available under Odoo's settings, accessible via `res_config_settings_views.xml`.
