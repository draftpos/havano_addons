frappe.listview_settings['Salary Summary On Payroll Run'] = {
    onload: function(listview) {
        // Add custom print button
        listview.page.add_menu_item(__("Print"), function() {
            show_period_dialog(listview);
        });
    }
};

function show_period_dialog(listview) {
    let dialog = new frappe.ui.Dialog({
        title: __('Select Period'),
        fields: [
            {
                fieldname: 'period',
                fieldtype: 'Data',
                label: __('Period'),
                reqd: 1,
                description: __('Enter period (e.g May 2025)')
            }
        ],
        primary_action_label: __('Submit'),
        primary_action(values) {
            if (values.period) {
                generate_print_page(values, listview);
                dialog.hide();
            }
        }
    });
    
    dialog.show();
}

function generate_print_page(values, listview) {
    // Get filtered data from list view
    let filters = listview.filter_area.get();

    // Add period filter to existing filters
    if (!filters) filters = [];
    filters.push(['period', 'like', `%${values.period}%`]);

    // Show loading
    frappe.show_alert({ message: __('Generating print view...'), indicator: 'blue' });

    // Fetch salary summary + salary components
    Promise.all([
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Salary Summary On Payroll Run',
                filters: filters,
                fields: ['name', 'salary_component', 'period', 'total', 'completed'],
                limit_page_length: 0
            }
        }),
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'havano_salary_component',
                fields: ['name', 'salary_component', 'type'],   // child table not returned here
                limit_page_length: 0
            }
        })
    ]).then(async function (responses) {

        let salary_data = responses[0].message;
        let component_docs = responses[1].message;

        let component_type_map = {};
        let company = ""; // <<-- this will store your company

        // Loop over all components
        for (let comp of component_docs) {

            // Save type mapping
            component_type_map[comp.salary_component] = comp.type;

            // Now fetch full document to access child table "accounts"
            let full_doc = await frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "havano_salary_component",
                    name: comp.name
                }
            });

            let doc = full_doc.message;

            // Extract first company found (all items share same company)
            if (!company && doc.accounts && doc.accounts.length > 0) {
                company = doc.accounts[0].company;  // <<-- HERE IS THE COMPANY
            }
        }


            // ──────────────────────────────────────────
            // 1. Fetch default currency from Company
            // ──────────────────────────────────────────
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Company",
                    name: company
                }
            }).then(res => {

                let comp = res.message;
                let default_currency = comp.default_currency || "USD";  // fallback

                // ──────────────────────────────────────────
                // 2. Build custom HTML print content
                // ──────────────────────────────────────────

            // Open custom print page with company passed in
            open_print_page(salary_data, values, component_type_map, company, default_currency);
            })
    });
}

function capitalizeFirst(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}


