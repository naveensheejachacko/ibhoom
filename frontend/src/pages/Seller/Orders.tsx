import React, { useState, useEffect } from 'react';
import { ShoppingCart, Search, Eye, Package, CheckCircle, X, Clock } from 'lucide-react';
import { sellerApi } from '../../lib/api';
import { useToast } from '../../components/Toast';
import type { OrderListResponse } from '../../types/api';

const Orders: React.FC = () => {
  const toast = useToast();
  const [orders, setOrders] = useState<OrderListResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedOrder, setSelectedOrder] = useState<OrderListResponse | null>(null);
  const [showOrderModal, setShowOrderModal] = useState(false);

  useEffect(() => {
    fetchOrders();
  }, [statusFilter]);

  const fetchOrders = async () => {
    try {
      setIsLoading(true);
      const params: any = {};
      if (statusFilter) params.status = statusFilter;
      const data = await sellerApi.getOrders(params);
      // Handle paginated response
      if (data.items) {
        setOrders(data.items);
      } else {
        // Fallback for non-paginated response
        setOrders(Array.isArray(data) ? data : []);
      }
    } catch (error: any) {
      console.error('Error fetching orders:', error);
      toast.show('Failed to fetch orders', { type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleStatusUpdate = async (orderId: string, newStatus: string, sellerNotes?: string) => {
    try {
      await sellerApi.updateOrderStatus(orderId, { 
        status: newStatus,
        seller_notes: sellerNotes 
      });
      toast.show('Order status updated successfully', { type: 'success' });
      fetchOrders();
      setShowOrderModal(false);
    } catch (error: any) {
      console.error('Error updating order status:', error);
      toast.show(error.response?.data?.detail || 'Failed to update order status', { type: 'error' });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'ready for dispatch': return 'bg-purple-100 text-purple-800';
      case 'dispatched': return 'bg-indigo-100 text-indigo-800';
      case 'delivered': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'processing': return <Package className="w-4 h-4" />;
      case 'ready for dispatch': return <Package className="w-4 h-4" />;
      case 'dispatched': return <CheckCircle className="w-4 h-4" />;
      case 'delivered': return <CheckCircle className="w-4 h-4" />;
      case 'cancelled': return <X className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const filteredOrders = orders.filter(order => {
    const matchesSearch = order.order_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         order.id.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-secondary-900">My Orders</h1>
        <p className="text-secondary-600">Manage orders for your products</p>
      </div>

      {/* Filters */}
      <div className="card p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Order number..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="processing">Processing</option>
              <option value="ready for dispatch">Ready for Dispatch</option>
              <option value="dispatched">Dispatched</option>
              <option value="delivered">Delivered</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={fetchOrders}
              className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Orders Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-secondary-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Order</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Items</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-secondary-200">
              {filteredOrders.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-secondary-500">
                    No orders found
                  </td>
                </tr>
              ) : (
                filteredOrders.map((order) => (
                  <tr key={order.id} className="hover:bg-secondary-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-secondary-900">{order.order_number}</div>
                      <div className="text-sm text-secondary-500">ID: {order.id.slice(0, 8)}...</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-secondary-900">{order.total_items} item(s)</div>
                      {order.items && order.items.length > 0 && (
                        <div className="text-xs text-secondary-500 mt-1">
                          {order.items[0].product_name}
                          {order.items.length > 1 && ` +${order.items.length - 1} more`}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-secondary-900">
                        ₹{order.total_customer_amount.toFixed(2)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}>
                        {getStatusIcon(order.status)}
                        {order.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">
                      {new Date(order.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => {
                          setSelectedOrder(order);
                          setShowOrderModal(true);
                        }}
                        className="text-primary-600 hover:text-primary-900 flex items-center gap-1"
                      >
                        <Eye className="w-4 h-4" />
                        View
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Order Detail Modal */}
      {showOrderModal && selectedOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-secondary-200">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-bold text-secondary-900">Order Details</h2>
                  <p className="text-sm text-secondary-500">{selectedOrder.order_number}</p>
                </div>
                <button
                  onClick={() => setShowOrderModal(false)}
                  className="text-secondary-400 hover:text-secondary-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            <div className="p-6 space-y-6">
              {/* Order Items */}
              <div>
                <h3 className="text-lg font-semibold text-secondary-900 mb-4">Order Items</h3>
                <div className="space-y-4">
                  {selectedOrder.items.map((item) => (
                    <div key={item.id} className="flex items-center gap-4 p-4 bg-secondary-50 rounded-lg">
                      {item.product_image && (
                        <img
                          src={item.product_image}
                          alt={item.product_name}
                          className="w-16 h-16 object-cover rounded"
                        />
                      )}
                      <div className="flex-1">
                        <h4 className="font-medium text-secondary-900">{item.product_name}</h4>
                        {item.variant_name && (
                          <p className="text-sm text-secondary-500">Variant: {item.variant_name}</p>
                        )}
                        <p className="text-sm text-secondary-600">Qty: {item.quantity} × ₹{item.customer_unit_price.toFixed(2)}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-secondary-900">₹{item.total_customer_amount.toFixed(2)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Status Update */}
              <div>
                <h3 className="text-lg font-semibold text-secondary-900 mb-4">Update Status</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {selectedOrder.status === 'pending' ? (
                    <>
                      <button
                        onClick={() => handleStatusUpdate(selectedOrder.id, 'processing')}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                      >
                        Accept & Process
                      </button>
                      <button
                        onClick={() => handleStatusUpdate(selectedOrder.id, 'rejected')}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
                      >
                        Reject
                      </button>
                    </>
                  ) : null}
                  {selectedOrder.status === 'processing' ? (
                    <button
                      onClick={() => handleStatusUpdate(selectedOrder.id, 'ready for dispatch')}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm"
                    >
                      Ready for Dispatch
                    </button>
                  ) : null}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Orders;

