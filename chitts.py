from flask import Blueprint, render_template, request
from models.Roommate import Roommate

# Create a Blueprint for chitts
chitts_bp = Blueprint("chitts_bp", __name__, template_folder="../templates")

@chitts_bp.route("/chitts", methods=["GET", "POST"])
def chitts():
    """
    Chitts (spin wheel) view:
    - Fetch all roommate names from the database.
    - Optionally add a temporary extra name (not saved to DB).
    - Render the chitts.html template.
    """

    # Try to fetch all roommates safely
    try:
        roommates = Roommate.query.all()
    except Exception as e:
        roommates = []
        print(f"[ERROR] Failed to load roommates: {e}")

    # Prepare list of names only
    roommate_names = [rm.name for rm in roommates if getattr(rm, "name", None)]

    # Handle optional POST input for extra name
    if request.method == "POST":
        extra_name = request.form.get("extra_name", "").strip()
        if extra_name:
            roommate_names.append(extra_name)

    # Render the template with roommate list
    return render_template("chitts.html", roommates=roommate_names)
