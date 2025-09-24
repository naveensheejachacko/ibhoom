# Local Vendor Marketplace - Project Documentation

## 🎯 Project Overview

### Business Model
A local vendor marketplace where admin acts as an intermediary between sellers and customers, handling physical fulfillment with cash-on-delivery only.

### Unique Value Proposition
- **Local Focus**: Connect local vendors with nearby customers
- **Admin-Mediated Fulfillment**: Admin collects from seller and delivers to customer
- **Cash-Only**: Simple payment model with cash on delivery
- **Quality Control**: All products require admin approval before listing

---

## 🏗️ System Architecture

### Core Components
1. **Admin Panel** - Product approval, order management, commission settings
2. **Seller Portal** - Product uploads, inventory management, order notifications
3. **Customer App/Web** - Browse products, place orders, track deliveries
4. **Backend APIs** - FastAPI-based microservices
5. **Database** - PostgreSQL with optimized schema

### Technology Stack
```
Backend:     FastAPI (Python 3.11+)
Database:    PostgreSQL 15+
Frontend:    React 18+ with Vite
Mobile:      React Native (Future)
Cache:       Redis
Search:      Elasticsearch (Optional)
Storage:     AWS S3 / Local Storage
Deployment:  Docker + Docker Compose
```

---

## 👥 User Roles & Permissions

### 1. Admin (Super User)
**Capabilities:**
- ✅ Approve/reject seller products
- ✅ Manage categories and attributes
- ✅ Set commission rates (global/category/seller-specific)
- ✅ Receive and manage orders
- ✅ User and seller management
- ✅ Hide/show approved products
- ✅ Analytics and reporting
- ✅ System configuration

### 2. Seller (Vendor)
**Capabilities:**
- ✅ Upload products with images and details
- ✅ Manage inventory and pricing
- ✅ View order notifications
- ✅ Track sales and earnings
- ✅ Update product information
- ✅ View commission deductions
- ❌ Cannot see customer details
- ❌ Cannot modify orders

### 3. Customer (Buyer)
**Capabilities:**
- ✅ Browse approved products
- ✅ Search and filter products
- ✅ Place orders (cash on delivery)
- ✅ Track order status
- ✅ View order history
- ✅ Product reviews and ratings
- ❌ Cannot contact sellers directly

---

## 🗄️ Database Schema Design

### Core Tables

#### 1. Users Table
```sql
users (
    id: UUID PRIMARY KEY,
    email: VARCHAR(255) UNIQUE NOT NULL,
    password_hash: VARCHAR(255) NOT NULL,
    first_name: VARCHAR(100),
    last_name: VARCHAR(100),
    phone: VARCHAR(20),
    role: ENUM('admin', 'seller', 'customer'),
    is_active: BOOLEAN DEFAULT true,
    is_verified: BOOLEAN DEFAULT false,
    created_at: TIMESTAMP,
    updated_at: TIMESTAMP
)
```

#### 2. Categories (Hierarchical)
```sql
categories (
    id: UUID PRIMARY KEY,
    name: VARCHAR(100) NOT NULL,
    slug: VARCHAR(100) UNIQUE,
    description: TEXT,
    parent_id: UUID REFERENCES categories(id),
    level: INTEGER DEFAULT 1,
    sort_order: INTEGER DEFAULT 0,
    is_active: BOOLEAN DEFAULT true,
    created_at: TIMESTAMP
)

-- Example hierarchy:
-- Electronics (level 1)
--   └── Mobile Phones (level 2)
--       ├── Samsung (level 3)
--       └── Nokia (level 3)
-- Fashion (level 1)
--   ├── Men (level 2)
--   │   └── Shirts (level 3)
--   │       ├── Formal (level 4)
--   │       └── Casual (level 4)
--   └── Women (level 2)
```

