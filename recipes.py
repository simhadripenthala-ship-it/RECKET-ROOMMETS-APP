import random

# ---------- Full Recipe Data ----------

def get_all_recipes():
    items = []

    # ---------- 60 Curry Recipes ----------
    curry_icons = ["🍛", "🍗", "🥘", "🌶️", "🍲"]
    curry_names = [
        "Chicken Curry", "Paneer Butter Masala", "Egg Curry", "Dal Tadka",
        "Kadai Chicken", "Mutton Rogan Josh", "Palak Paneer", "Chole Masala",
        "Fish Curry", "Aloo Gobi", "Bhindi Masala", "Mixed Veg Curry",
        "Prawn Masala", "Mushroom Curry", "Tomato Curry", "Egg Masala",
        "Veg Korma", "Butter Chicken", "Malai Kofta", "Cabbage Curry",
        "Cauliflower Masala", "Capsicum Curry", "Bottle Gourd Curry",
        "Karela Fry", "Brinjal Curry", "Beetroot Curry", "Drumstick Curry",
        "Spinach Curry", "Coconut Curry", "Methi Chicken", "Keema Curry",
        "Green Peas Curry", "Chana Dal Curry", "Masoor Dal Curry",
        "Sambar", "Rasam", "Kadhi Pakora", "Lemon Dal", "Vegetable Kurma",
        "Toor Dal Curry", "Tomato Dal", "Punjabi Dal Fry", "Dum Aloo",
        "Egg Kurma", "Chicken Chettinad", "Gongura Chicken", "Pepper Chicken",
        "Prawn Coconut Curry", "Methi Malai Paneer", "Paneer Do Pyaza",
        "Aloo Palak", "Kofta Curry", "Rajma Masala", "Kashmiri Curry",
        "Veg Manchurian Gravy", "Navratan Korma", "Shahi Paneer",
        "Veg Hyderabadi", "Vegetable Stew", "Matar Paneer", "Cabbage Kootu"
    ]

    for i, name in enumerate(curry_names, start=1):
        items.append({
            "id": i,
            "name": name,
            "icon": curry_icons[i % len(curry_icons)],
            "desc": f"A flavorful {name} cooked with traditional Indian spices.",
            "time": random.choice([25, 30, 40, 45, 50]),
            "serves": random.choice([2, 3, 4]),
            "difficulty": random.choice(["Easy", "Medium"]),
            "tags": ["Curry", "Indian", "Spicy"],
        })

    # ---------- 25 Desserts ----------
    dessert_icons = ["🍨", "🍰", "🍮", "🍪", "🍩"]
    dessert_names = [
        "Gulab Jamun", "Rasgulla", "Kheer", "Payasam", "Halwa", "Carrot Halwa",
        "Coconut Ladoo", "Boondi Ladoo", "Mysore Pak", "Rasmalai", "Basundi",
        "Phirni", "Sooji Halwa", "Malpua", "Sweet Pongal", "Badam Kheer",
        "Kalakand", "Barfi", "Peda", "Milk Cake", "Shrikhand", "Kesari Bath",
        "Mango Custard", "Fruit Salad", "Chocolate Sandesh"
    ]

    for i, name in enumerate(dessert_names, start=len(items) + 1):
        items.append({
            "id": i,
            "name": name,
            "icon": dessert_icons[i % len(dessert_icons)],
            "desc": f"A delightful {name} to satisfy your sweet tooth.",
            "time": random.choice([15, 20, 25, 30]),
            "serves": random.choice([2, 4]),
            "difficulty": random.choice(["Easy", "Medium"]),
            "tags": ["Dessert", "Sweet"],
        })

    # ---------- 15 Rice Dishes ----------
    rice_icons = ["🍚", "🥗", "🍱", "🥣"]
    rice_names = [
        "Tomato Rice", "Veg Pulao", "Jeera Rice", "Lemon Rice",
        "Coconut Rice", "Curd Rice", "Biryani", "Fried Rice",
        "Tamarind Rice", "Schezwan Rice", "Peas Pulao", "Carrot Rice",
        "Mint Rice", "Garlic Rice", "Onion Rice"
    ]

    for i, name in enumerate(rice_names, start=len(items) + 1):
        items.append({
            "id": i,
            "name": name,
            "icon": rice_icons[i % len(rice_icons)],
            "desc": f"Aromatic {name} full of flavor and texture.",
            "time": random.choice([20, 25, 30]),
            "serves": random.choice([2, 3, 4]),
            "difficulty": random.choice(["Easy", "Medium"]),
            "tags": ["Rice", "Indian"],
        })

    return items


# ---------- Fetch Single Recipe by ID ----------
def get_recipe_by_id(recipe_id):
    recipes = get_all_recipes()
    return next((r for r in recipes if r["id"] == recipe_id), None)
