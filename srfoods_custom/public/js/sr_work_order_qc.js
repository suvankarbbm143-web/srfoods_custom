frappe.ui.form.on('Work Order', {
    refresh: function(frm) {
        // Work Order সাবমিট বা কমপ্লিট হলে QC Details বাটন দেখাবে
        if (frm.doc.docstatus > 0 || frm.doc.status === 'Completed') {
            frm.add_custom_button(__('QC Details'), function() {
                
                // ১. Quality Inspection ডেটা আনা
                frappe.call({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: 'Quality Inspection',
                        fields: ['name', 'inspection_type', 'reference_name', 'status', 'docstatus'],
                        filters: { reference_name: frm.doc.name },
                        limit_page_length: 20
                    },
                    callback: function(r) {
                        let qc_list = r.message || [];
                        
                        // ২. সম্পর্কিত Stock Entry ডেটা আনা
                        frappe.call({
                            method: 'frappe.client.get_list',
                            args: {
                                doctype: 'Stock Entry',
                                fields: ['name', 'docstatus'],
                                filters: { work_order: frm.doc.name, docstatus: 1 },
                                limit_page_length: 5
                            },
                            callback: function(s) {
                                let stock_entries = s.message || [];
                                let stock_name = stock_entries.length > 0 ? stock_entries[stock_entries.length - 1].name : '-';
                                let rows_html = '';

                                if (qc_list.length > 0) {
                                    qc_list.forEach((qc, index) => {
                                        let status_badge = qc.docstatus === 1 
                                            ? '<span style="color: #28a745; font-weight: 500;">● Submitted</span>' 
                                            : '<span style="color: #fd7e14; font-weight: 500;">● Draft</span>';

                                        rows_html += `
                                            <tr>
                                                <td style="color: #6c757d;">${index + 1}</td>
                                                <td><a href="/app/quality-inspection/${qc.name}" target="_blank">${qc.name}</a></td>
                                                <td>${qc.name}</td>
                                                <td>-</td>
                                                <td><a href="/app/stock-entry/${stock_name}" target="_blank">${stock_name}</a></td>
                                                <td>${status_badge}</td>
                                            </tr>
                                        `;
                                    });
                                } else {
                                    rows_html = `
                                        <tr>
                                            <td style="color: #6c757d;">1</td>
                                            <td>-</td>
                                            <td>-</td>
                                            <td>-</td>
                                            <td><a href="/app/stock-entry/${stock_name}" target="_blank">${stock_name}</a></td>
                                            <td><span style="color: #28a745; font-weight: 500;">● Submitted</span></td>
                                        </tr>
                                    `;
                                }

                                let html_content = `
                                    <div style="font-size: 13px; color: #495057; margin-bottom: 12px;">
                                        Work Order: <strong>${frm.doc.name}</strong>
                                    </div>
                                    <div style="border: 1px solid #ebedf2; border-radius: 6px; overflow: hidden;">
                                        <table class="table table-bordered" style="margin-bottom: 0; font-size: 13px;">
                                            <thead style="background-color: #f8f9fa;">
                                                <tr style="color: #6c757d; font-weight: 500;">
                                                    <th style="width: 40px;">#</th>
                                                    <th>Quality Inspection</th>
                                                    <th>Product Inspection</th>
                                                    <th>Application Inspection</th>
                                                    <th>Stock Entry</th>
                                                    <th>Status</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ${rows_html}
                                            </tbody>
                                        </table>
                                    </div>
                                `;

                                let d = new frappe.ui.Dialog({
                                    title: __('QC Details'),
                                    size: 'large',
                                    fields: [
                                        {
                                            fieldname: 'qc_html',
                                            fieldtype: 'HTML',
                                            options: html_content
                                        }
                                    ]
                                });

                                d.show();
                            }
                        });
                    }
                });
            });
        }
    }
});