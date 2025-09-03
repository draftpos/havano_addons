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
























frappe.listview_settings['Ha Group Invoice'] = {
    onload: function(listview) {
        listview.page.add_menu_item(__('Promote Customers'), function() {
            show_bulk_promote_dialog();
        });
    }
};

function show_bulk_promote_dialog() {
    let dialog = new frappe.ui.Dialog({
        title: __('Bulk Promote Customers'),
        fields: [
            {
                fieldname: 'from_group',
                fieldtype: 'Link',
                label: __('From Group'),
                options: 'Customer Group',
                reqd: 1,
                get_query: function() {
                    return {
                        filters: {
                            'is_group': 0  // Only show leaf groups
                        }
                    };
                }
            },
            {
                fieldname: 'to_group',
                fieldtype: 'Link',
                label: __('To Group'),
                options: 'Customer Group',
                reqd: 1,
                get_query: function() {
                    return {
                        filters: {
                            'is_group': 0  // Only show leaf groups
                        }
                    };
                }
            },
            {
                fieldname: 'customer_count',
                fieldtype: 'Data',
                label: __('Customers Affected'),
                read_only: 1,
                default: __('Will be calculated after selecting groups')
            }
        ],
        primary_action: function() {
            let values = dialog.get_values();
            if (values) {
                bulk_promote_customers(values.from_group, values.to_group);
            }
        },
        primary_action_label: __('Promote All Customers')
    });
    
    // Update customer count when groups change
    dialog.fields_dict.from_group.df.onchange = function() {
        update_customer_count(dialog);
    };
    dialog.fields_dict.to_group.df.onchange = function() {
        update_customer_count(dialog);
    };
    
    dialog.show();
}

function update_customer_count(dialog) {
    let from_group = dialog.get_value('from_group');
    let to_group = dialog.get_value('to_group');
    
    if (from_group && to_group) {
        frappe.call({
            method: 'havano_addons.havano_addons.doctype.ha_group_invoice.ha_group_invoice.get_customer_count',
            args: {
                from_group: from_group,
                to_group: to_group
            },
            callback: function(r) {
                if (r.message) {
                    dialog.set_value('customer_count', 
                        __('{0} customers will be moved from {1} to {2}').format(
                            r.message.count, from_group, to_group
                        )
                    );
                }
            }
        });
    }
}

function bulk_promote_customers(from_group, to_group) {
    frappe.confirm(
        __('Are you sure you want to move ALL customers from {0} to {1}? This action cannot be undone.').format(from_group, to_group),
        function() {
            frappe.call({
                method: 'havano_addons.havano_addons.doctype.ha_group_invoice.ha_group_invoice.bulk_promote_customers',
                args: {
                    from_group: from_group,
                    to_group: to_group
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint({
                            title: __('Success'),
                            indicator: 'green',
                            message: __('Successfully promoted {0} customers from {1} to {2}').format(
                                r.message.promoted_count, from_group, to_group
                            )
                        });
                    }
                },
                freeze: true,
                freeze_message: __('Promoting customers...')
            });
        }
    );
}