#### 3. Attributes & Attribute Values
```sql
attributes (
    id: UUID PRIMARY KEY,
    name: VARCHAR(100) NOT NULL,        -- color, size, storage, brand
    type: ENUM('text', 'select', 'multiselect', 'number'),
    is_required: BOOLEAN DEFAULT false,
    sort_order: INTEGER DEFAULT 0,
    created_at: TIMESTAMP
)

attribute_values (
    id: UUID PRIMARY KEY,
    attribute_id: UUID REFERENCES attributes(id),
    value: VARCHAR(255) NOT NULL,       -- Red, Large, 128GB, Samsung
    sort_order: INTEGER DEFAULT 0,
    created_at: TIMESTAMP
)

category_attributes (
    id: UUID PRIMARY KEY,
    category_id: UUID REFERENCES categories(id),
    attribute_id: UUID REFERENCES attributes(id),
    is_required: BOOLEAN DEFAULT false,
    is_variant: BOOLEAN DEFAULT false,  -- affects pricing/inventory
    created_at: TIMESTAMP
)
```

#### 4. Sellers
```sql
sellers (
    id: UUID PRIMARY KEY,
    user_id: UUID REFERENCES users(id),
    business_name: VARCHAR(255) NOT NULL,
    business_type: VARCHAR(100),
    address: TEXT NOT NULL,
    city: VARCHAR(100),
    state: VARCHAR(100),
    pincode: VARCHAR(10),
    is_approved: BOOLEAN DEFAULT false,
    approval_date: TIMESTAMP,
    created_at: TIMESTAMP,
    updated_at: TIMESTAMP
)
```

#### 5. Products
```sql
products (
    id: UUID PRIMARY KEY,
    seller_id: UUID REFERENCES sellers(id),
    category_id: UUID REFERENCES categories(id),
    name: VARCHAR(255) NOT NULL,
    description: TEXT,
    short_description: VARCHAR(500),
    sku: VARCHAR(100) UNIQUE,
    seller_price: DECIMAL(10,2) NOT NULL,        -- Price seller gets
    commission_rate: DECIMAL(5,2) NOT NULL,      -- Commission % for this product
    commission_amount: DECIMAL(10,2) NOT NULL,   -- Calculated commission
    customer_price: DECIMAL(10,2) NOT NULL,      -- Final price customer pays
    status: ENUM('draft', 'pending', 'approved', 'rejected', 'hidden'),
    approval_date: TIMESTAMP,
    rejection_reason: TEXT,
    is_active: BOOLEAN DEFAULT true,
    meta_title: VARCHAR(255),
    meta_description: VARCHAR(500),
    tags: TEXT[],
    created_at: TIMESTAMP,
    updated_at: TIMESTAMP
)
```

#### 6. Product Variants
```sql
product_variants (
    id: UUID PRIMARY KEY,
    product_id: UUID REFERENCES products(id),
    variant_name: VARCHAR(255),        -- "Red Large", "128GB Black"
    sku: VARCHAR(100) UNIQUE,
    seller_price: DECIMAL(10,2) NOT NULL,        -- Price seller gets for this variant
    commission_rate: DECIMAL(5,2) NOT NULL,      -- Commission % for this variant
    commission_amount: DECIMAL(10,2) NOT NULL,   -- Calculated commission
    customer_price: DECIMAL(10,2) NOT NULL,      -- Final price customer pays
    stock_quantity: INTEGER DEFAULT 0,
    is_active: BOOLEAN DEFAULT true,
    created_at: TIMESTAMP,
    updated_at: TIMESTAMP
)

product_variant_attributes (
    id: UUID PRIMARY KEY,
    variant_id: UUID REFERENCES product_variants(id),
    attribute_id: UUID REFERENCES attributes(id),
    attribute_value_id: UUID REFERENCES attribute_values(id),
    custom_value: VARCHAR(255),        -- For text inputs
    created_at: TIMESTAMP
)
```

#### 7. Product Images
```sql
product_images (
    id: UUID PRIMARY KEY,
    product_id: UUID REFERENCES products(id),
    variant_id: UUID REFERENCES product_variants(id) NULL,
    image_url: VARCHAR(500) NOT NULL,
    alt_text: VARCHAR(255),
    is_primary: BOOLEAN DEFAULT false,
    sort_order: INTEGER DEFAULT 0,
    created_at: TIMESTAMP
)
```

