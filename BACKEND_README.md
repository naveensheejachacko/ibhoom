# Local Vendor Marketplace - Backend API

## 🚀 Quick Start

### 1. Setup Virtual Environment
```bash
# Already created and activated
source venv/bin/activate
```

### 2. Install Dependencies
```bash
# Already installed
pip install -r backend/requirements.txt
```

### 3. Initialize Database
```bash
# Run the test script to create tables and default data
python test_backend.py
```

### 4. Start the Server
```bash
# Method 1: Using uvicorn (recommended)
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Using Python directly
cd backend && python -m app.main
```

## 📚 API Documentation

### Interactive Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Base URL
```
http://localhost:8000
```

## 🔐 Authentication

### JWT Token-based Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### Default Admin Credentials
```
Email: admin@marketplace.com
Password: admin123
```

## 📋 API Endpoints

### Authentication
```
POST /api/v1/auth/login              # Login (all user types)
POST /api/v1/auth/register/admin     # Register admin (dev only)
POST /api/v1/auth/register/seller    # Register seller
POST /api/v1/auth/register/customer  # Register customer
GET  /api/v1/auth/me                 # Get current user info
```

### Example API Calls

#### 1. Admin Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@marketplace.com",
    "password": "admin123"
  }'
```

#### 2. Register a Seller
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register/seller" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "1234567890",
    "business_name": "John's Electronics",
    "business_type": "Electronics Store",
    "address": "123 Main St, City, State",
    "city": "City",
    "state": "State",
    "pincode": "12345"
  }'
```

#### 3. Register a Customer
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register/customer" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "password123",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone": "0987654321"
  }'
```

#### 4. Get Current User (requires token)
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <your_access_token>"
```

## 🗄️ Database Schema

### SQLite Database: `marketplace.db`

**Key Tables:**
- `users` - All user accounts (admin, seller, customer)
- `sellers` - Seller business information
- `categories` - Product categories (hierarchical)
- `attributes` - Product attributes (color, size, etc.)
- `products` - Products with commission pricing
- `product_variants` - Product variations
- `orders` - Customer orders
- `commission_settings` - Commission rates

## 💰 Commission System

### How It Works:
```
Seller Price: ₹1000
Commission Rate: 8%
Commission Amount: ₹80
Customer Price: ₹1080

Distribution:
- Customer Pays: ₹1080
- Seller Gets: ₹1000
- Admin Gets: ₹80
```

### Commission Priority:
1. **Product-specific rate** (highest priority)
2. **Category-specific rate** (medium priority)  
3. **Global default rate** (fallback - 8%)

## 🔧 Development

### Project Structure
```
backend/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── core/
│   │   ├── config.py          # Settings
│   │   ├── database.py        # DB setup
│   │   ├── security.py        # JWT & password
│   │   └── dependencies.py    # Auth dependencies
│   ├── models/                # SQLAlchemy models
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── ...
│   ├── schemas/               # Pydantic schemas
│   ├── api/v1/               # API routes
│   │   ├── auth.py
│   │   ├── admin/
│   │   ├── seller/
│   │   └── customer/
│   ├── services/             # Business logic
│   └── utils/               # Utilities
├── requirements.txt
└── marketplace.db           # SQLite database
```

### Adding New Features

#### 1. Create Model
```python
# app/models/new_model.py
from sqlalchemy import Column, String
from ..core.database import Base

class NewModel(Base):
    __tablename__ = "new_models"
    
    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
```

#### 2. Create Schema
```python
# app/schemas/new_schema.py
from pydantic import BaseModel

class NewModelCreate(BaseModel):
    name: str

class NewModelResponse(BaseModel):
    id: str
    name: str
    
    class Config:
        from_attributes = True
```

#### 3. Create API Route
```python
# app/api/v1/new_route.py
from fastapi import APIRouter, Depends
from ...core.dependencies import get_admin_user

router = APIRouter()

@router.post("/", response_model=NewModelResponse)
async def create_item(
    item: NewModelCreate,
    current_user = Depends(get_admin_user)
):
    # Implementation
    pass
```

## 🧪 Testing

### Test the APIs
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test root endpoint
curl http://localhost:8000/

# View API docs
open http://localhost:8000/docs
```

## 🚦 Next Steps

### Phase 1: Core APIs (Current)
- ✅ Authentication system
- ✅ User management
- ✅ Database models
- ⏳ Category management APIs
- ⏳ Product management APIs
- ⏳ Order management APIs

### Phase 2: Admin APIs
- ⏳ Product approval workflow
- ⏳ Commission management
- ⏳ User/seller management
- ⏳ Analytics endpoints

### Phase 3: Seller APIs
- ⏳ Product upload
- ⏳ Inventory management
- ⏳ Order notifications
- ⏳ Sales tracking

### Phase 4: Customer APIs
- ⏳ Product browsing
- ⏳ Order placement
- ⏳ Order tracking

## 🔧 Configuration

### Environment Variables (.env)
```env
# App Configuration
APP_NAME="Local Vendor Marketplace"
DEBUG=True

# Database
DATABASE_URL="sqlite:///./marketplace.db"

# JWT
JWT_SECRET_KEY="your-super-secret-key"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin
ADMIN_EMAIL="admin@marketplace.com"
ADMIN_PASSWORD="admin123"

# Commission
DEFAULT_COMMISSION_RATE=8.0
```

## 📝 Notes

- **SQLite** is used for development (easy setup)
- **JWT tokens** expire in 30 minutes
- **Refresh tokens** expire in 7 days
- **Commission rates** are stored as percentages (8.0 = 8%)
- **File uploads** go to `/uploads` directory
- **CORS** is enabled for frontend development

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're in the virtual environment
2. **Database Errors**: Run `python test_backend.py` to recreate tables
3. **Port in Use**: Change port in startup command
4. **Permission Denied**: Check file permissions in uploads directory

### Logs
Check the terminal where uvicorn is running for detailed error logs.

## 🎯 Ready for Development!

Your backend is now running and ready for frontend integration. The API documentation is available at http://localhost:8000/docs where you can test all endpoints interactively. 