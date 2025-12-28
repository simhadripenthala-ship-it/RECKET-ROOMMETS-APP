# app.py
import os, json, random
from datetime import datetime
from flask import Flask, abort, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

# Models and helpers
from models import db
from models.recipes import get_all_recipes, get_recipe_by_id
from models.user import User
from models.chitts import chitts
from models.bills import Expense
from models.chores import Chore
from models.veggie import Veggie
from models.tiffin import Tiffin
from models.Roommate import Roommate
 # ensure filename is models/roommate.py
from utils.helpers import create_user, get_current_user

# ------------------ APP CONFIG ------------------
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "your_secret_key"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///recketroom.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Upload folders
app.config["UPLOAD_FOLDER_ROOMMATES"] = os.path.join(BASE_DIR, "static", "uploads", "roommates")
app.config["UPLOAD_FOLDER_TIFFINS"]  = os.path.join(BASE_DIR, "static", "uploads", "tiffins")
os.makedirs(app.config["UPLOAD_FOLDER_ROOMMATES"], exist_ok=True)
os.makedirs(app.config["UPLOAD_FOLDER_TIFFINS"],  exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# DB init
db.init_app(app)
with app.app_context():
    db.create_all()

# ------------------ ROUTES ------------------

@app.route("/ping")
def ping():
    return {"ok": True, "ts": datetime.utcnow().isoformat()}

# Home / Dashboard
@app.route("/")
def home():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=user.username)

# ------------------ AUTH ------------------
# ------------------ AUTH ------------------
from flask import request, redirect, url_for, flash, session, render_template
from models.user import User  # adjust if your folder structure differs

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.create_user(username=username, password=password)
        if not user:
            flash("Username already exists!", "danger")
            return redirect(url_for("signup"))

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            flash("Login successful!", "success")
            return redirect(url_for("home"))  # change "home" to your main page route
        else:
            flash("Invalid username or password!", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))


