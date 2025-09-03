// Copyright (c) 2025, showlina and contributors
// For license information, please see license.txt

frappe.ui.form.on("Ha Group Invoice", {
    edit_posting_datetime: function(frm) {
        if (frm.doc.edit_posting_datetime) {
            frm.set_df_property('posting_date', 'read_only', 0);
            frm.set_df_property('posting_time', 'read_only', 0);
        } else {
            frm.set_df_property('posting_date', 'read_only', 1);
            frm.set_df_property('posting_time', 'read_only', 1);
        }
    }
});





frappe.ui.form.on('Ha Group Invoice', {
    refresh: function(frm) {
        // Add button to create invoices manually if not submitted
        if (!frm.doc.__islocal && frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Create Invoices Now'), function() {
                frappe.call({
                    method: 'havano_addons.havano_addons.doctype.ha_group_invoice.ha_group_invoice.create_invoices_now',
                    args: {
                        docname: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(__('Invoices created successfully'));
                            frm.reload_doc();
                        }
                    }
                });
            });
        }
        
        // Show creation status if available
        if (frm.doc.creation_status) {
            try {
                const status = JSON.parse(frm.doc.creation_status);
                let msg = `<b>Invoice Creation Results:</b><br>`;
                msg += `Successfully created: ${status.total_created} invoices<br>`;
                msg += `Failed: ${status.total_failed} customers<br>`;
                msg += `Completed at: ${status.completion_time}`;
                
                frm.dashboard.add_comment(msg, 'blue', true);
            } catch (e) {
                console.error('Error parsing creation status', e);
            }
        }
    },
    
    group_customer: function(frm) {
        // Auto-update total customers when group changes
        if (frm.doc.group_customer) {
            frm.call('update_total_customers').then(() => {
                frm.refresh_field('total_customers');
            });
        }
    },
    
    items_add: function(frm, cdt, cdn) {
        // Auto-calculate when new items are added
        frm.events.calculate_totals(frm);
    },
    
    items_remove: function(frm, cdt, cdn) {
        // Recalculate when items are removed
        frm.events.calculate_totals(frm);
    },
    
    calculate_totals: function(frm) {
        // Calculate grand total
        let total = 0;
        $.each(frm.doc.items || [], function(i, item) {
            total += flt(item.amount);
        });
        frm.set_value('grand_total', total);
    }
});

frappe.ui.form.on('Ha Group Invoice Item', {
    qty: function(frm, cdt, cdn) {
        calculate_item_amount(frm, cdt, cdn);
    },
    rate: function(frm, cdt, cdn) {
        calculate_item_amount(frm, cdt, cdn);
    }
});

function calculate_item_amount(frm, cdt, cdn) {
    const item = frappe.get_doc(cdt, cdn);
    if (item.qty && item.rate) {
        frappe.model.set_value(cdt, cdn, 'amount', flt(item.qty) * flt(item.rate));
        frm.events.calculate_totals(frm);
    }
}





















frappe.ui.form.on('Ha Group Invoice', {
    refresh: function(frm) {
        // Enable in-cell editing and quick search for items table
        if (frm.fields_dict.items) {
            const grid = frm.fields_dict.items.grid;
            
            // Enable cell editing (this allows quick search on click)
            grid.set_allow_editing(true);
            
            // Set up item query for quick search
            grid.set_columns_editable(['item_code', 'qty', 'rate', 'cost_center', 'project']);
            
            // Add custom behavior for item code field
            grid.grid_rows.forEach(function(row) {
                const item_code_field = row.docfields.find(f => f.fieldname === 'item_code');
                if (item_code_field) {
                    item_code_field.get_control = function() {
                        const control = frappe.ui.form.make_control({
                            parent: this.wrapper,
                            df: {
                                fieldtype: 'Link',
                                fieldname: 'item_code',
                                options: 'Item',
                                get_query: function() {
                                    return {
                                        query: "erpnext.controllers.queries.item_query",
                                        filters: {'is_sales_item': 1}
                                    };
                                }
                            },
                            render_input: true
                        });
                        return control;
                    };
                }
            });
        }
    },
    
    setup: function(frm) {
        // Set up item query for both form and quick entry
        frm.set_query('item_code', 'items', function(doc, cdt, cdn) {
            return {
                query: "erpnext.controllers.queries.item_query",
                filters: {
                    'is_sales_item': 1,
                    'disabled': 0
                }
            };
        });
    }
});