"""
Punto de entrada de línea de comandos (CLI) para ssf_tool.
"""

import argparse
import os
import sys
from .seeder import run_seed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simple Stock Flow · Herramienta de Demostración y Sembrado"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Command: seed
    seed_parser = subparsers.add_parser("seed", help="Siembra productos, imágenes y ventas de prueba")
    seed_parser.add_argument(
        "--url",
        default=os.getenv("API_BASE_URL", "http://localhost:8000"),
        help="URL base de la API (por defecto: http://localhost:8000 o env API_BASE_URL)",
    )
    seed_parser.add_argument(
        "--username",
        default=os.getenv("ADMIN_USERNAME", os.getenv("ADMIN_EMAIL", "admin")),
        help="Usuario o correo administrador (por defecto: env ADMIN_USERNAME o 'admin')",
    )
    seed_parser.add_argument(
        "--password",
        default=os.getenv("ADMIN_PASSWORD", "Admin12345!"),
        help="Contraseña de administrador (por defecto: env ADMIN_PASSWORD)",
    )
    seed_parser.add_argument(
        "--images-dir",
        default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "demo_images"),
        help="Ruta al directorio de imágenes de prueba",
    )

    args = parser.parse_args()

    if args.command == "seed":
        run_seed(
            base_url=args.url,
            username=args.username,
            password=args.password,
            images_dir=args.images_dir,
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
