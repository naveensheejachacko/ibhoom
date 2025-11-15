# Notification Flow: When Customer Places an Order

This document explains step-by-step how notifications work when a customer places an order.

## 📋 Complete Flow Diagram

```
Customer Places Order
        ↓
[1] Order Created & Committed to Database ✅
        ↓
[2] Cart Cleared (if items were in cart)
        ↓
[3] Notification Service Called
        ↓
    ┌─────────────────────────────────────┐
    │  notify_order_placed()              │
    └─────────────────────────────────────┘
        ↓
    ┌─────────────────────────────────────┐
    │  [A] Admin Notification              │
    │  - Create DB notification            │
    │  - Send Firebase push (if enabled)  │
    └─────────────────────────────────────┘
        ↓
    ┌─────────────────────────────────────┐
    │  [B] Group Items by Seller           │
    │  - Loop through order items          │
    │  - Group by seller_user_id           │
    └─────────────────────────────────────┘
        ↓
    ┌─────────────────────────────────────┐
    │  [C] Seller Notifications           │
    │  - For each seller:                  │
    │    • Create DB notification          │
    │    • Send Firebase push (if enabled) │
    └─────────────────────────────────────┘
        ↓
[4] Order Response Returned to Customer
```

---

## 🔄 Step-by-Step Process

### **Step 1: Customer Places Order**

**Location**: `POST /api/v1/customer/orders/`

**What happens**:
1. Customer submits order with items
2. Order is validated (stock, location, etc.)
3. Order is created in database
4. Stock quantities are updated
5. **Order is committed** (`db.commit()`)

**Code**: `backend/app/api/v1/customer/orders.py` → `create_order()`
```python
db_order = order_service.create_order(db, order, current_user.id)
```

---

### **Step 2: Notification Trigger**

**Location**: `backend/app/services/order_service.py` (line 213-227)

**What happens**:
After order is successfully committed, the system calls:
```python
NotificationService.notify_order_placed(db, db_order)
```

**Important**: This happens **after** the order is committed, so:
- ✅ Order is already saved
- ✅ If notifications fail, order still exists
- ✅ Errors in notifications don't break order creation

---

### **Step 3: Admin Notification**

**Location**: `backend/app/services/notification_service.py` → `notify_admin_new_order()`

**What happens**:

1. **Find Admin User**:
   ```python
   admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
   ```

2. **Create Database Notification**:
   ```python
   Notification(
       user_id=admin.id,
       notification_type=NotificationType.NEW_ORDER,
       title="New Order: ORD-1234567890-ABCDEFGH",
       message="New order received from John Customer. Total: ₹1,500.00 (3 items)",
       order_id=order.id,
       is_read=False
   )
   ```
   - Saved to `notifications` table
   - Visible in admin app via `GET /api/v1/admin/notifications`

3. **Send Firebase Push Notification** (if enabled):
   - Queries `fcm_tokens` table for admin's devices
   - Sends push notification to all registered devices
   - Admin sees notification even if app is closed

**Example Notification**:
```json
{
  "id": "notification-uuid",
  "user_id": "admin-user-id",
  "type": "new_order",
  "title": "New Order: ORD-1234567890-ABCDEFGH",
  "message": "New order received from John Customer. Total: ₹1,500.00 (3 items)",
  "order_id": "order-uuid",
  "is_read": false,
  "created_at": "2025-01-11T10:30:00"
}
```

---

### **Step 4: Group Items by Seller**

**Location**: `backend/app/services/notification_service.py` (line 210-228)

**What happens**:

1. **Loop through order items**:
   ```python
   for item in order.items:
       product = db.query(Product).options(
           joinedload(Product.seller).joinedload(Seller.user)
       ).filter(Product.id == item.product_id).first()
   ```

2. **Group by seller**:
   - If order has products from multiple sellers:
     - Seller A: [Item 1, Item 2]
     - Seller B: [Item 3]
   - Each seller gets **one notification** with their products

3. **Store in map**:
   ```python
   seller_items_map[seller_user_id] = [item1, item2, ...]
   ```

**Example**:
```
Order has:
- Product A (from Seller 1)
- Product B (from Seller 1)  
- Product C (from Seller 2)

Result:
- Seller 1 gets notification with Product A + B
- Seller 2 gets notification with Product C
```

---

### **Step 5: Seller Notifications**

**Location**: `backend/app/services/notification_service.py` → `notify_seller_new_order()`

**What happens** (for each seller):

1. **Calculate seller's total**:
   ```python
   seller_total = sum(item.total_seller_amount for item in seller_items)
   # Example: ₹1,200.00
   ```

2. **Create Database Notification**:
   ```python
   Notification(
       user_id=seller_user_id,
       notification_type=NotificationType.NEW_ORDER,
       title="New Order for Your Products: ORD-1234567890-ABCDEFGH",
       message="Your 2 products ordered. You will receive ₹1,200.00. Order: ORD-1234567890-ABCDEFGH",
       order_id=order.id,
       is_read=False
   )
   ```
   - Saved to `notifications` table
   - Visible in seller app via `GET /api/v1/seller/notifications`

3. **Send Firebase Push Notification** (if enabled):
   - Queries `fcm_tokens` table for seller's devices
   - Sends push notification to all registered devices
   - Seller sees notification even if app is closed

