"""
Script to generate a sample invoice for testing purposes
Run this script to see what the invoice looks like: python generate_sample_invoice.py
"""
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.invoice import generate_invoice_pdf
from app.models.order import Order, OrderStatus, PaymentStatus, OrderItem
from app.models.user import User, UserRole


def create_sample_order():
    """Create a mock order object for testing"""
    
    # Create mock customer
    customer = type('User', (), {
        'id': 'customer-123',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com'
    })()
    
    # Create mock order
    order = type('Order', (), {
        'id': 'order-123',
        'order_number': 'ORD-2024-001',
        'customer': customer,
        'customer_id': 'customer-123',
        'total_customer_amount': Decimal('1250.00'),
        'total_seller_amount': Decimal('1150.00'),
        'total_commission_amount': Decimal('100.00'),
        'status': OrderStatus.DELIVERED,
        'payment_status': PaymentStatus.COD_COLLECTED,
        'delivery_address': '123 Main Street, ABC Building',
        'delivery_city': 'Kochi',
        'delivery_state': 'Kerala',
        'delivery_pincode': '682001',
        'phone': '+91 9876543210',
        'notes': 'Please deliver between 10 AM - 2 PM',
        'admin_notes': None,
        'seller_notes': None,
        'return_reason': None,
        'return_notes': None,
        'created_at': datetime(2024, 1, 15, 10, 30, 0),
        'updated_at': datetime(2024, 1, 18, 14, 45, 0),
        'items': []
    })()
    
    # Create mock order items
    item1 = type('OrderItem', (), {
        'id': 'item-1',
        'product_name': 'Fresh Organic Tomatoes (1kg)',
        'quantity': 3,
        'customer_unit_price': Decimal('80.00'),
        'total_customer_amount': Decimal('240.00'),
        'seller_unit_price': Decimal('70.00'),
        'total_seller_amount': Decimal('210.00'),
        'commission_unit_rate': Decimal('10.00'),
        'commission_unit_amount': Decimal('10.00'),
        'total_commission_amount': Decimal('30.00')
    })()
    
    item2 = type('OrderItem', (), {
        'id': 'item-2',
        'product_name': 'Premium Basmati Rice (5kg)',
        'quantity': 2,
        'customer_unit_price': Decimal('350.00'),
        'total_customer_amount': Decimal('700.00'),
        'seller_unit_price': Decimal('320.00'),
        'total_seller_amount': Decimal('640.00'),
        'commission_unit_rate': Decimal('30.00'),
        'commission_unit_amount': Decimal('30.00'),
        'total_commission_amount': Decimal('60.00')
    })()
    
    item3 = type('OrderItem', (), {
        'id': 'item-3',
        'product_name': 'Fresh Mangoes (1kg)',
        'quantity': 1,
        'customer_unit_price': Decimal('310.00'),
        'total_customer_amount': Decimal('310.00'),
        'seller_unit_price': Decimal('300.00'),
        'total_seller_amount': Decimal('300.00'),
        'commission_unit_rate': Decimal('10.00'),
        'commission_unit_amount': Decimal('10.00'),
        'total_commission_amount': Decimal('10.00')
    })()
    
    order.items = [item1, item2, item3]
    
    return order


if __name__ == "__main__":
    print("Generating sample invoice...")
    
    # Create sample order
    sample_order = create_sample_order()
    
    # Generate invoice
    try:
        backend_dir = Path(__file__).parent
        invoice_dir = backend_dir / "static" / "invoices"
        invoice_dir.mkdir(parents=True, exist_ok=True)
        
        invoice_buffer = generate_invoice_pdf(sample_order, output_path=invoice_dir)
        
        output_file = invoice_dir / f"invoice_{sample_order.order_number}.pdf"
        
        if output_file.exists():
            print(f"\n✅ Sample invoice generated successfully!")
            print(f"📄 Invoice saved at: {output_file}")
            print(f"\nYou can open it with any PDF viewer to see the invoice format.")
        else:
            print(f"\n⚠️  Invoice buffer created but file may not have been saved.")
            print(f"Buffer size: {len(invoice_buffer.getvalue())} bytes")
            
    except Exception as e:
        print(f"\n❌ Error generating invoice: {str(e)}")
        import traceback
        traceback.print_exc()