function open_print_page(data, values, component_type_map, company, default_currency) {
    // Create a new window for printing
    let print_window = window.open('', '_blank');
    
    // Separate earnings and deductions
    let earnings = [];
    let deductions = [];
    let total_earnings = 0;
    let total_deductions = 0;
    
    data.forEach(function(row) {
        let component_type = component_type_map[row.salary_component];
        let amount = parseFloat(row.total) || 0;
        
        if (component_type === 'Earning') {
            earnings.push({
                name: row.salary_component,
                amount: amount
            });
            total_earnings += amount;
        } else if (component_type === 'Deduction') {
            deductions.push({
                name: row.salary_component,
                amount: amount
            });
            total_deductions += amount;
        }
    });
    
    // Calculate net pay
    let net_pay = total_earnings - total_deductions;
    
    let html_content = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payroll Summary - ${values.period}</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 20px; 
                    font-size: 12px;
                }
                .header { 
                    text-align: center; 
                    margin-bottom: 20px; 
                }
                .header h1 { 
                    margin: 0 0 5px 0; 
                    color: #333; 
                    font-size: 18px;
                }
                .company-info {
                    margin-bottom: 15px;
                    text-align: left;
                }
                .summary-table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin-top: 10px;
                }
                .summary-table th { 
                    background-color: #f5f5f5; 
                    padding: 8px; 
                    text-align: left; 
                    border: 1px solid #ddd; 
                    font-weight: bold;
                }
                .summary-table td { 
                    padding: 8px; 
                    border: 1px solid #ddd; 
                    vertical-align: top;
                }
                .deductions-section, .earnings-section{
                   width: 30%;
                }
    

                .amount-column {
                    text-align: right;
                    width: 20%;
                }
                .total-row { 
                    font-weight: bold; 
                    background-color: #e8f4fd !important; 
                }
                .section-header {
                    background-color: #2c3e50 !important;
                    color: white;
                    text-align: center;
                    font-size: 13px;
                }
                .net-pay-section {
                    margin-top: 20px;
                    border-top: 2px solid #333;
                    padding-top: 10px;
                }
                .net-pay-row {
                    font-weight: bold;
                    font-size: 14px;
                }
                .print-btn { 
                    margin: 20px 0; 
                    padding: 8px 16px; 
                    background: #5e64ff; 
                    color: white; 
                    border: none; 
                    border-radius: 3px; 
                    cursor: pointer; 
                    font-size: 12px;
                }
                .print-btn:hover { 
                    background: #4a50e0; 
                }
                @media print {
                    .print-btn { display: none; }
                    body { margin: 10px; }
                    .summary-table th { background-color: #e0e0e0 !important; -webkit-print-color-adjust: exact; }
                    .section-header { background-color: #2c3e50 !important; color: white !important; -webkit-print-color-adjust: exact; }
                    .total-row { background-color: #e8f4fd !important; -webkit-print-color-adjust: exact; }
                }
                .report-info {
                    margin-bottom: 15px;
                    font-size: 11px;
                    color: #666;
                }
                .report-info div {
                    margin-bottom: 3px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>${escapeHtml(company)}</h1>
                <div style="font-size: 14px; font-weight: bold; margin-bottom: 10px;">Payroll Summary for the period of ${values.period}</div>
            </div>
            
            <div class="company-info">
                <div><strong>Company:</strong> ${escapeHtml(company)}</div>
                <div><strong>Period:</strong> ${escapeHtml(values.period)}</div>
                <div><strong>Currency:</strong> ${escapeHtml(default_currency)}</div>
                <div><strong>Report Date:</strong> ${new Date().toLocaleDateString()}</div>
            </div>
            
            <button class="print-btn" onclick="window.print()">Print Report</button>
            
            <table class="summary-table">
                <thead>
                    <tr>
                        <th class="earnings-section">Earnings</th>
                        <th class="amount-column">Amount (${escapeHtml(default_currency)})</th>
                        <th class="deductions-section">Deductions</th>
                        <th class="amount-column">Amount (${escapeHtml(default_currency)})</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    // Determine the maximum number of rows needed
    let max_rows = Math.max(earnings.length, deductions.length);
    
    // Add rows for earnings and deductions
    for (let i = 0; i < max_rows; i++) {
        html_content += '<tr>';
        
        // Earnings column
        if (i < earnings.length) {
            html_content += `
                <td>${capitalizeFirst(escapeHtml(earnings[i].name))}</td>
                <td class="amount-column">${format_currency(earnings[i].amount)}</td>
            `;
        } else {
            html_content += `
                <td></td>
                <td class="amount-column"></td>
            `;
        }
        
        // Deductions column
        if (i < deductions.length) {
            html_content += `
                <td>${capitalizeFirst(escapeHtml(deductions[i].name))}</td>
                <td class="amount-column">${format_currency(deductions[i].amount)}</td>
            `;
        } else {
            html_content += `
                <td></td>
                <td class="amount-column"></td>
            `;
        }
        
        html_content += '</tr>';
    }
    
    // Add total rows
    html_content += `
                    <tr class="total-row">
                        <td><strong>Total Earnings</strong></td>
                        <td class="amount-column"><strong>${format_currency(total_earnings)}</strong></td>
                        <td><strong>Total Deductions</strong></td>
                        <td class="amount-column"><strong>${format_currency(total_deductions)}</strong></td>
                    </tr>
                </tbody>
            </table>
            
            <div class="net-pay-section">
                <table class="summary-table">
                    <tr class="net-pay-row">
                        <td style="width: 70%; text-align: right;"><strong>Net Pay</strong></td>
                        <td class="amount-column"><strong>${format_currency(net_pay)}</strong></td>
                    </tr>
                </table>
            </div>
            
            <div style="margin-top: 30px; text-align: right; font-size: 10px; color: #666;">
                Generated on: ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}
            </div>
            
            <script>
                function format_currency(amount) {
                    return new Intl.NumberFormat('en-US', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    }).format(amount);
                }
                
                function escapeHtml(unsafe) {
                    if (unsafe === null || unsafe === undefined) return '';
                    return unsafe.toString()
                        .replace(/&/g, "&amp;")
                        .replace(/</g, "&lt;")
                        .replace(/>/g, "&gt;")
                        .replace(/"/g, "&quot;")
                        .replace(/'/g, "&#039;");
                }
            </script>
        </body>
        </html>
    `;
    
    print_window.document.write(html_content);
    print_window.document.close();
    
    frappe.show_alert({message: __('Payroll summary generated successfully'), indicator: 'green'});
}

// Utility function to escape HTML
function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) return '';
    return unsafe.toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Utility function to format currency
function format_currency(amount) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(parseFloat(amount) || 0);
}