#### 8. Orders
```sql
orders (
    id: UUID PRIMARY KEY,
    order_number: VARCHAR(50) UNIQUE NOT NULL,
    customer_id: UUID REFERENCES users(id),
    total_customer_amount: DECIMAL(10,2) NOT NULL,    -- Total amount customer pays
    total_seller_amount: DECIMAL(10,2) NOT NULL,      -- Total amount sellers get
    total_commission_amount: DECIMAL(10,2) NOT NULL,  -- Total commission admin gets
    status: ENUM('pending', 'confirmed', 'collected', 'out_for_delivery', 'delivered', 'cancelled'),
    delivery_address: TEXT NOT NULL,
    customer_phone: VARCHAR(20) NOT NULL,
    customer_name: VARCHAR(255) NOT NULL,
    notes: TEXT,
    created_at: TIMESTAMP,
    updated_at: TIMESTAMP
)

order_items (
    id: UUID PRIMARY KEY,
    order_id: UUID REFERENCES orders(id),
    product_id: UUID REFERENCES products(id),
    variant_id: UUID REFERENCES product_variants(id) NULL,
    seller_id: UUID REFERENCES sellers(id),
    product_name: VARCHAR(255) NOT NULL,
    variant_details: TEXT,
    quantity: INTEGER NOT NULL,
    seller_unit_price: DECIMAL(10,2) NOT NULL,        -- Price seller gets per unit
    customer_unit_price: DECIMAL(10,2) NOT NULL,      -- Price customer pays per unit
    commission_unit_rate: DECIMAL(5,2) NOT NULL,      -- Commission rate per unit
    commission_unit_amount: DECIMAL(10,2) NOT NULL,   -- Commission amount per unit
    total_seller_amount: DECIMAL(10,2) NOT NULL,      -- Total seller amount for this item
    total_customer_amount: DECIMAL(10,2) NOT NULL,    -- Total customer amount for this item
    total_commission_amount: DECIMAL(10,2) NOT NULL,  -- Total commission for this item
    created_at: TIMESTAMP
)
```

#### 9. Commission Settings
```sql
commission_settings (
    id: UUID PRIMARY KEY,
    type: ENUM('global', 'category', 'product'),
    entity_id: UUID NULL,              -- category_id or product_id
    commission_rate: DECIMAL(5,2) NOT NULL,
    min_seller_price: DECIMAL(10,2) DEFAULT 0.00,
    max_seller_price: DECIMAL(10,2) NULL,
    is_active: BOOLEAN DEFAULT true,
    effective_from: TIMESTAMP,
    effective_until: TIMESTAMP NULL,
    created_at: TIMESTAMP
)
```

---

## 🔄 Business Flow

### 1. Seller Onboarding
```
1. Seller registers account
2. Admin reviews and approves seller
3. Seller can start uploading products
```

### 2. Product Lifecycle
```
1. Seller uploads product with details and images
2. Admin reviews product
3. Admin approves/rejects with reasons
4. Approved products visible to customers
5. Admin can hide products anytime
```

### 3. Order Processing
```
1. Customer places order (cash on delivery)
2. Admin receives order notification
3. Admin confirms order
4. Admin collects product from seller
5. Admin delivers to customer
6. Payment collected and distributed
```

### 4. Commission Calculation & Price Flow
```
Seller Sets Price: ₹1000
Admin Sets Commission Rate: 10%
Commission Amount: ₹1000 × 10% = ₹100
Final Customer Price: ₹1000 + ₹100 = ₹1100

When Customer Orders:
- Customer Pays: ₹1100
- Seller Receives: ₹1000 (Original price)
- Admin Receives: ₹100 (Commission)
```

### Commission Priority (Product-Level)
```
1. Individual Product Commission (if set)
2. Category Commission (if no product-specific rate)
3. Global Default Commission (fallback)

Example:
- Global Rate: 8%
- Electronics Category Rate: 12%
- Specific iPhone Product Rate: 15%
- Result: iPhone uses 15% commission
```

---

## 📱 Application Structure

