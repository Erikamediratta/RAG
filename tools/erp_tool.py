# Mock ERP tool — a pretend company database (employees, equipment,
# support tickets) read from erp_data.json instead of a real system.
#
# Every function here returns a dict, never raises an error. If something
# isn't found we return {"found": False, ...} so the AI agent calling this
# can react to it instead of the program crashing.

import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "erp_data.json")

with open(DATA_FILE, "r") as f:
    DB = json.load(f)


def find_employee(name):
    search_term = name.strip().lower()

    for employee in DB["employees"]:
        employee_id = employee["employee_id"].lower()
        employee_name = employee["name"].lower()

        if search_term == employee_id:
            return employee
        if search_term in employee_name:
            return employee

    return None


def get_employee_info(name):
    employee = find_employee(name)

    if employee is None:
        return {"found": False, "message": f"No employee matching '{name}'"}

    return {"found": True, "employee": employee}


def get_tickets(name, status=None):
    employee = find_employee(name)

    if employee is None:
        return {"found": False, "message": f"No employee matching '{name}'"}

    matching_tickets = []
    for ticket in DB["tickets"]:
        if ticket["employee_id"] == employee["employee_id"]:
            matching_tickets.append(ticket)

    # optional filter: only keep tickets with the requested status
    if status is not None:
        filtered_tickets = []
        for ticket in matching_tickets:
            if ticket["status"].lower() == status.lower():
                filtered_tickets.append(ticket)
        matching_tickets = filtered_tickets

    return {"found": True, "employee": employee["name"], "tickets": matching_tickets}


def get_assets(name):
    employee = find_employee(name)

    if employee is None:
        return {"found": False, "message": f"No employee matching '{name}'"}

    matching_assets = []
    for asset in DB["assets"]:
        if asset["assigned_to"] == employee["employee_id"]:
            matching_assets.append(asset)

    return {"found": True, "employee": employee["name"], "assets": matching_assets}


# Only runs when you do `python tools/erp_tool.py` directly — not when
# another file imports these functions. Quick manual test.
if __name__ == "__main__":
    print(get_employee_info("priya"))
    print(get_tickets("Priya Sharma", status="Open"))
    print(get_assets("tom reilly"))
    print(get_employee_info("nobody"))
