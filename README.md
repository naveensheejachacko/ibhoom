# ibhoom - Local Vendor Marketplace

A comprehensive e-commerce platform that connects local vendors with customers, featuring a multi-role system with admin, seller, and customer interfaces.

## 🚀 Features

### **Admin Panel**
- Dashboard with user and order statistics
- User management (activate/deactivate users)
- Seller management (approve/reject sellers)
- Product approval system
- Category management with hierarchical structure
- Order management and tracking
- Commission management

### **Seller Panel**
- Product creation with dynamic category selection
- Image upload and management
- Product variants and attributes
- Order management
- Sales analytics
- Commission tracking

### **Customer Features**
- Product browsing and search
- Category-based filtering
- Product reviews and ratings
- Order placement and tracking
- User account management

## 🛠️ Tech Stack

### **Backend**
- **Framework**: FastAPI (Python)
- **Database**: SQLite (development)
- **Authentication**: JWT tokens
- **Password Hashing**: Argon2 + bcrypt
- **ORM**: SQLAlchemy
- **File Upload**: Python-multipart

### **Frontend**
- **Framework**: React 18 with TypeScript
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Build Tool**: Vite

## 📋 Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **Git**

## 🚀 Quick Start

### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/ibhoom.git
cd ibhoom
```

### **2. Backend Setup**

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database (IMPORTANT for new clones)
python -c "from app.core.database import create_database; create_database(); print('Database initialized successfully!')"

# Create default admin user (optional)
python -c "
from app.core.database import get_db
from app.models.user import User, UserRole
from app.core.security import pwd_context
from sqlalchemy.orm import Session
import uuid

db = next(get_db())
# Check if admin already exists
admin = db.query(User).filter(User.email == 'admin@gmail.com').first()
if not admin:
    admin_user = User(
        id=str(uuid.uuid4()),
        email='admin@gmail.com',
        hashed_password=pwd_context.hash('admin123'),
        first_name='Admin',
        last_name='User',
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    db.add(admin_user)
    db.commit()
    print('Default admin user created: admin@gmail.com / admin123')
else:
    print('Admin user already exists')
db.close()
"

# Start the backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### **3. Frontend Setup**

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 🔐 Default Credentials

### **Admin Account**
- **Email**: `admin@gmail.com`
- **Password**: `admin123`

### **Seller Account**
- **Email**: `seller@example.com`
- **Password**: `password123`

## 📁 Project Structure

```
ibhoom/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── admin/          # Admin endpoints
│   │   │   ├── seller/         # Seller endpoints
│   │   │   ├── customer/       # Customer endpoints
│   │   │   └── auth.py         # Authentication
│   │   ├── core/
│   │   │   ├── config.py       # Configuration
│   │   │   ├── database.py     # Database setup
│   │   │   ├── dependencies.py # Auth dependencies
│   │   │   └── security.py     # JWT & password hashing
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Business logic
│   │   └── main.py             # FastAPI app
│   ├── requirements.txt
│   └── marketplace.db          # SQLite database
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable components
│   │   ├── pages/              # Page components
│   │   │   ├── Admin/          # Admin pages
│   │   │   ├── Seller/         # Seller pages
│   │   │   └── Customer/       # Customer pages
│   │   ├── lib/                # API client
│   │   ├── types/              # TypeScript types
│   │   └── App.tsx             # Main app component
│   ├── public/
│   │   └── ibhoom-logo.png     # Logo file
│   └── package.json
└── README.md
```

## 🔧 Configuration

### **Backend Configuration**
The backend uses environment variables for configuration. Key settings in `backend/app/core/config.py`:

```python
# JWT Configuration
JWT_SECRET_KEY = "your-super-secret-jwt-key-change-this-in-production"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS Configuration
BACKEND_CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000"]

# Database
DATABASE_URL = "sqlite:///./marketplace.db"
```

### **Frontend Configuration**
The frontend API base URL is configured in `frontend/src/lib/api.ts`:

```typescript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

## 🗄️ Database Schema

### **Core Tables**
- **users** - User accounts (admin, seller, customer)
- **sellers** - Seller profiles and business info
- **categories** - Hierarchical product categories
- **products** - Product information
- **orders** - Customer orders
- **order_items** - Individual items in orders
- **product_reviews** - Customer reviews

### **Key Relationships**
- Users can have multiple roles
- Products belong to categories (hierarchical)
- Orders contain multiple order items
- Products can have multiple variants and images

## 🚀 API Endpoints

### **Authentication**
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user

### **Admin Endpoints**
- `GET /api/v1/admin/users/stats` - User statistics
- `GET /api/v1/admin/orders/stats` - Order statistics
- `GET /api/v1/admin/users` - List users
- `PUT /api/v1/admin/users/{id}/status` - Update user status

### **Seller Endpoints**
- `GET /api/v1/seller/products` - List seller products
- `POST /api/v1/seller/products` - Create product
- `PUT /api/v1/seller/products/{id}` - Update product

### **Customer Endpoints**
- `GET /api/v1/customer/products` - Browse products
- `GET /api/v1/customer/categories` - Get categories
- `POST /api/v1/customer/orders` - Place order

## 🎨 UI Components

### **Key Components**
- **DynamicCategorySelector** - Hierarchical category selection
- **Toast** - Notification system
- **ProtectedRoute** - Authentication guard
- **ProductForm** - Product creation/editing

### **Styling**
- Tailwind CSS for utility-first styling
- Custom color scheme (primary, secondary)
- Responsive design for all screen sizes
- Modern UI with clean aesthetics

## 🔒 Security Features

- **JWT Authentication** with access and refresh tokens
- **Password Hashing** using Argon2 (with bcrypt fallback)
- **Role-based Access Control** (admin, seller, customer)
- **CORS Protection** configured for development
- **Input Validation** using Pydantic schemas
- **SQL Injection Protection** via SQLAlchemy ORM

## 🧪 Testing

### **Backend Testing**
```bash
cd backend
pytest
```

### **Frontend Testing**
```bash
cd frontend
npm test
```

## 📦 Deployment

### **Backend Deployment on Render**

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

**Quick Setup:**
1. **Root Directory**: `backend`
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables**:
   - `JWT_SECRET_KEY`: Generate a secure random string
   - `BACKEND_CORS_ORIGINS`: Your frontend URL
   - `DEBUG`: `false`

**Render Configuration:**
```yaml
# render.yaml
services:
  - type: web
    name: ibhoom-backend
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### **Frontend Deployment**
1. Build the production bundle:
```bash
npm run build
```
2. Deploy the `dist` folder to your hosting service (Vercel, Netlify, etc.)
3. Update API base URL in your frontend to point to your deployed backend

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check the browser console for frontend errors
2. Check the backend logs for server errors
3. Ensure all dependencies are installed correctly
4. Verify the database is properly initialized

## 🎯 Roadmap

- [ ] Payment gateway integration
- [ ] Real-time notifications
- [ ] Advanced analytics dashboard
- [ ] Mobile app development
- [ ] Multi-language support
- [ ] Advanced search and filtering
- [ ] Inventory management
- [ ] Shipping integration

## 📞 Contact

For questions or support, please contact:
- **Email**: support@ibhoom.com
- **GitHub Issues**: [Create an issue](https://github.com/yourusername/ibhoom/issues)

---

**Made with ❤️ by the ibhoom team**