# ------------------ ROOMMATES ------------------
# ------------------ ROOMMATES ------------------
@app.route("/roommates", methods=["GET", "POST"])
def roommates_view():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        name    = request.form.get("name")
        address = request.form.get("address")
        contact = request.form.get("contact")
        image   = request.files.get("image")
        proof   = request.files.get("proof")

        image_path = None
        proof_path = None

        # Save profile image
        if image and image.filename and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER_ROOMMATES"], filename)
            image.save(save_path)
            image_path = f"uploads/roommates/{filename}"

        # Save address proof
        if proof and proof.filename and allowed_file(proof.filename):
            proofname = secure_filename(proof.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER_ROOMMATES"], proofname)
            proof.save(save_path)
            proof_path = f"uploads/roommates/{proofname}"

        # Save to database
        roommate = Roommate(
            name=name,
            address=address,
            contact_number=contact,
            image_path=image_path,
            proof_path=proof_path,
        )
        db.session.add(roommate)
        db.session.commit()

        flash("🏠 Roommate added successfully!", "success")
        return redirect(url_for("roommates_view"))

    roommates = Roommate.query.order_by(Roommate.created_at.desc()).all()
    return render_template("roommates.html", roommates=roommates)
# ------------------ DELETE ROOMMATE ------------------
@app.route("/delete_roommate/<int:id>", methods=["POST"])
def delete_roommate(id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    roommate = Roommate.query.get_or_404(id)

    # Remove image if exists
    if roommate.image_path:
        image_file = os.path.join(app.static_folder, roommate.image_path)
        if os.path.exists(image_file):
            try:
                os.remove(image_file)
            except Exception as e:
                print(f"Error deleting image: {e}")

    # Remove proof file if exists
    if roommate.proof_path:
        proof_file = os.path.join(app.static_folder, roommate.proof_path)
        if os.path.exists(proof_file):
            try:
                os.remove(proof_file)
            except Exception as e:
                print(f"Error deleting proof: {e}")

    # Delete from DB
    db.session.delete(roommate)
    db.session.commit()

    flash(f"🗑 Roommate '{roommate.name}' deleted successfully!", "success")
    return redirect(url_for("roommates_view"))



# ------------------ CHITTS ------------------
# ------------------ CHITTS (Task Spinner) ------------------
#from flask import render_template, request
#from models.Roommate import Roommate

@app.route("/chitts", methods=["GET", "POST"])
def chitts():
    """
    Chitts (Task Spinner)
    ---------------------
    - Fetch all roommate names from the database.
    - Allow adding one temporary name (not saved).
    - Render the wheel spinner page with assigned tasks.
    """

    # Fetch all roommates safely
    try:
        roommates = Roommate.query.all()
    except Exception as e:
        print(f"[ERROR] Could not fetch roommates: {e}")
        roommates = []

    # Extract only names
    roommate_names = [rm.name for rm in roommates if getattr(rm, "name", None)]

    # Handle form input for extra (temporary) name
    if request.method == "POST":
        extra_name = request.form.get("extra_name", "").strip()
        if extra_name:
            roommate_names.append(extra_name)

    # Render the Chitts page
    return render_template("chitts.html", roommates=roommate_names)

# ------------------ EXPENSES ------------------
# ------------------ EXPENSES ------------------
@app.route("/expenses", methods=["GET", "POST"])
def expenses_view():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    # Default variables
    total_exp = 0
    fixed_total = 0
    balance_money = 0
    custom_items = []
    num_persons = 0

    if request.method == "POST":
        try:
            total_exp = float(request.form.get("total_exp", 0) or 0)
            num_persons = int(request.form.get("num_persons", 0) or 0)
        except ValueError:
            total_exp, num_persons = 0, 0

        # Fixed values
        gas = 300
        water = 100
        current = 300
        rent = num_persons * 1100  # Rent per person = ₹1100

        # Calculate total of fixed payments
        fixed_total = gas + water + current + rent

        # Handle extra item if provided
        add_label = request.form.get("add_label")
        add_amount = request.form.get("add_amount")
        if add_label and add_amount:
            try:
                add_amount = float(add_amount)
                custom_items.append({"label": add_label, "amount": add_amount})
                fixed_total += add_amount
            except ValueError:
                pass

        # Balance = Total - Fixed
        balance_money = total_exp - fixed_total

    # Pass all data to template
    return render_template(
        "expenses.html",
        total_exp=total_exp,
        num_persons=num_persons,
        fixed_total=fixed_total,
        balance_money=balance_money,
        custom_items=custom_items,
    )


# ------------------ TIFFINS ------------------
@app.route("/tiffin", methods=["GET", "POST"])
def tiffin_view():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        recipe   = request.form.get("recipe")
        week_day = request.form.get("week_day")
        image    = request.files.get("image")
        image_path = None
        # your existing save logic here …

    # Example context data
    items = [
        {"recipe": "Veg Rice", "day": "Monday"},
        {"recipe": "Dal Fry", "day": "Tuesday"},
    ]
    return render_template("tiffin.html", items=items)


# ------------------ VEGGIES ------------------
@app.route("/veggies", methods=["GET", "POST"])
def veggies_view():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        qty = float(request.form.get("quantity", 0) or 0)
        cost = float(request.form.get("cost", 0) or 0)
        curry_recipe = request.form.get("curry_recipe")

        v = Veggie(name=name, quantity_kg=qty, cost_per_kg=cost, curry_recipe=curry_recipe)
        db.session.add(v)
        db.session.commit()
        flash("Veggie added!", "success")
        return redirect(url_for("veggies_view"))

    veggies = Veggie.query.order_by(Veggie.created_at.desc()).all()
    return render_template("veggies.html", veggies=veggies)


# ------------------ DELETE VEGGIE ------------------
@app.route("/delete_veggie/<int:veggie_id>", methods=["POST"])
def delete_veggie(veggie_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    veggie = Veggie.query.get_or_404(veggie_id)
    db.session.delete(veggie)
    db.session.commit()
    flash("Veggie deleted successfully!", "info")
    return redirect(url_for("veggies_view"))



# ------------------ Rice Calculator ------------------
# ------------------ Rice Calculator 🍚 ------------------
@app.route("/rice-calculator", methods=["GET", "POST"])
def rice_calculator():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    rice_result = None
    if request.method == "POST":
        try:
            people   = int(request.form.get("people", 0))
            appetite = request.form.get("appetite", "normal")
            per_person = 70 if appetite == "low" else 90 if appetite == "normal" else 120
            total_rice = people * per_person  # grams
            water_ml = total_rice * 1.5      # 1.5 ml water per gram rice
            rice_result = {
                "people": people,
                "per_person": per_person,
                "rice_grams": total_rice,
                "water_ml": water_ml
            }
        except Exception:
            flash("❌ Invalid input for Rice Calculator.", "danger")
    return render_template("rice_calculator.html", rice_result=rice_result)

# ------------------ White Rava Calculator 🌾 ------------------
@app.route("/white-rava-calculator", methods=["GET", "POST"])
def white_rava_calculator():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    result = None
    if request.method == "POST":
        try:
            people = int(request.form.get("people", 0))
            rava_per_person = 100       # grams per person
            total_rava = people * rava_per_person
            water_ml = total_rava * 3   # 1 g rava = 3 ml water
            result = {
                "people": people,
                "total_rava": total_rava,
                "water_ml": water_ml
            }
        except Exception:
            flash("❌ Invalid input for White Rava.", "danger")
    return render_template("rice_calculator.html", white_rava_result=result)

# ------------------ Natu Rava Calculator 🌾 ------------------
@app.route("/natu-rava-calculator", methods=["GET", "POST"])
def natu_rava_calculator():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    result = None
    if request.method == "POST":
        try:
            people = int(request.form.get("people", 0))
            rava_per_person = 100
            total_rava = people * rava_per_person
            water_ml = total_rava * 2.5   # 1 g rava = 2.5 ml water
            result = {
                "people": people,
                "total_rava": total_rava,
                "water_ml": water_ml
            }
        except Exception:
            flash("❌ Invalid input for Natu Rava.", "danger")
    return render_template("rice_calculator.html", natu_rava_result=result)

# ------------------ Dosa Batter Calculator 🥞 ------------------
@app.route("/dosa-batter-calculator", methods=["GET", "POST"])
def dosa_batter_calculator():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    result = None
    if request.method == "POST":
        try:
            people = int(request.form.get("people", 0))   # number of people
            rice_per_person = 100    # g per person (adjustable)
            total_rice = people * rice_per_person
            total_urad = total_rice * 0.25   # 25% of rice weight
            total_batter = total_rice + total_urad
            result = {
                "people": people,
                "rice": total_rice,
                "urad_dal": total_urad,
                "total_batter": total_batter
            }
        except Exception:
            flash("❌ Invalid input for Dosa Batter.", "danger")
    return render_template("rice_calculator.html", dosa_batter_result=result)



# ------------------ RECIPES ------------------# ------------------ RECIPES ------------------
@app.route("/recipes")
def recipes():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    recipes = []

    # --- Curry Recipes (1–100) ---
    curry_names = [
        "Butter Chicken", "Paneer Masala", "Chana Curry", "Egg Curry", "Mutton Rogan Josh",
        "Fish Curry", "Palak Paneer", "Vegetable Korma", "Chettinad Chicken", "Dal Tadka"
    ]
    curry_emojis = ["🍗", "🌶", "🥥", "🍛", "🍖", "🥘", "🍲", "🥄", "🌿", "🥕"]
    base_ingredients_curry = [
        "Chicken", "Tomato", "Onion", "Garlic", "Ginger", "Chili",
        "Curry leaves", "Coconut milk", "Yogurt", "Turmeric", "Cumin",
        "Coriander", "Mustard seeds", "Fenugreek"
    ]
    steps_curry = [
        "Heat oil and sauté onions until golden.",
        "Add ginger-garlic paste and cook for a minute.",
        "Add tomatoes and cook till soft.",
        "Mix in spices and cook until fragrant.",
        "Add main ingredient and simmer until tender.",
        "Finish with cream or coconut milk and garnish."
    ]

    for i in range(1, 101):
        name = f"Curry {i} — {curry_names[i % len(curry_names)]}"
        recipes.append({
            "name": name,
            "icon": curry_emojis[i % len(curry_emojis)],
            "desc": f"Aromatic Indian curry rich in spices and flavor — {curry_names[i % len(curry_names)]}.",
            "time": 30 + (i % 5) * 5,
            "serves": (i % 4) + 2,
            "difficulty": ["Easy", "Medium", "Hard"][i % 3],
            "ingredients": base_ingredients_curry[i % len(base_ingredients_curry):(i % len(base_ingredients_curry)) + 5],
            "steps": steps_curry,
            "tags": ["Curry", "Indian", "Main Course"]
        })

    # --- Desserts (101–150) ---
    dessert_names = [
        "Gulab Jamun", "Kheer", "Rasgulla", "Halwa", "Ladoo", "Barfi",
        "Payasam", "Mysore Pak", "Jalebi", "Rabri"
    ]
    dessert_emojis = ["🍨", "🍰", "🍮", "🍪", "🍩", "🍫", "🍡", "🥧", "🍧", "🍦"]
    dessert_ingredients = [
        "Sugar", "Milk", "Cardamom", "Saffron", "Rose water",
        "Condensed milk", "Almonds", "Cashews", "Rice flour", "Coconut"
    ]
    dessert_steps = [
        "Heat ghee in a pan and roast base ingredient.",
        "Add milk and cook till thick.",
        "Mix in sugar and flavoring (saffron, cardamom).",
        "Cook until it reaches desired consistency.",
        "Garnish with nuts and serve warm or chilled."
    ]

    for i in range(101, 151):
        name = f"Dessert {i-100} — {dessert_names[(i - 101) % len(dessert_names)]}"
        recipes.append({
            "name": name,
            "icon": dessert_emojis[(i - 101) % len(dessert_emojis)],
            "desc": f"Sweet Indian dessert — {dessert_names[(i - 101) % len(dessert_names)]}, rich and delightful.",
            "time": 25 + (i % 20),
            "serves": ((i - 101) % 5) + 2,
            "difficulty": "Easy" if i % 2 == 0 else "Medium",
            "ingredients": dessert_ingredients[:6],
            "steps": dessert_steps,
            "tags": ["Dessert", "Sweet", "Indian"]
        })

    # --- Rice Dishes (151–180) ---
    rice_names = [
        "Veg Biryani", "Chicken Biryani", "Jeera Rice", "Lemon Rice", "Curd Rice",
        "Pulao", "Fried Rice", "Tamarind Rice", "Ghee Rice", "Peas Pulao"
    ]
    rice_emojis = ["🍚", "🍛", "🥘", "🍲", "🍽"]
    rice_ingredients = [
        "Basmati rice", "Ghee", "Onion", "Garlic", "Cloves",
        "Cinnamon", "Bay leaves", "Cashews", "Raisins", "Saffron"
    ]
    rice_steps = [
        "Soak rice for 15 minutes.",
        "Sauté spices and onions in ghee.",
        "Add rice and stir for 2 minutes.",
        "Pour water and cook covered.",
        "Fluff and serve with garnish."
    ]

    for i in range(151, 181):
        name = f"Rice Dish {i-150} — {rice_names[(i - 151) % len(rice_names)]}"
        recipes.append({
            "name": name,
            "icon": rice_emojis[(i - 151) % len(rice_emojis)],
            "desc": f"Aromatic rice dish — {rice_names[(i - 151) % len(rice_names)]}.",
            "time": 35 + (i % 15),
            "serves": ((i - 151) % 4) + 2,
            "difficulty": "Easy" if (i % 2 == 0) else "Medium",
            "ingredients": rice_ingredients,
            "steps": rice_steps,
            "tags": ["Rice", "Main Course"]
        })

    return render_template("recipes.html", items=recipes)




# ------------------ ROOM INFO ------------------
@app.route("/roominfo")
def roominfo():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    return render_template("roominfo.html")

# ------------------ RUN ------------------
if __name__ == "_main_":
    # Avoid double-start during development
    app.run(debug=True, use_reloader=False)