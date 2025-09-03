frappe.listview_settings['Ha Group Invoice'] = {
    onload: function(listview) {
        // Define all functions inside the same scope
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
                                    'is_group': 0
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
                                    'is_group': 0
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
            
            // Fix event listeners
            dialog.fields_dict.from_group.input.addEventListener('change', function() {
                update_customer_count(dialog);
            });
            
            dialog.fields_dict.to_group.input.addEventListener('change', function() {
                update_customer_count(dialog);
            });
            
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
                                // FIXED: Use template literals instead of .format()
                                const message = `${r.message.count} customers will be moved from ${from_group} to ${to_group}`;
                                dialog.set_value('customer_count', message);
                            }
                        }
                    });
                }
            }
            
            dialog.show();
        }

        function bulk_promote_customers(from_group, to_group) {
            // FIXED: Use template literals for the confirmation message
            const confirmMessage = `Are you sure you want to move ALL customers from ${from_group} to ${to_group}? This action cannot be undone.`;
            
            frappe.confirm(
                confirmMessage,
                function() {
                    frappe.call({
                        method: 'havano_addons.havano_addons.doctype.ha_group_invoice.ha_group_invoice.bulk_promote_customers',
                        args: {
                            from_group: from_group,
                            to_group: to_group
                        },
                        callback: function(r) {
                            if (r.message) {
                                // FIXED: Use template literals for success message
                                const successMessage = `Successfully promoted ${r.message.promoted_count} customers from ${from_group} to ${to_group}`;
                                frappe.msgprint({
                                    title: __('Success'),
                                    indicator: 'green',
                                    message: successMessage
                                });
                            }
                        },
                        freeze: true,
                        freeze_message: __('Promoting customers...')
                    });
                }
            );
        }

        // Add menu item
        listview.page.add_menu_item(__('Promote Customers'), function() {
            show_bulk_promote_dialog();
        });
    }
};