import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.category import Category


class TestCategoryModel:
    """Test cases for Category model"""

    def test_create_category(self, db_session: Session):
        """Test creating a category"""
        category = Category(
            name="Electronics",
            description="Electronic devices and accessories",
            slug="electronics",
            is_active=True,
            sort_order=1,
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        assert category.id is not None
        assert category.name == "Electronics"
        assert category.description == "Electronic devices and accessories"
        assert category.slug == "electronics"
        assert category.is_active is True
        assert category.sort_order == 1
        assert category.created_at is not None
        assert isinstance(category.created_at, datetime)

    def test_category_parent_child_relationship(self, db_session: Session):
        """Test parent-child relationship between categories"""
        parent_category = Category(
            name="Electronics",
            slug="electronics",
            is_active=True,
        )
        db_session.add(parent_category)
        db_session.commit()
        db_session.refresh(parent_category)

        child_category = Category(
            name="Smartphones",
            slug="smartphones",
            is_active=True,
            parent_id=parent_category.id,
        )
        db_session.add(child_category)
        db_session.commit()
        db_session.refresh(child_category)

        assert child_category.parent_id == parent_category.id
        assert child_category.parent == parent_category
        assert child_category in parent_category.children

    def test_category_unique_slug(self, db_session: Session):
        """Test that category slug must be unique"""
        category1 = Category(
            name="Electronics",
            slug="electronics",
            is_active=True,
        )
        db_session.add(category1)
        db_session.commit()

        category2 = Category(
            name="Electronic Devices",
            slug="electronics",
            is_active=True,
        )
        db_session.add(category2)

        with pytest.raises(Exception):  # IntegrityError will be raised
            db_session.commit()

    def test_category_defaults(self, db_session: Session):
        """Test default values for category fields"""
        category = Category(
            name="Test Category",
            slug="test-category",
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        assert category.is_active is True
        assert category.sort_order == 0
        assert category.parent_id is None
        assert category.description is None
        assert category.image_url is None

    def test_category_str_representation(self, db_session: Session):
        """Test string representation of category"""
        category = Category(
            name="Electronics",
            slug="electronics",
        )
        db_session.add(category)
        db_session.commit()

        assert str(category) == "Electronics"
