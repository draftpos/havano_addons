from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class HaGroupInvoiceItem(Document):
    def validate(self):
        # Automatically calculate amount when qty or rate changes
        self.calculate_amount()
        
        # Fetch item name if not set
        if self.item_code and not self.item_name:
            self.fetch_item_name()
    
    def calculate_amount(self):
        """Calculate amount based on quantity and rate"""
        if self.qty and self.rate:
            self.amount = flt(self.qty) * flt(self.rate)
        else:
            self.amount = 0
    
    def fetch_item_name(self):
        """Fetch item name from Item doctype"""
        if self.item_code:
            item_name = frappe.db.get_value('Item', self.item_code, 'item_name')
            if item_name:
                self.item_name = item_name
    
    def on_update(self):
        # Update parent document's grand total when item changes
        self.update_parent_total()
    
    def update_parent_total(self):
        """Update the parent document's grand total"""
        if self.get('parent') and self.get('parenttype'):
            parent = frappe.get_doc(self.parenttype, self.parent)
            parent.calculate_grand_total()
            parent.save(ignore_permissions=True)