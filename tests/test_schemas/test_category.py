import pytest
from pydantic_core import ValidationError

from app.schemas.category import CategoryCreate, CategoryUpdate


class TestCategorySchemas:
    """Test cases for Category schemas"""

    def test_category_create_valid(self):
        """Test valid CategoryCreate schema"""
        category_data = {
            "name": "Electronics",
            "description": "Electronic devices and accessories",
            "slug": "electronics",
            "is_active": True,
            "parent_id": None,
            "image_url": "https://example.com/image.jpg",
            "sort_order": 1,
        }
        category = CategoryCreate(**category_data)

        assert category.name == "Electronics"
        assert category.description == "Electronic devices and accessories"
        assert category.slug == "electronics"
        assert category.is_active is True
        assert category.parent_id is None
        assert category.image_url == "https://example.com/image.jpg"
        assert category.sort_order == 1

    def test_category_create_name_validation(self):
        """Test CategoryCreate name validation"""
        category_data = {
            "name": "A",  # Too short
            "description": "Electronic devices and accessories",
            "slug": "electronics",
            "is_active": True,
            "parent_id": None,
            "image_url": "https://example.com/image.jpg",
            "sort_order": 1,
        }

        with pytest.raises(ValidationError) as exc_info:
            CategoryCreate(**category_data)

        assert "Category name must be at least 2 characters long" in str(exc_info.value)

    def test_category_create_minimal(self):
        """Test CategoryCreate with minimal required fields"""
        category_data = {
            "name": "Electronics",
            "slug": "electronics",
        }
        category = CategoryCreate(**category_data)  # type: ignore[arg-type]

        assert category.name == "Electronics"
        assert category.slug == "electronics"
        assert category.is_active is True  # Default value
        assert category.sort_order == 0  # Default value
        assert category.description is None
        assert category.parent_id is None
        assert category.image_url is None

    def test_category_update_valid(self):
        """Test valid CategoryUpdate schema"""
        update_data = {
            "name": "Updated Electronics",
            "description": "Updated description",
            "is_active": False,
            "parent_id": 1,
            "image_url": "https://example.com/new-image.jpg",
            "sort_order": 2,
        }
        category_update = CategoryUpdate(**update_data)

        assert category_update.name == "Updated Electronics"
        assert category_update.description == "Updated description"
        assert category_update.is_active is False
        assert category_update.parent_id == 1
        assert category_update.image_url == "https://example.com/new-image.jpg"
        assert category_update.sort_order == 2

    def test_category_update_partial(self):
        """Test partial CategoryUpdate schema"""
        update_data = {
            "name": "Updated Electronics",
        }
        category_update = CategoryUpdate(**update_data)  # type: ignore[arg-type]

        assert category_update.name == "Updated Electronics"
        assert category_update.description is None
        assert category_update.is_active is None
        assert category_update.parent_id is None
        assert category_update.image_url is None
        assert category_update.sort_order is None

    def test_category_update_empty(self):
        """Test CategoryUpdate with no fields"""
        category_update = CategoryUpdate()

        assert category_update.name is None
        assert category_update.description is None
        assert category_update.is_active is None
        assert category_update.parent_id is None
        assert category_update.image_url is None
        assert category_update.sort_order is None

    def test_category_create_with_parent(self):
        """Test CategoryCreate with parent category"""
        category_data = {
            "name": "Smartphones",
            "slug": "smartphones",
            "parent_id": 1,
        }
        category = CategoryCreate(**category_data)

        assert category.name == "Smartphones"
        assert category.slug == "smartphones"
        assert category.parent_id == 1

    def test_category_create_defaults(self):
        """Test CategoryCreate default values"""
        category_data = {
            "name": "Test Category",
            "slug": "test-category",
        }
        category = CategoryCreate(**category_data)  # type: ignore[arg-type]

        assert category.is_active is True
        assert category.sort_order == 0
        assert category.parent_id is None
        assert category.description is None
        assert category.image_url is None

    def test_category_create_string_conversion(self):
        """Test CategoryCreate handles string inputs correctly"""
        category_data = {
            "name": "Electronics",
            "slug": "electronics",
            "is_active": "true",  # String que debe convertirse a bool
            "sort_order": "5",  # String que debe convertirse a int
            "parent_id": "10",  # String que debe convertirse a int
        }
        category = CategoryCreate(**category_data)  # type: ignore[arg-type]

        assert category.name == "Electronics"
        assert category.slug == "electronics"
        assert category.is_active is True
        assert category.sort_order == 5
        assert category.parent_id == 10

    def test_category_create_string_conversion_false(self):
        """Test CategoryCreate handles false string inputs correctly"""
        category_data = {
            "name": "Electronics",
            "slug": "electronics",
            "is_active": "false",  # String que debe convertirse a bool False
            "sort_order": "0",  # String que debe convertirse a int 0
            "parent_id": "",  # String vacío que debe convertirse a None
        }
        category = CategoryCreate(**category_data)  # type: ignore[arg-type]

        assert category.is_active is False
        assert category.sort_order == 0
        assert category.parent_id is None

    def test_category_update_string_conversion(self):
        """Test CategoryUpdate handles string inputs correctly"""
        update_data = {
            "name": "Updated Electronics",
            "is_active": "false",  # String que debe convertirse a bool
            "sort_order": "3",  # String que debe convertirse a int
            "parent_id": "5",  # String que debe convertirse a int
        }
        category_update = CategoryUpdate(**update_data)  # type: ignore[arg-type]

        assert category_update.name == "Updated Electronics"
        assert category_update.is_active is False
        assert category_update.sort_order == 3
        assert category_update.parent_id == 5
