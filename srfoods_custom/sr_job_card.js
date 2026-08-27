frappe.ui.form.on('Job Card', {
    refresh: function(frm) {
        
        const is_manager = frappe.user_roles.includes('System Manager') || 
                           frappe.user_roles.includes('Manufacturing Manager');
        
        frm.set_df_property('employee', 'read_only', !is_manager);

        
        if (frm.is_new() || frm.doc.employee.length === 0) {
            frappe.db.get_value('Employee', {'user_id': frappe.session.user}, 'name')
                .then(r => {
                    if (r && r.message && r.message.name) {
                        let row = frm.add_child('employee');
                        row.employee = r.message.name;
                        frm.refresh_field('employee');
                    }
                });
        }
    }
});