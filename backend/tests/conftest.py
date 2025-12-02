"""
Pytest configuration and fixtures for customer API tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import Base, get_db
from app.main import app
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.seller import Seller
from app.models.product import Product, ProductStatus, ProductVariant, ProductImage
from app.models.category import Category
from app.models.order import Order, OrderStatus, PaymentStatus, OrderItem
from app.models.cart import Cart, Wishlist
from app.models.review import ProductReview
from app.models.banner import Banner, BannerStatus, BannerPosition
from app.models.fcm_token import FCMToken
from app.core.security import create_access_token

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def customer_user(db):
    """Create a test customer user"""
    user = User(
        id="customer-123",
        email="customer@test.com",
        password_hash=get_password_hash("testpassword123"),
        first_name="Test",
        last_name="Customer",
        role=UserRole.CUSTOMER,
        is_active=True,
        is_verified=True,
        phone="1234567890",
        pincode="680001"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def customer_token(customer_user):
    """Create access token for customer user"""
    return create_access_token(data={"sub": customer_user.email})


@pytest.fixture
def authenticated_client(client, customer_token):
    """Create an authenticated test client"""
    client.headers.update({"Authorization": f"Bearer {customer_token}"})
    return client


@pytest.fixture
def seller_user(db):
    """Create a test seller user"""
    user = User(
        id="seller-123",
        email="seller@test.com",
        password_hash=get_password_hash("testpassword123"),
        first_name="Test",
        last_name="Seller",
        role=UserRole.SELLER,
        is_active=True,
        is_verified=True,
        phone="9876543210",
        pincode="680001"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def seller(db, seller_user):
    """Create a test seller"""
    seller_obj = Seller(
        id="seller-profile-123",
        user_id=seller_user.id,
        business_name="Test Business",
        business_type="Retail",
        city="Thrissur",
        state="Kerala",
        pincode="680001",
        is_approved=True
    )
    db.add(seller_obj)
    db.commit()
    db.refresh(seller_obj)
    return seller_obj


@pytest.fixture
def category(db):
    """Create a test category"""
    category_obj = Category(
        id="category-123",
        name="Test Category",
        slug="test-category",
        description="Test category description",
        is_active=True
    )
    db.add(category_obj)
    db.commit()
    db.refresh(category_obj)
    return category_obj


@pytest.fixture
def product(db, seller, category):
    """Create a test product"""
    product_obj = Product(
        id="product-123",
        name="Test Product",
        slug="test-product",
        description="Test product description",
        category_id=category.id,
        seller_id=seller.id,
        seller_price=100.00,
        customer_price=120.00,
        commission_rate=10.00,
        commission_amount=10.00,
        stock_quantity=50,
        status=ProductStatus.APPROVED,
        tax_rate=18.00,
        has_return_policy=True,
        return_period_days=7
    )
    db.add(product_obj)
    db.commit()
    db.refresh(product_obj)
    return product_obj


@pytest.fixture
def product_variant(db, product):
    """Create a test product variant"""
    variant = ProductVariant(
        id="variant-123",
        product_id=product.id,
        variant_name="Large",
        sku="TEST-LARGE",
        seller_price=150.00,
        customer_price=180.00,
        commission_rate=10.00,
        commission_amount=15.00,
        stock_quantity=30,
        is_active=True,
        tax_rate=18.00
    )
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant


@pytest.fixture
def product_image(db, product):
    """Create a test product image"""
    image = ProductImage(
        id="image-123",
        product_id=product.id,
        image_url="https://example.com/image.jpg",
        is_primary=True,
        sort_order=1
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


@pytest.fixture
def order(db, customer_user, product):
    """Create a test order"""
    order_obj = Order(
        id="order-123",
        order_number="ORD-123456",
        customer_id=customer_user.id,
        total_customer_amount=120.00,
        total_tax_amount=21.60,
        grand_total_amount=141.60,
        total_seller_amount=100.00,
        total_commission_amount=10.00,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.COD_PENDING,
        delivery_address="123 Test Street",
        delivery_city="Thrissur",
        delivery_state="Kerala",
        delivery_pincode="680001",
        phone="1234567890"
    )
    db.add(order_obj)
    db.commit()
    db.refresh(order_obj)
    return order_obj


@pytest.fixture
def order_item(db, order, product):
    """Create a test order item"""
    item = OrderItem(
        id="order-item-123",
        order_id=order.id,
        product_id=product.id,
        product_name=product.name,
        quantity=1,
        seller_unit_price=100.00,
        customer_unit_price=120.00,
        commission_unit_rate=10.00,
        commission_unit_amount=10.00,
        total_seller_amount=100.00,
        total_customer_amount=120.00,
        total_commission_amount=10.00,
        tax_rate=18.00,
        tax_unit_amount=21.60,
        total_tax_amount=21.60,
        final_unit_price=141.60,
        total_final_amount=141.60
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@pytest.fixture
def cart_item(db, customer_user, product):
    """Create a test cart item"""
    cart = Cart(
        id="cart-123",
        customer_id=customer_user.id,
        product_id=product.id,
        quantity=2
    )
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart


@pytest.fixture
def wishlist_item(db, customer_user, product):
    """Create a test wishlist item"""
    wishlist = Wishlist(
        id="wishlist-123",
        customer_id=customer_user.id,
        product_id=product.id
    )
    db.add(wishlist)
    db.commit()
    db.refresh(wishlist)
    return wishlist


@pytest.fixture
def review(db, customer_user, product):
    """Create a test review"""
    review_obj = ProductReview(
        id="review-123",
        product_id=product.id,
        customer_id=customer_user.id,
        rating=5,
        comment="Great product!",
        is_approved=True
    )
    db.add(review_obj)
    db.commit()
    db.refresh(review_obj)
    return review_obj


@pytest.fixture
def banner(db, category):
    """Create a test banner"""
    from datetime import datetime, timedelta
    banner_obj = Banner(
        id="banner-123",
        title="Test Banner",
        description="Test banner description",
        image_url="https://example.com/banner.jpg",
        link_url="https://example.com",
        position=BannerPosition.HOME_TOP,
        status=BannerStatus.ACTIVE,
        is_active=True,
        sort_order=1,
        category_id=category.id,
        start_date=datetime.utcnow() - timedelta(days=1),
        end_date=datetime.utcnow() + timedelta(days=30)
    )
    db.add(banner_obj)
    db.commit()
    db.refresh(banner_obj)
    return banner_obj


@pytest.fixture
def fcm_token(db, customer_user):
    """Create a test FCM token"""
    token_obj = FCMToken(
        id="fcm-123",
        user_id=customer_user.id,
        token="test-fcm-token-12345",
        device_type="android",
        is_active=True
    )
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)
    return token_obj



