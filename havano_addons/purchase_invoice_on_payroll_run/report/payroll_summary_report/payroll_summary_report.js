// frappe.query_reports["Payroll Summary Report"] = {
//     "filters": [
//         {
//             "fieldname": "period",
//             "label": __("Payroll Period"),
//             "fieldtype": "Data",
//             "reqd": 1,
//             "wildcard_filter": 1
//         },
//         {
//             "fieldname": "from_date",
//             "label": __("From Date"),
//             "fieldtype": "Date"
//         },
//         {
//             "fieldname": "to_date", 
//             "label": __("To Date"),
//             "fieldtype": "Date"
//         }
//     ],

//     "formatter": function(value, row, column, data, default_formatter) {
//         value = default_formatter(value, row, column, data);
        
//         // Make totals row bold
//         if (data && data.bold) {
//             value = value.replace('>', ' style="font-weight: bold; background-color: #f0f0f0;">');
//         }
        
//         return value;
//     },

//     "onload": function(report) {
//         // Set default period to current month if available
//         var current_date = frappe.datetime.now_date();
//         var first_day = frappe.datetime.month_start(current_date);
//         var last_day = frappe.datetime.month_end(current_date);
        
//         // Format period as "MM-YYYY" or similar based on your data
//         var period = frappe.datetime.str_to_user(first_day).split('-')[1] + '-' + 
//                      frappe.datetime.str_to_user(first_day).split('-')[2];
        
//         report.set_filter_value("from_date", first_day);
//         report.set_filter_value("to_date", last_day);
        
//         // You might want to get the most recent period from your data
//         frappe.call({
//             method: "frappe.client.get_list",
//             args: {
//                 doctype: "Salary Summary On Payroll Run",
//                 fields: ["period"],
//                 filters: {"completed": "yes"},
//                 order_by: "creation desc",
//                 limit_page_length: 1
//             },
//             callback: function(r) {
//                 if (r.message && r.message.length > 0) {
//                     report.set_filter_value("period", r.message[0].period);
//                 } else {
//                     report.set_filter_value("period", period);
//                 }
//             }
//         });
//     }
// };