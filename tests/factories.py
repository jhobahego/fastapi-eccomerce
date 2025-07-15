"""
Factory classes for creating test data using Factory Boy.
"""

import factory
from decimal import Decimal
from faker import Faker
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.core.security import get_password_hash

fake = Faker()


class UserFactory(factory.Factory):
    """Factory for creating User instances"""

    class Meta:  # type: ignore[misc]
        model = User

    email = factory.Sequence(lambda n: f"user{n}@test.com")
    username = factory.Sequence(lambda n: f"user{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    hashed_password = factory.LazyAttribute(
        lambda obj: get_password_hash("testpassword123")
    )
    is_active = True
    is_superuser = False
    phone = factory.Faker("phone_number")
    address = factory.Faker("address")
    city = factory.Faker("city")
    country = factory.Faker("country")
    postal_code = factory.Faker("postcode")


class SuperUserFactory(UserFactory):
    """Factory for creating superuser instances"""

    is_superuser = True
    email = factory.Sequence(lambda n: f"admin{n}@test.com")
    username = factory.Sequence(lambda n: f"admin{n}")


class CategoryFactory(factory.Factory):
    """Factory for creating Category instances"""

    class Meta:  # type: ignore[misc]
        model = Category

    name = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=200)
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))
    is_active = True
    sort_order = factory.Sequence(lambda n: n)
    image_url = factory.Faker("image_url")


class ProductFactory(factory.Factory):
    """Factory for creating Product instances"""

    class Meta:  # type: ignore[misc]
        model = Product

    name = factory.Faker("catch_phrase")
    description = factory.Faker("text")
    short_description = factory.Faker("sentence")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))
    sku = factory.Sequence(lambda n: f"SKU-{n:06d}")
    price = factory.LazyFunction(
        lambda: Decimal(str(fake.random_int(min=10, max=1000)))
    )
    sale_price = None
    cost_price = factory.LazyAttribute(lambda obj: obj.price * Decimal("0.7"))
    stock_quantity = factory.Faker("random_int", min=0, max=100)
    min_stock_level = 5
    is_active = True
    is_featured = False
    weight = factory.LazyFunction(
        lambda: Decimal(str(fake.random_int(min=100, max=5000))) / 1000
    )


class CartFactory(factory.Factory):
    """Factory for creating Cart instances"""

    class Meta:  # type: ignore[misc]
        model = Cart

    is_active = True
    session_id = factory.Faker("uuid4")


class CartItemFactory(factory.Factory):
    """Factory for creating CartItem instances"""

    class Meta:  # type: ignore[misc]
        model = CartItem

    quantity = factory.Faker("random_int", min=1, max=5)
    unit_price = factory.LazyFunction(
        lambda: Decimal(str(fake.random_int(min=10, max=500)))
    )


class OrderFactory(factory.Factory):
    """Factory for creating Order instances"""

    class Meta:  # type: ignore[misc]
        model = Order

    order_number = factory.Sequence(lambda n: f"ORD-{n:08d}")
    status = OrderStatus.PENDING
    payment_status = PaymentStatus.PENDING
    shipping_address = factory.Faker("address")
    shipping_city = factory.Faker("city")
    shipping_country = factory.Faker("country")
    shipping_postal_code = factory.Faker("postcode")
    shipping_phone = factory.Faker("phone_number")
    billing_address = factory.SelfAttribute("shipping_address")
    billing_city = factory.SelfAttribute("shipping_city")
    billing_country = factory.SelfAttribute("shipping_country")
    billing_postal_code = factory.SelfAttribute("shipping_postal_code")
    subtotal = factory.LazyFunction(
        lambda: Decimal(str(fake.random_int(min=100, max=1000)))
    )
    tax_amount = factory.LazyAttribute(lambda obj: obj.subtotal * Decimal("0.1"))
    shipping_cost = Decimal("10.00")
    discount_amount = Decimal("0.00")
    total_amount = factory.LazyAttribute(
        lambda obj: obj.subtotal
        + obj.tax_amount
        + obj.shipping_cost
        - obj.discount_amount
    )
    payment_method = "credit_card"


class OrderItemFactory(factory.Factory):
    """Factory for creating OrderItem instances"""

    class Meta:  # type: ignore[misc]
        model = OrderItem

    quantity = factory.Faker("random_int", min=1, max=5)
    unit_price = factory.LazyFunction(
        lambda: Decimal(str(fake.random_int(min=10, max=500)))
    )
    product_name = factory.Faker("catch_phrase")
    product_sku = factory.Sequence(lambda n: f"SKU-{n:06d}")
    total_price = factory.LazyAttribute(lambda obj: obj.unit_price * obj.quantity)
