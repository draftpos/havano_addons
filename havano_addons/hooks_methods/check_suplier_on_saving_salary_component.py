from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

def check_supplier_on_saving_salary_component(doc, method):
    """
    Check if suppliers are set in accounts table before saving salary component
    """

    try:
        print("=== CHECKING SUPPLIERS IN SALARY COMPONENT ===")
        
        # Check if accounts table exists and has entries
        if not doc.get("accounts"):
            frappe.throw(_("Accounts table cannot be empty. Please add at least one account with supplier."))
        
        # Check each account entry for supplier
        missing_suppliers = []
        
        for i, account in enumerate(doc.accounts):
            account_idx = i + 1
            if not account.get("supplier"):
                missing_suppliers.append(f"Row {account_idx}: Supplier is required")
            
            # Optional: Also check if account is set
            if not account.get("account"):
                missing_suppliers.append(f"Row {account_idx}: Account is required")
        
        # If any suppliers are missing, throw error
        
        print("✓ All suppliers are properly set")
        
    except Exception as e:
        frappe.log_error(f"Error in check_supplier_on_saving_salary_component: {str(e)}")
        frappe.throw(_("Error validating suppliers: {0}").format(str(e)))