**Example Notification**:
```json
{
  "id": "notification-uuid-2",
  "user_id": "seller-user-id",
  "type": "new_order",
  "title": "New Order for Your Products: ORD-1234567890-ABCDEFGH",
  "message": "Your 2 products ordered. You will receive ₹1,200.00. Order: ORD-1234567890-ABCDEFGH",
  "order_id": "order-uuid",
  "is_read": false,
  "created_at": "2025-01-11T10:30:00"
}
```

---

## 📊 Notification Types

### **Database Notifications** (Always Created)
- Stored in `notifications` table
- Persistent - visible in app
- Can be marked as read/unread
- History is maintained

### **Firebase Push Notifications** (Optional)
- Real-time push to devices
- Works even when app is closed
- Requires:
  - Firebase configured (`FIREBASE_ENABLED=true`)
  - User has registered FCM token
  - `fcm_tokens` table exists

---

## 🎯 Who Gets What?

### **Admin Receives**:
- **1 notification** per order
- **Title**: "New Order: {order_number}"
- **Message**: "New order received from {customer_name}. Total: ₹{amount} ({item_count} items)"
- **Contains**: Customer name, total amount, item count

### **Each Seller Receives**:
- **1 notification** per order (if they have products in it)
- **Title**: "New Order for Your Products: {order_number}"
- **Message**: "Your {count} products ordered. You will receive ₹{seller_total}. Order: {order_number}"
- **Contains**: Their products only, their total amount

### **Customer Receives**:
- **No notification** (they placed the order, so they already know)
- They can see their order in their order history

---

## 🔍 Example Scenario

### **Order Details**:
- **Order Number**: `ORD-1763142208-67A424C2`
- **Customer**: John Customer
- **Items**:
  - Product A (from Seller 1) - ₹500
  - Product B (from Seller 1) - ₹300
  - Product C (from Seller 2) - ₹700
- **Total**: ₹1,500

### **Notifications Created**:

#### **1. Admin Notification**:
```json
{
  "title": "New Order: ORD-1763142208-67A424C2",
  "message": "New order received from John Customer. Total: ₹1,500.00 (3 items)",
  "type": "new_order",
  "order_id": "order-uuid"
}
```

#### **2. Seller 1 Notification**:
```json
{
  "title": "New Order for Your Products: ORD-1763142208-67A424C2",
  "message": "Your 2 products ordered. You will receive ₹800.00. Order: ORD-1763142208-67A424C2",
  "type": "new_order",
  "order_id": "order-uuid"
}
```

#### **3. Seller 2 Notification**:
```json
{
  "title": "New Order for Your Products: ORD-1763142208-67A424C2",
  "message": "Your 1 product ordered. You will receive ₹700.00. Order: ORD-1763142208-67A424C2",
  "type": "new_order",
  "order_id": "order-uuid"
}
```

---

## 🛡️ Error Handling

### **If Notification Fails**:
- ✅ Order is **still created** (already committed)
- ⚠️ Error is logged
- ⚠️ Warning message in logs
- ❌ Notification is not created
- ✅ Order response still returned to customer

### **If Firebase Fails**:
- ✅ Database notification is **still created**
- ⚠️ Firebase error is logged
- ⚠️ Warning message in logs
- ✅ Admin/Seller can still see notification in app
- ❌ Push notification not sent

### **Transaction Safety**:
- Order commit happens **before** notifications
- Notification errors don't rollback order
- Each notification is wrapped in try-except
- Errors are collected and logged, not thrown

---

## 📱 How to View Notifications

### **Admin**:
```bash
GET /api/v1/admin/notifications
```

**Response**:
```json
{
  "notifications": [
    {
      "id": "notification-id",
      "title": "New Order: ORD-123...",
      "message": "New order received...",
      "type": "new_order",
      "order_id": "order-id",
      "is_read": false,
      "created_at": "2025-01-11T10:30:00"
    }
  ],
  "total_unread": 5,
  "total_count": 10
}
```

### **Seller**:
```bash
GET /api/v1/seller/notifications
```

**Response**: Same format as admin

### **Mark as Read**:
```bash
PUT /api/v1/admin/notifications/{notification_id}/read
PUT /api/v1/seller/notifications/{notification_id}/read
```

### **Mark All as Read**:
```bash
PUT /api/v1/admin/notifications/mark-all-read
PUT /api/v1/seller/notifications/mark-all-read
```

---

## 🔧 Configuration

### **Enable/Disable Firebase**:
```env
# In backend/.env
FIREBASE_ENABLED=true  # or false
```

- If `false`: Only database notifications (always work)
- If `true`: Database + Firebase push notifications

### **Notification Types**:
Currently supported:
- `NEW_ORDER` - When order is placed
- `ORDER_STATUS_CHANGED` - (Future)
- `PAYMENT_RECEIVED` - (Future)
- `ORDER_CANCELLED` - (Future)
- `PRODUCT_APPROVED` - (Future)
- `PRODUCT_REJECTED` - (Future)

---

## 📝 Summary

**When customer places order**:

1. ✅ Order created and saved
2. ✅ Admin gets 1 notification (all orders)
3. ✅ Each seller gets 1 notification (their products only)
4. ✅ Database notifications always created
5. ✅ Firebase push sent (if enabled and tokens exist)
6. ✅ Errors don't break order creation
7. ✅ Notifications visible in admin/seller apps

**Key Points**:
- Notifications are **non-blocking** (order succeeds even if notifications fail)
- Each seller gets **separate notification** (grouped by their products)
- **Database notifications** are always created (persistent)
- **Firebase push** is optional (requires setup)
- Notifications are **linked to orders** via `order_id`

