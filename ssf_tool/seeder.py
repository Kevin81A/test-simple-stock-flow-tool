"""
Módulo de sembrado de datos de prueba para Simple Stock Flow.
Totalmente idempotente: no duplica productos si ya existen.
"""

import os
from typing import Dict, List
from .client import ApiClient

DEMO_PRODUCTS = [
    {
        "name": "Café Especial en Grano 500g",
        "category_name": "Bebidas",
        "price": 28500.00,
        "stock": 45,
        "image_file": "cafe_grano.jpg",
    },
    {
        "name": "Queso Campesino Fresco 1kg",
        "category_name": "Lácteos",
        "price": 18000.00,
        "stock": 30,
        "image_file": "queso_campesino.png",
    },
    {
        "name": "Pan Artesanal Masa Madre",
        "category_name": "Panadería",
        "price": 9500.00,
        "stock": 25,
        "image_file": "pan_artesanal.jpg",
    },
    {
        "name": "Leche Entera Pasteurizada 1L",
        "category_name": "Lácteos",
        "price": 4600.00,
        "stock": 80,
        "image_file": "leche_entera.png",
    },
    {
        "name": "Arroz Premium Seleccionado 5kg",
        "category_name": "Abarrotes",
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
    print("  Simple Stock Flow · Sembrador de Datos (CLI T-24)")
    print(f"  Destino: {base_url}")
    print("=" * 60)

    client = ApiClient(base_url)

    # 1. Autenticación
    print(f"\n[1/4] Autenticando como '{username}'...")
    try:
        client.login(username, password)
        print("  ✓ Autenticación exitosa (Token JWT obtenido)")
    except Exception as e:
        print(f"  ✗ Error de autenticación: {e}")
        return

    # 2. Categorías
    print("\n[2/4] Consultando categorías disponibles...")
    categories = client.get_categories()
    cat_map: Dict[str, str] = {c["name"].lower(): c["id"] for c in categories}
    print(f"  ✓ {len(categories)} categorías encontradas: {list(cat_map.keys())}")

    # 3. Productos (Idempotente)
    print("\n[3/4] Verificando y sembrando catálogo de productos...")
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
            print(f"  • Producto existente: '{prod_name}' (ID: {prod_id}) - omitiendo creación")
        else:
            prod_id = client.create_product(
                name=prod_name,
                price=item["price"],
                stock=item["stock"],
                category_id=cat_id,
            )
            print(f"  + Creado producto: '{prod_name}' (ID: {prod_id})")

        product_ids.append(prod_id)

        # Imagen
        img_name = item["image_file"]
        img_path = os.path.join(images_dir, img_name)
        if os.path.exists(img_path):
            try:
                img_url = client.upload_image(prod_id, img_path)
                print(f"    ✓ Imagen cargada: {img_url}")
            except Exception as e:
                print(f"    ⚠ Imagen no subida ({img_name}): {e}")
        else:
            print(f"    ⚠ Archivo local de imagen no encontrado: {img_path}")

    # 4. Ventas de Demostración
    print("\n[4/4] Sembrando transacciones de venta de prueba...")
    if len(product_ids) >= 2:
        try:
            sale_1 = client.create_sale([
                {"productId": product_ids[0], "quantity": 2},
                {"productId": product_ids[1], "quantity": 1},
            ])
            print(f"  + Venta #1 registrada con éxito (ID: {sale_1})")

            sale_2 = client.create_sale([
                {"productId": product_ids[2], "quantity": 3},
                {"productId": product_ids[3], "quantity": 2},
            ])
            print(f"  + Venta #2 registrada con éxito (ID: {sale_2})")
        except Exception as e:
            print(f"  ⚠ Advertencia en registro de ventas de demo: {e}")

    print("\n" + "=" * 60)
    print("  ¡Sembrado de datos finalizado exitosamente!")
    print("=" * 60)
