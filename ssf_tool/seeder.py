"""
Seed module for demo data in Simple Stock Flow.
Fully idempotent: does not duplicate products if they already exist.
"""

import os
from typing import Dict, List
from .client import ApiClient

DEMO_PRODUCTS = [
    {
        "name": "Specialty Whole Bean Coffee 500g",
        "category_name": "General",
        "price": 28500.00,
        "stock": 45,
        "image_file": "cafe_grano.jpg",
    },
    {
        "name": "Fresh Farm Cheese 1kg",
        "category_name": "General",
        "price": 18000.00,
        "stock": 30,
        "image_file": "queso_campesino.png",
    },
    {
        "name": "Artisan Sourdough Bread",
        "category_name": "General",
        "price": 9500.00,
        "stock": 25,
        "image_file": "pan_artesanal.jpg",
    },
    {
        "name": "Pasteurized Whole Milk 1L",
        "category_name": "General",
        "price": 4600.00,
        "stock": 80,
        "image_file": "leche_entera.png",
    },
    {
        "name": "Selected Premium Rice 5kg",
        "category_name": "General",
        "price": 24000.00,
        "stock": 50,
        "image_file": "arroz_premium.jpg",
    },
]


def run_seed(
    base_url: str,
    username: str,
    password: str,
    images_dir: str,
) -> None:
    print("=" * 60)
    print("  Simple Stock Flow · Demo Data Seeder (CLI T-24)")
    print(f"  Target URL: {base_url}")
    print("=" * 60)

    client = ApiClient(base_url)

    # 1. Authentication
    print(f"\n[1/4] Authenticating as '{username}'...")
    try:
        client.login(username, password)
        print("  ✓ Authentication successful (JWT token retrieved)")
    except Exception as e:
        print(f"  ✗ Authentication error: {e}")
        return

    # 2. Categories
    print("\n[2/4] Fetching available categories...")
    categories = client.get_categories()
    cat_map: Dict[str, str] = {c["name"].lower(): c["id"] for c in categories}
    print(f"  ✓ {len(categories)} categories found: {list(cat_map.keys())}")

    # 3. Products (Idempotent)
    print("\n[3/4] Verifying and seeding product catalog...")
    existing = client.get_products(size=100)
    existing_map: Dict[str, Dict] = {
        p["name"].lower(): p for p in existing.get("items", [])
    }

    product_ids: List[str] = []

    for item in DEMO_PRODUCTS:
        cat_id = cat_map.get(item["category_name"].lower())
        if not cat_id:
            # Fallback to first available category
            cat_id = list(cat_map.values())[0]

        prod_name = item["name"]
        if prod_name.lower() in existing_map:
            prod_info = existing_map[prod_name.lower()]
            prod_id = prod_info["id"]
            print(f"  • Existing product: '{prod_name}' (ID: {prod_id}) - skipping creation")
        else:
            prod_id = client.create_product(
                name=prod_name,
                price=item["price"],
                stock=item["stock"],
                category_id=cat_id,
            )
            print(f"  + Created product: '{prod_name}' (ID: {prod_id})")

        product_ids.append(prod_id)

        # Image
        img_name = item["image_file"]
        img_path = os.path.join(images_dir, img_name)
        if os.path.exists(img_path):
            try:
                img_url = client.upload_image(prod_id, img_path)
                print(f"    ✓ Image uploaded: {img_url}")
            except Exception as e:
                print(f"    ⚠ Image upload skipped ({img_name}): {e}")
        else:
            print(f"    ⚠ Local image file not found: {img_path}")

    # 4. Demo Sales
    print("\n[4/4] Seeding sample sale transactions...")
    if len(product_ids) >= 2:
        try:
            sale_1 = client.create_sale([
                {"productId": product_ids[0], "quantity": 2},
                {"productId": product_ids[1], "quantity": 1},
            ])
            print(f"  + Sale #1 successfully created (ID: {sale_1})")

            sale_2 = client.create_sale([
                {"productId": product_ids[2], "quantity": 3},
                {"productId": product_ids[3], "quantity": 2},
            ])
            print(f"  + Sale #2 successfully created (ID: {sale_2})")
        except Exception as e:
            print(f"  ⚠ Notice during demo sales seeding: {e}")

    print("\n" + "=" * 60)
    print("  Demo data seeding completed successfully!")
    print("=" * 60)