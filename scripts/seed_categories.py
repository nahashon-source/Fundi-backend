"""
Seeds initial service categories. Safe to run multiple times --
skips any category whose slug already exists, so it won't create
duplicates on repeated runs (e.g. after a fresh deploy).
"""
import sys
import os
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models.category import Category

INITIAL_CATEGORIES = [
    {"name": "Plumbing", "slug": "plumber", "icon": "Wrench"},
    {"name": "Electrical", "slug": "electrician", "icon": "Zap"},
    {"name": "Painting", "slug": "painter", "icon": "Paintbrush"},
]


def seed_categories() -> None:
    db = SessionLocal()
    try:
        for cat in INITIAL_CATEGORIES:
            exists = db.query(Category).filter(Category.slug == cat["slug"]).first()
            if exists:
                print(f"Skipping '{cat['name']}' -- already exists.")
                continue
            db.add(Category(**cat))
            print(f"Added category: {cat['name']}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_categories()