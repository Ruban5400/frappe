import frappe
from frappe.utils import today
from datetime import datetime

def update_project_status():
    # Get the current date as a datetime.date object
    current_date = datetime.strptime(today(), "%Y-%m-%d").date()

    # Fetch all records from the "Projects And Events Posting" doctype
    projects = frappe.get_all('Projects And Events Posting', fields=['name', 'status', 'date_of_opportunity', 'due_date'])

    for project in projects:
        # Skip if the date fields are not set
        if project.date_of_opportunity and project.due_date:
            # These fields are already in date format, no need to convert them again
            date_of_opportunity = project.date_of_opportunity
            due_date = project.due_date

            # Check if the current date is between date_of_opportunity and due_date
            if date_of_opportunity <= current_date <= due_date:
                new_status = 'Open'
            # If the due date has passed, set status to 'Closed'
            elif current_date > due_date:
                new_status = 'Closed'
            else:
                continue

            # Only update if the status is different from the existing one
            if project.status != new_status:
                frappe.db.set_value('Projects And Events Posting', project.name, 'status', new_status)

    # Commit the transaction to save changes
    frappe.db.commit()