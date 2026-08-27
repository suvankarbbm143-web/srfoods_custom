frappe.ui.form.on('Work Order', {
    refresh: function(frm) {
        if (!frm.is_new()) {

            // Finish বাটনে ক্লিক করলে Stock Entry ওপেন হবে
            if (frm.doc.docstatus === 1 && frm.doc.status !== 'Completed' && flt(frm.doc.material_transferred_for_manufacturing) > 0) {
                frm.page.set_primary_action(__('Finish'), function() {
                    frappe.model.open_mapped_doc({
                        method: "srfoods_custom.custom_work_order.custom_make_stock_entry",
                        frm: frm,
                        args: {
                            purpose: "Manufacture",
                            qty: flt(frm.doc.qty) - flt(frm.doc.produced_qty)
                        }
                    });
                });
            }

            // QC Details Button
            frm.add_custom_button(__('QC Details'), function() {
                frappe.call({
                    method: "srfoods_custom.api.get_qc_details",
                    args: { work_order: frm.doc.name },
                    callback: function(r) {
                        let records = r.message || [];
                        if (!records.length) {
                            frappe.msgprint(__('No QC details found.'));
                            return;
                        }
                        let row = records[0];
                        let badge_class = row.status === "Submitted" ? "green" : "orange";
                        let prod_qa = (row.product_inspection && row.product_inspection !== '-') 
                            ? `<a href="/app/quality-inspection/${row.product_inspection}" target="_blank">${row.product_inspection}</a>` : '-';
                        let app_qa = (row.application_inspection && row.application_inspection !== '-') 
                            ? `<a href="/app/quality-inspection/${row.application_inspection}" target="_blank">${row.application_inspection}</a>` : '-';
                        let se_link = `<a href="/app/stock-entry/${row.stock_entry}" target="_blank">${row.stock_entry}</a>`;

                        let d = new frappe.ui.Dialog({
                            title: __('QC Details'),
                            size: 'large',
                            fields: [{
                                fieldtype: 'HTML',
                                fieldname: 'qc_table_html',
                                options: `
                                    <p>Work Order: <b>${frm.doc.name}</b></p>
                                    <table style="width:100%; border-collapse:collapse; font-size:13px;">
                                        <thead>
                                            <tr style="background:#fafbfc; border-bottom:2px solid #d1d8dd; text-align:left;">
                                                <th style="padding:8px;">#</th>
                                                <th style="padding:8px;">Product Inspection</th>
                                                <th style="padding:8px;">Application Inspection</th>
                                                <th style="padding:8px;">Stock Entry</th>
                                                <th style="padding:8px;">Status</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td style="padding:8px;">1</td>
                                                <td style="padding:8px;">${prod_qa}</td>
                                                <td style="padding:8px;">${app_qa}</td>
                                                <td style="padding:8px;">${se_link}</td>
                                                <td style="padding:8px;"><span class="indicator-pill ${badge_class}">${row.status}</span></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                `
                            }]
                        });
                        d.show();
                    }
                });
            });

            // Material Consumption Button
            if (frm.doc.docstatus === 1 && frm.doc.status !== 'Completed') {
                frm.add_custom_button(__('Material Consumption'), function() {
                    frappe.call({
                        method: "srfoods_custom.custom_work_order.make_material_consumption_entry",
                        args: { work_order_id: frm.doc.name },
                        callback: function(res) {
                            if (res.message) {
                                frappe.set_route('Form', 'Stock Entry', res.message.name || res.message);
                            }
                        }
                    });
                });
            }
        }
    }
});