### Backend (FastAPI)
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── dependencies.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── ...
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   └── ...
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── admin/
│   │   │   │   ├── users.py
│   │   │   │   ├── products.py
│   │   │   │   ├── orders.py
│   │   │   │   └── analytics.py
│   │   │   ├── seller/
│   │   │   │   ├── products.py
│   │   │   │   ├── orders.py
│   │   │   │   └── profile.py
│   │   │   └── customer/
│   │   │       ├── products.py
│   │   │       ├── orders.py
│   │   │       └── profile.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── product_service.py
│   │   ├── order_service.py
│   │   └── commission_service.py
│   └── utils/
│       ├── __init__.py
│       ├── email.py
│       ├── image_upload.py
│       └── helpers.py
├── alembic/
├── tests/
├── requirements.txt
└── docker-compose.yml
```

### Frontend (React)
```
frontend/
├── admin/                  # Admin React App
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── utils/
├── seller/                 # Seller React App
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── utils/
└── customer/               # Customer React App (Future)
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── hooks/
    │   ├── services/
    │   └── utils/
```

---

## 🚀 Development Phases

### Phase 1: Core Backend (Weeks 1-3)
- ✅ Setup FastAPI project structure
- ✅ Database schema and models
- ✅ Authentication system
- ✅ Basic CRUD operations
- ✅ Admin APIs (users, sellers, products)

### Phase 2: Seller APIs (Weeks 4-5)
- ✅ Seller product management
- ✅ Order notifications
- ✅ Sales tracking
- ✅ Image upload system

### Phase 3: Customer APIs (Weeks 6-7)
- ✅ Product browsing and search
- ✅ Order placement
- ✅ Order tracking

### Phase 4: Admin Frontend (Weeks 8-10)
- ✅ React admin dashboard
- ✅ Product approval interface
- ✅ Order management
- ✅ Analytics dashboard

### Phase 5: Seller Frontend (Weeks 11-12)
- ✅ React seller portal
- ✅ Product upload interface
- ✅ Order management
- ✅ Sales dashboard

### Phase 6: Customer Frontend (Weeks 13-15)
- ✅ Customer web app
- ✅ Product catalog
- ✅ Order placement
- ✅ Order tracking

---

## 🔧 Technical Requirements

### Minimum Requirements
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- 8GB RAM
- 50GB Storage

### Production Requirements
- Load Balancer (Nginx)
- SSL Certificates
- CDN for images
- Backup strategy
- Monitoring (Grafana/Prometheus)
- Error tracking (Sentry)

---

## 📊 Key Features

### Admin Panel
- ✅ Dashboard with key metrics
- ✅ Product approval workflow
- ✅ Dynamic commission management
- ✅ Order tracking and management
- ✅ User and seller management
- ✅ Category and attribute management
- ✅ Analytics and reporting

### Seller Portal
- ✅ Product upload with variants
- ✅ Inventory management
- ✅ Order notifications
- ✅ Sales analytics
- ✅ Commission tracking
- ✅ Bulk product operations

### Customer Features
- ✅ Advanced product search
- ✅ Filter by attributes
- ✅ Product comparison
- ✅ Order tracking
- ✅ Review and rating system
- ✅ Wishlist functionality

---

## 🔐 Security Considerations

### Authentication
- JWT tokens with refresh mechanism
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Rate limiting on APIs

### Data Security
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CORS configuration
- API versioning

### File Upload Security
- File type validation
- File size limits
- Virus scanning
- Secure file storage

---

## 📈 Scalability Considerations

### Database Optimization
- Proper indexing strategy
- Query optimization
- Connection pooling
- Read replicas for heavy reads

### Caching Strategy
- Redis for session storage
- Cache frequently accessed data
- Image CDN for faster delivery

### Performance
- Async operations where possible
- Database connection pooling
- Image optimization and compression
- API response compression

---

## 🧪 Testing Strategy

### Backend Testing
- Unit tests for services
- Integration tests for APIs
- Database testing with fixtures
- Performance testing

### Frontend Testing
- Component testing with Jest
- E2E testing with Playwright
- User flow testing
- Accessibility testing

---

## 📝 Next Steps

1. **Review and approve** this documentation
2. **Create detailed API specifications**
3. **Setup development environment**
4. **Start with database schema implementation**
5. **Build core authentication system**
6. **Implement admin APIs first**

---

**Questions for Discussion:**

1. Any modifications needed to the database schema?
2. Should we add multi-language support?
3. Do you want mobile app development included?
4. Any specific integrations required (SMS, Email)?
5. Preferred deployment strategy (Cloud/On-premise)?
6. Budget and timeline constraints?

Let me know your thoughts on this documentation, and we can start with the implementation! 