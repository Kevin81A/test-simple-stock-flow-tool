"""
Command-Line Interface (CLI) for ssf_tool.
"""

import argparse
import os
import sys
from .seeder import run_seed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simple Stock Flow · Demo Seeder and Utility Tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: seed
    seed_parser = subparsers.add_parser("seed", help="Seed demo products, images, and sales")
    seed_parser.add_argument(
        "--url",
        default=os.getenv("API_BASE_URL", "http://localhost:8000"),
        help="Base API URL (default: http://localhost:8000 or env API_BASE_URL)",
    )
    seed_parser.add_argument(
        "--username",
        default=os.getenv("ADMIN_USERNAME", os.getenv("ADMIN_EMAIL", "admin")),
        help="Admin username or email (default: env ADMIN_USERNAME or 'admin')",
    )
    seed_parser.add_argument(
        "--password",
        default=os.getenv("ADMIN_PASSWORD", "Admin12345!"),
        help="Admin password (default: env ADMIN_PASSWORD)",
    )
    seed_parser.add_argument(
        "--images-dir",
        default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "demo_images"),
        help="Path to directory containing sample demo images",
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