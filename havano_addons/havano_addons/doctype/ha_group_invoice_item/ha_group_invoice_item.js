frappe.ui.form.on('Ha Group Invoice Item', {
    item_code: function(frm, cdt, cdn) {
        // Auto-fetch item details when item is selected (works for both quick entry and form)
        var row = frappe.get_doc(cdt, cdn);
        if (row.item_code) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Item",
                    fieldname: ["item_name", "standard_rate"],
                    filters: { name: row.item_code }
                },
                callback: function(r) {
                    if (!r.exc && r.message) {
                        frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name);
                        if (!row.rate) {
                            frappe.model.set_value(cdt, cdn, "rate", r.message.standard_rate || 0);
                        }
                        // Calculate amount
                        var qty = row.qty || 1;
                        var rate = row.rate || r.message.standard_rate || 0;
                        frappe.model.set_value(cdt, cdn, "amount", qty * rate);
                    }
                }
            });
        }
    },
    
    qty: function(frm, cdt, cdn) {
        // Recalculate amount when quantity changes
        var row = frappe.get_doc(cdt, cdn);
        if (row.qty && row.rate) {
            frappe.model.set_value(cdt, cdn, "amount", row.qty * row.rate);
        }
    },
    
    rate: function(frm, cdt, cdn) {
        // Recalculate amount when rate changes
        var row = frappe.get_doc(cdt, cdn);
        if (row.qty && row.rate) {
            frappe.model.set_value(cdt, cdn, "amount", row.qty * row.rate);
        }
    }
});