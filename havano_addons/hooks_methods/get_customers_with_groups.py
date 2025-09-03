from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, flt, cint, now_datetime
from frappe import _
import json

def get_all_customers_from_groups_and_sub_groups(self):
    print("--------------------SELECTED GROUP----------------------------------")
    print(self.group_customer)
    if self.group_customer == "All Customer Groups":
        all_groups = frappe.get_all('Customer Group', pluck='name')
        customers = frappe.get_all('Customer',
            filters={
                'customer_group': ['in', all_groups],
                'disabled': 0
            },
            fields=['name', 'customer_name']
        )
        print("--------------ALL GOUPD PART")
        print(customers)
        return customers
    
    parent_group = frappe.db.get_value('Customer Group', self.group_customer, 'parent_customer_group')
    if parent_group == "All Customer Groups":
        parent_group = ""

    has_children = frappe.db.exists('Customer Group', {'parent_customer_group': self.group_customer})
    if has_children:
        child_groups = get_all_child_groups_recursive(self.group_customer)
        child_groups.append(self.group_customer)

        customers = frappe.get_all('Customer',
            filters={
                'customer_group': ['in', child_groups],
                'disabled': 0
            },
            fields=['name', 'customer_name']
        )
        print("------------HAS CHILDREN PART")
        print(customers)
        print(f"-----------------actual PARENT GROUP {parent_group}")
        return customers
    

    elif parent_group and (self.group_customer != "All Customer Groups"):
        child_groups = get_all_child_groups_recursive(parent_group)
        child_groups.append(parent_group)
        
        customers = frappe.get_all('Customer',
            filters={
                'customer_group': ['in', child_groups],
                'disabled': 0
            },
            fields=['name', 'customer_name']
        )
        print("--------------PARENT GROUP PART------------------")
        print(customers)
        print(f"-----------------actual PARENT GROUP {parent_group}")
        return customers
    
    else:
        # If no parent and no children, just fetch customers from the specified group
        customers = frappe.get_all('Customer',
            filters={
                'customer_group': self.group_customer,
                'disabled': 0
            },
            fields=['name', 'customer_name']
        )
        print("--------------------PRINT NORMAL PART------------------")
        print(customers)
        print(f"-----------------actual PARENT GROUP {parent_group}")
        return customers

def get_all_child_groups_recursive(parent_group):
    """Recursively get all child groups of a parent group"""
    child_groups = []
    
    children = frappe.get_all('Customer Group',
        filters={'parent_customer_group': parent_group},
        pluck='name'
    )
    
    for child in children:
        child_groups.append(child)
        child_groups.extend(get_all_child_groups_recursive(child))
    
    return child_groups
