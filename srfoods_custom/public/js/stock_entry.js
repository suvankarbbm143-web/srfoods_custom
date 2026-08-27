frappe.ui.form.on('Stock Entry', {
    refresh: function(frm) {
        // ড্রাফট থাকা অবস্থায় Create বাটনে Quality Inspection অপশন যুক্ত করা
        if (!frm.is_new() && frm.doc.docstatus === 0 && (frm.doc.stock_entry_type === 'Manufacture' || frm.doc.purpose === 'Manufacture')) {
            // Finished Goods রো বের করা
            let fg_item = frm.doc.items ? frm.doc.items.find(d => d.is_finished_item || (!d.s_warehouse && d.t_warehouse)) : null;
            if (!fg_item && frm.doc.items && frm.doc.items.length > 0) {
                fg_item = frm.doc.items[0];
            }

            let item_code = fg_item ? fg_item.item_code : '';
            let sample_size = fg_item ? fg_item.qty : 1;
            let batch_no = fg_item ? fg_item.batch_no : '';
            let quality_inspection_template = fg_item ? fg_item.quality_inspection_template : '';

            // ১. Production Inspection বাটন
            let req_prod = frm.doc.custom_production_inspection_required || frm.doc.production_inspection_required;
            if (req_prod) {
                frm.add_custom_button(__('Production Inspection'), function() {
                    frappe.model.with_doctype('Quality Inspection', function() {
                        let qi = frappe.model.get_new_doc('Quality Inspection');
                        qi.inspection_type = 'In Process';
                        qi.reference_type = 'Stock Entry';
                        qi.reference_name = frm.doc.name;
                        qi.item_code = item_code;
                        qi.sample_size = sample_size;
                        qi.batch_no = batch_no;
                        qi.quality_inspection_template = quality_inspection_template;
                        frappe.set_route('Form', 'Quality Inspection', qi.name);
                    });
                }, __('Create'));
            }

            // ২. Application Inspection বাটন
            let req_app = frm.doc.custom_application_inspection_required || frm.doc.application_inspection_required;
            if (req_app) {
                frm.add_custom_button(__('Application Inspection'), function() {
                    frappe.model.with_doctype('Quality Inspection', function() {
                        let qi = frappe.model.get_new_doc('Quality Inspection');
                        qi.inspection_type = 'Application Inspection';
                        qi.reference_type = 'Stock Entry';
                        qi.reference_name = frm.doc.name;
                        qi.item_code = item_code;
                        qi.sample_size = sample_size;
                        qi.batch_no = batch_no;
                        qi.quality_inspection_template = quality_inspection_template;
                        frappe.set_route('Form', 'Quality Inspection', qi.name);
                    });
                }, __('Create'));
            }
        }
    }
});