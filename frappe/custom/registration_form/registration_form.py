import frappe
from frappe.model.naming import make_autoname
from frappe import _

def validate_registration_form(doc, method):
    """Generate autoname series when Registration Form is approved."""
    frappe.logger().info(f"Validating: {doc.name}, Workflow State: {doc.workflow_state}")
    
    if doc.workflow_state == "Approved":
        if not doc.application_no:
            application_no = make_autoname("BRB-S1-.#####")
            doc.db_set("application_no", application_no)
        
        if not doc.registration_no:
            registration_no = make_autoname("BRB-S2-.#####")
            doc.db_set("registration_no", registration_no)

def on_update(doc, method):
    """Trigger when the Registration Form document is updated."""
    frappe.logger().info(f"Updating: {doc.name}, Workflow State: {doc.workflow_state}")
    
    if doc.workflow_state == "Approved" and not doc.user_id:
        create_user_from_registration(doc)

def create_user_from_registration(doc):
    """Create Website User from the Registration Form on approval."""
    
    # Check if a user with the same Email or Mobile already exists
    existing_users = frappe.db.get_all(
        "User",
        fields=["email", "mobile_no"],
        or_filters={"email": doc.email, "mobile_no": doc.mobile_no}
    )
    
    if existing_users:
        frappe.throw(
            _(f"User exists with Email {frappe.bold(existing_users[0].email)}, Mobile {frappe.bold(existing_users[0].mobile_no)}<br>Please check email / mobile or contact administrator."),
            frappe.DuplicateEntryError
        )
    
    # Create new Website User
    user = frappe.get_doc({
        "doctype": "User",
        "first_name": doc.contact_person_name,  # Mapped from Registration Form
        "email": doc.email_id,
        "user_type": "Website User",
        "phone": doc.phone,
        "mobile_no": doc.mobile_no,
    })
    
    user.flags.ignore_permissions = True
    user.enabled = True
    user.send_welcome_email = True
    user.insert()
    
    # Assign "BB User" Role
    user.add_roles("BB User")
    
    # Update the Registration Form with the created User ID
    doc.db_set("user_id", user.name)