# 🛒 ibhoom - Local Vendor Marketplace Platform

A comprehensive full-stack e-commerce platform that connects local vendors with customers, featuring a multi-role system with admin, seller, and customer interfaces. Built with FastAPI and React, designed for local businesses in Kerala, India.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12-blue)
![React](https://img.shields.io/badge/react-18.2-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Architecture](#architecture)
5. [Getting Started](#getting-started)
6. [Configuration](#configuration)
7. [API Documentation](#api-documentation)
8. [Project Structure](#project-structure)
9. [Database Schema](#database-schema)
10. [Development Guide](#development-guide)
11. [Deployment](#deployment)
12. [Security](#security)
13. [Contributing](#contributing)
14. [License](#license)

---

## 🎯 Overview

**ibhoom** is a local vendor marketplace platform designed to help local businesses sell their products online. The platform supports three main user roles:

- **Admins**: Manage the platform, approve sellers and products, handle commissions
- **Sellers**: Create and manage products, handle orders, track sales
- **Customers**: Browse products, place orders, leave reviews

### Key Highlights

- ✅ **Location-based filtering** - Products filtered by customer location
- ✅ **Multi-variant products** - Support for product variants (size, color, etc.)
- ✅ **Commission system** - Flexible commission rates per category/product
- ✅ **Real-time notifications** - Firebase Cloud Messaging integration
- ✅ **Image management** - Cloudinary integration for product images
- ✅ **Order tracking** - Complete order lifecycle management
- ✅ **Review system** - Customer reviews and ratings

---

## ✨ Features

### 👨‍💼 Admin Panel

- **Dashboard**: User and order statistics, sales analytics
- **User Management**: Activate/deactivate users, view user details
- **Seller Management**: Approve/reject seller registrations
- **Product Approval**: Review and approve/reject products
- **Category Management**: Hierarchical category structure with attributes
- **Attribute Management**: Create and manage product attributes
- **Order Management**: View and manage all orders
- **Commission Management**: Set commission rates per category/product
- **Banner Management**: Manage promotional banners

### 🏪 Seller Panel

- **Dashboard**: Sales analytics, order statistics
- **Product Management**: Create, edit, and manage products
- **Variant System**: Create products with multiple variants (size, color, etc.)
- **Image Upload**: Upload and manage product images
- **Order Management**: View and process customer orders
- **Profile Settings**: Manage business information and location
- **Sales Reports**: Track sales and commissions

### 🛍️ Customer Features

- **Product Browsing**: Browse products by category
- **Location-based Filtering**: See products from nearby sellers
- **Search & Filter**: Search products and filter by various criteria
- **Product Details**: View detailed product information with variants
- **Shopping Cart**: Add products to cart
- **Wishlist**: Save favorite products
- **Order Placement**: Place and track orders
- **Reviews & Ratings**: Leave reviews and ratings for products
- **Order History**: View past orders

---

## 🛠️ Tech Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12 | Programming language |
| **FastAPI** | 0.104.1 | Web framework |
| **Uvicorn** | 0.24.0 | ASGI server |
| **SQLAlchemy** | 2.0.23 | ORM |
| **Alembic** | 1.12.1 | Database migrations |
| **PostgreSQL** | 14+ | Production database |
| **Pydantic** | 2.5.0 | Data validation |
| **JWT** | python-jose | Authentication |
| **Argon2/Bcrypt** | passlib | Password hashing |
| **Cloudinary** | 1.41.0 | Image hosting |
| **Firebase Admin** | 6.5.0 | Push notifications |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.2.0 | UI framework |
| **TypeScript** | 5.2.2 | Type safety |
| **Vite** | 5.0.0 | Build tool |
| **React Router** | 6.20.1 | Routing |
| **Axios** | 1.6.2 | HTTP client |
| **Tailwind CSS** | 3.3.6 | Styling |
| **Lucide React** | 0.294.0 | Icons |
| **Firebase** | 12.6.0 | Client SDK |
| **React Easy Crop** | 5.5.3 | Image cropping |

### Infrastructure

- **Web Server**: Nginx 1.24.0
- **Process Manager**: systemd
- **CDN/Proxy**: Cloudflare
- **Database**: PostgreSQL (production), SQLite (development)

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────┐
│              Cloudflare CDN                      │
│  - SSL/TLS Termination                           │
│  - DDoS Protection                               │
│  - CDN Caching                                   │
└──────────────┬──────────────────────────────────┘
               │
               │ HTTPS (443)
               │
┌──────────────▼──────────────────────────────────┐
│         Hostinger VPS (KVM2)                     │
│  ┌──────────────────────────────────────────┐  │
│  │         Nginx (Port 80)                   │  │
│  │  - Frontend: ibhoom.in                    │  │
│  │  - Backend API: api.ibhoom.in            │  │
│  └──────┬───────────────────┬────────────────┘  │
│         │                   │                    │
│  ┌──────▼──────┐    ┌──────▼──────┐            │
│  │   React     │    │   FastAPI    │            │
│  │  Frontend   │    │   Backend    │            │
│  │  (Static)   │    │  (Port 8000) │            │
│  └─────────────┘    └──────┬──────┘            │
│                             │                    │
│                      ┌──────▼──────┐            │
│                      │ PostgreSQL  │            │
│                      │  Database   │            │
│                      │  (Port 5432)│            │
│                      └─────────────┘            │
└─────────────────────────────────────────────────┘
```

### Domain Structure

- **Frontend**: `https://ibhoom.in` → React application
- **Backend API**: `https://api.ibhoom.in` → FastAPI backend
- **WWW**: `https://www.ibhoom.in` → Redirects to main domain

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ (20+ recommended)
- **Python** 3.11+ (3.12 recommended)
- **PostgreSQL** 14+ (for production)
- **Git**
- **npm** or **yarn**

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/naveensheejachacko/ibhoom.git
cd ibhoom
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cp .env.example .env  # If exists, or create manually
nano .env  # Edit with your configuration

# Run database migrations
alembic upgrade head

# Initialize database (creates admin user)
python -c "from app.utils.init_db import init_db; init_db()"

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

---

## ⚙️ Configuration

### Backend Environment Variables

Create `backend/.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ibhoom_db
# For SQLite (development): sqlite:///./marketplace.db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://ibhoom.in

# App Configuration
DEBUG=true  # Set to false in production
APP_NAME=ibhoom
APP_VERSION=1.0.0

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880  # 5MB

# Admin Configuration
ADMIN_EMAIL=admin@ibhoom.in
ADMIN_PASSWORD=change_this_password

# Cloudinary (Optional - for image hosting)
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# Firebase (Optional - for push notifications)
FIREBASE_ENABLED=false
FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-service-account.json

# Mapbox (Optional - for geocoding)
MAPBOX_ACCESS_TOKEN=your_mapbox_token
```

**Important**: URL-encode special characters in passwords:
- `@` → `%40`
- `+` → `%2B`
- `#` → `%23`

### Frontend Environment Variables

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
# For production: https://api.ibhoom.in
```

---

## 📚 API Documentation

### Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.ibhoom.in`

### Interactive API Docs

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Authentication

All protected endpoints require JWT token in Authorization header:

```http
Authorization: Bearer <access_token>
```

### Main Endpoints

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh access token

#### Admin Endpoints
- `GET /api/v1/admin/dashboard/stats` - Dashboard statistics
- `GET /api/v1/admin/users` - List all users
- `PUT /api/v1/admin/users/{id}/status` - Update user status
- `GET /api/v1/admin/sellers` - List all sellers
- `PUT /api/v1/admin/sellers/{id}/approve` - Approve seller
- `GET /api/v1/admin/products` - List all products
- `PUT /api/v1/admin/products/{id}/approve` - Approve product
- `GET /api/v1/admin/categories` - List categories
- `POST /api/v1/admin/categories` - Create category
- `GET /api/v1/admin/attributes` - List attributes
- `POST /api/v1/admin/attributes` - Create attribute
- `GET /api/v1/admin/orders` - List all orders
- `GET /api/v1/admin/commissions` - Commission settings

#### Seller Endpoints
- `GET /api/v1/seller/dashboard/stats` - Seller dashboard
- `GET /api/v1/seller/products` - List seller's products
- `POST /api/v1/seller/products` - Create product
- `PUT /api/v1/seller/products/{id}` - Update product
- `DELETE /api/v1/seller/products/{id}` - Delete product
- `GET /api/v1/seller/orders` - List seller's orders
- `PUT /api/v1/seller/orders/{id}/status` - Update order status
- `GET /api/v1/seller/profile` - Get seller profile
- `PUT /api/v1/seller/profile` - Update seller profile

#### Customer Endpoints
- `GET /api/v1/customer/products` - Browse products (with location filtering)
- `GET /api/v1/customer/products/{id}` - Get product details
- `GET /api/v1/customer/categories` - List categories
- `GET /api/v1/customer/banners` - Get active banners
- `POST /api/v1/customer/cart` - Add to cart
- `GET /api/v1/customer/cart` - Get cart items
- `DELETE /api/v1/customer/cart/{id}` - Remove from cart
- `POST /api/v1/customer/wishlist` - Add to wishlist
- `GET /api/v1/customer/wishlist` - Get wishlist
- `POST /api/v1/customer/orders` - Place order
- `GET /api/v1/customer/orders` - Get customer orders
- `GET /api/v1/customer/orders/{id}` - Get order details
- `POST /api/v1/customer/reviews` - Create review

### Location-Based Filtering

Customer product endpoints support location filtering:

```http
GET /api/v1/customer/products?latitude=8.5241&longitude=76.9366&radius_km=25
GET /api/v1/customer/products?city=Thiruvananthapuram&radius_km=50
```

---

## 📁 Project Structure

```
ibhoom/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── admin/          # Admin endpoints
│   │   │       ├── seller/         # Seller endpoints
│   │   │       ├── customer/       # Customer endpoints
│   │   │       └── auth.py         # Authentication
│   │   ├── core/
│   │   │   ├── config.py           # Configuration
│   │   │   ├── database.py         # Database setup
│   │   │   ├── dependencies.py     # Auth dependencies
│   │   │   └── security.py         # JWT & password hashing
│   │   ├── models/                 # SQLAlchemy models
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── services/               # Business logic
│   │   ├── utils/                  # Utility functions
│   │   └── main.py                 # FastAPI app
│   ├── migrations/                 # Alembic migrations
│   ├── requirements.txt            # Python dependencies
│   ├── alembic.ini                 # Alembic config
│   └── .env                        # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/             # React components
│   │   │   ├── Auth/               # Auth components
│   │   │   ├── Layout/             # Layout components
│   │   │   └── Notifications/      # Notification components
│   │   ├── pages/                  # Page components
│   │   │   ├── Admin/              # Admin pages
│   │   │   ├── Seller/             # Seller pages
│   │   │   └── Customer/           # Customer pages
│   │   ├── contexts/               # React contexts
│   │   ├── lib/                    # API client, Firebase
│   │   ├── types/                  # TypeScript types
│   │   └── App.tsx                 # Main app component
│   ├── public/                     # Static assets
│   ├── package.json                # Node dependencies
│   └── .env                        # Environment variables
├── deployment/                     # Deployment files
│   ├── nginx/                      # Nginx configs
│   ├── systemd/                    # Systemd services
│   └── deploy.sh                   # Deployment script
├── HOSTING_DOCUMENTATION.md        # Hosting guide
├── HOSTINGER_VPS_DEPLOYMENT.md     # VPS deployment
├── CLOUDFLARE_DOMAIN_SETUP.md      # Cloudflare setup
├── CREDENTIALS_TEMPLATE.md         # Credentials template
└── README.md                       # This file
```

---

## 🗄️ Database Schema

### Core Tables

- **users** - User accounts (admin, seller, customer)
- **sellers** - Seller profiles with location data
- **categories** - Hierarchical product categories
- **attributes** - Product attributes (color, size, etc.)
- **products** - Product information
- **product_variants** - Product variants with pricing
- **product_images** - Product images
- **orders** - Customer orders
- **order_items** - Individual items in orders
- **product_reviews** - Customer reviews and ratings
- **cart** - Shopping cart items
- **wishlist** - Wishlist items
- **commission_settings** - Commission configuration
- **notifications** - User notifications
- **banners** - Promotional banners
- **pincode_cache** - Cached geocoded pincodes

### Key Relationships

- Users → Sellers (one-to-one)
- Categories → Products (many-to-one, hierarchical)
- Products → ProductVariants (one-to-many)
- Products → ProductImages (one-to-many)
- Orders → OrderItems (one-to-many)
- Products → Reviews (one-to-many)

---

## 💻 Development Guide

### Running in Development

#### Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm run dev
```

### Database Migrations

```bash
cd backend
source venv/bin/activate

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Code Style

#### Backend (Python)

- Follow PEP 8 style guide
- Use type hints
- Document functions with docstrings

#### Frontend (TypeScript)

- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 🚀 Deployment

### Production Deployment

For complete deployment instructions, see:

- **[HOSTING_DOCUMENTATION.md](HOSTING_DOCUMENTATION.md)** - Complete hosting guide
- **[HOSTINGER_VPS_DEPLOYMENT.md](HOSTINGER_VPS_DEPLOYMENT.md)** - Step-by-step VPS deployment
- **[CLOUDFLARE_DOMAIN_SETUP.md](CLOUDFLARE_DOMAIN_SETUP.md)** - Domain and DNS setup

### Quick Deployment Checklist

- [ ] VPS provisioned and configured
- [ ] Domain registered and DNS configured
- [ ] Cloudflare setup complete
- [ ] Database created and migrations run
- [ ] Environment variables configured
- [ ] Backend service running
- [ ] Frontend built and deployed
- [ ] Nginx configured
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Backups configured

### Current Production Setup

- **Frontend**: `https://ibhoom.in`
- **Backend API**: `https://api.ibhoom.in`
- **VPS**: Hostinger KVM2 (3GB RAM, 50GB storage)
- **Database**: PostgreSQL
- **CDN**: Cloudflare

---

## 🔒 Security

### Security Features

- **JWT Authentication** with access and refresh tokens
- **Password Hashing** using Argon2 (with bcrypt fallback)
- **Role-based Access Control** (RBAC)
- **CORS Protection** configured
- **Input Validation** using Pydantic schemas
- **SQL Injection Protection** via SQLAlchemy ORM
- **HTTPS/SSL** via Cloudflare
- **Environment Variables** for sensitive data
- **File Upload Validation** (size, type restrictions)

### Security Best Practices

- Never commit `.env` files
- Use strong, random JWT secrets
- Keep dependencies updated
- Regular security audits
- Monitor logs for suspicious activity
- Use HTTPS in production
- Implement rate limiting
- Regular backups

---

## 📖 Additional Documentation

- **[HOSTING_DOCUMENTATION.md](HOSTING_DOCUMENTATION.md)** - Complete hosting guide
- **[CREDENTIALS_TEMPLATE.md](CREDENTIALS_TEMPLATE.md)** - Credentials management
- **[JWT_AUTHENTICATION_GUIDE.md](JWT_AUTHENTICATION_GUIDE.md)** - JWT implementation
- **[LOCATION_BASED_FILTERING_GUIDE.md](LOCATION_BASED_FILTERING_GUIDE.md)** - Location features
- **[VARIANT_SYSTEM_GUIDE.md](VARIANT_SYSTEM_GUIDE.md)** - Product variant system
- **[BACKEND_README.md](BACKEND_README.md)** - Backend-specific documentation

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Commit your changes** (`git commit -m 'Add some amazing feature'`)
5. **Push to the branch** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request**

### Contribution Guidelines

- Follow the existing code style
- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

### Getting Help

- **Documentation**: Check the guides in the repository
- **Issues**: [GitHub Issues](https://github.com/naveensheejachacko/ibhoom/issues)
- **API Docs**: Visit `/docs` endpoint when backend is running

### Common Issues

1. **Database connection errors**: Check DATABASE_URL in .env
2. **CORS errors**: Verify BACKEND_CORS_ORIGINS includes your frontend URL
3. **Migration errors**: Run `alembic upgrade head`
4. **Build errors**: Check Node.js version (18+ required)

---

## 🎯 Roadmap

### Planned Features

- [ ] Payment gateway integration (Razorpay, Stripe)
- [ ] Real-time chat between sellers and customers
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native/Flutter)
- [ ] Multi-language support
- [ ] Advanced search with filters
- [ ] Inventory management system
- [ ] Shipping integration
- [ ] Email notifications
- [ ] SMS notifications
- [ ] Social media login
- [ ] Product recommendations

---

## 📊 Project Status

- ✅ **Core Features**: Complete
- ✅ **Admin Panel**: Complete
- ✅ **Seller Panel**: Complete
- ✅ **Customer Features**: Complete
- ✅ **Location Filtering**: Complete
- ✅ **Variant System**: Complete
- ✅ **Production Deployment**: Complete
- 🚧 **Payment Integration**: In Progress
- 🚧 **Mobile App**: Planned

---

## 👥 Team

- **Repository**: [naveensheejachacko/ibhoom](https://github.com/naveensheejachacko/ibhoom)

---

## 🙏 Acknowledgments

- FastAPI community
- React community
- All contributors and users

---

**Made with ❤️ by the ibhoom team**

---

**Last Updated**: November 16, 2025  
**Version**: 1.0.0
