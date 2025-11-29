import React, { useState, useEffect } from 'react';
import { Search, Eye, Package, Truck, CheckCircle, X, XCircle, Clock, FileText, Download, RefreshCw, RotateCcw } from 'lucide-react';
import { adminApi } from '../../lib/api';
import { useToast } from '../../components/Toast';
import Pagination from '../../components/Pagination';
import type { OrderListResponse } from '../../types/api';

const Orders: React.FC = () => {
  const toast = useToast();
  const [orders, setOrders] = useState<OrderListResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeSearchTerm, setActiveSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [paymentFilter, setPaymentFilter] = useState('');
  const [selectedOrder, setSelectedOrder] = useState<OrderListResponse | null>(null);
  const [showOrderModal, setShowOrderModal] = useState(false);
  const [showRefundModal, setShowRefundModal] = useState(false);
  const [refundAmount, setRefundAmount] = useState<string>('');
  const [refundNotes, setRefundNotes] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPerPage = 20;

  useEffect(() => {
    fetchOrders();
  }, [statusFilter, paymentFilter, currentPage, activeSearchTerm]);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [statusFilter, paymentFilter, activeSearchTerm]);

  const fetchOrders = async () => {
    try {
      setIsLoading(true);
      const params: any = {
        page: currentPage,
        limit: itemsPerPage,
      };
      if (statusFilter) params.status = statusFilter;
      if (paymentFilter) params.payment_status = paymentFilter;
      if (activeSearchTerm) params.search = activeSearchTerm;
      const data = await adminApi.getOrders(params);
      // Handle paginated response
      if (data.items) {
        setOrders(data.items);
        setTotalPages(data.pages);
        setTotalItems(data.total);
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

  const handleStatusUpdate = async (orderId: string, newStatus: string) => {
    try {
      await adminApi.updateOrderStatus(orderId, { status: newStatus });
      toast.show('Order status updated successfully', { type: 'success' });
      fetchOrders();
      setShowOrderModal(false);
    } catch (error: any) {
      console.error('Error updating order status:', error);
      toast.show(error.response?.data?.detail || 'Failed to update order status', { type: 'error' });
    }
  };

  const handleDownloadInvoice = async (orderId: string, orderNumber: string) => {
    try {
      const blob = await adminApi.downloadInvoice(orderId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `invoice_${orderNumber}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.show('Invoice downloaded successfully', { type: 'success' });
    } catch (error: any) {
      console.error('Error downloading invoice:', error);
      if (error.response?.status === 400) {
        toast.show('Invoice can only be generated for delivered orders', { type: 'error' });
      } else {
        toast.show('Failed to download invoice', { type: 'error' });
      }
    }
  };

  const handleViewInvoice = async (orderId: string) => {
    try {
      const blob = await adminApi.downloadInvoice(orderId);
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
      toast.show('Invoice opened in new tab', { type: 'success' });
    } catch (error: any) {
      console.error('Error viewing invoice:', error);
      if (error.response?.status === 400) {
        toast.show('Invoice can only be generated for delivered orders', { type: 'error' });
      } else {
        toast.show('Failed to view invoice', { type: 'error' });
      }
    }
  };

  const handleReturnAction = async (orderId: string, status: string, notes?: string) => {
    try {
      await adminApi.handleReturn(orderId, { status, admin_notes: notes });
      toast.show(`Return ${status} successfully`, { type: 'success' });
      fetchOrders();
      setShowOrderModal(false);
    } catch (error: any) {
      console.error('Error handling return:', error);
      toast.show(error.response?.data?.detail || 'Failed to handle return', { type: 'error' });
    }
  };

  const handleInitiateRefund = () => {
    if (!selectedOrder) return;
    setRefundAmount(selectedOrder.total_customer_amount.toString());
    setRefundNotes('');
    setShowRefundModal(true);
  };

  const handleProcessRefund = async () => {
    if (!selectedOrder || !refundAmount) {
      toast.show('Please enter refund amount', { type: 'error' });
      return;
    }

    try {
      await adminApi.processRefund(selectedOrder.id, {
        refund_amount: parseFloat(refundAmount),
        refund_notes: refundNotes
      });
      toast.show('Refund initiated successfully', { type: 'success' });
      setShowRefundModal(false);
      setShowOrderModal(false);
      fetchOrders();
    } catch (error: any) {
      console.error('Error processing refund:', error);
      toast.show(error.response?.data?.detail || 'Failed to process refund', { type: 'error' });
    }
  };

  const handleCompleteRefund = async (orderId: string, notes?: string) => {
    try {
      await adminApi.completeRefund(orderId, { refund_notes: notes });
      toast.show('Refund marked as completed', { type: 'success' });
      fetchOrders();
      setShowOrderModal(false);
    } catch (error: any) {
      console.error('Error completing refund:', error);
      toast.show(error.response?.data?.detail || 'Failed to complete refund', { type: 'error' });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING': return 'bg-yellow-100 text-yellow-800';
      case 'REJECTED': return 'bg-red-100 text-red-800';
      case 'PROCESSING': return 'bg-blue-100 text-blue-800';
      case 'READY_FOR_DISPATCH': return 'bg-purple-100 text-purple-800';
      case 'DISPATCHED': return 'bg-indigo-100 text-indigo-800';
      case 'DELIVERED': return 'bg-green-100 text-green-800';
      case 'CANCELLED': return 'bg-red-100 text-red-800';
      case 'RETURN_REQUESTED': return 'bg-orange-100 text-orange-800';
      case 'RETURN_APPROVED': return 'bg-teal-100 text-teal-800';
      case 'RETURN_REJECTED': return 'bg-red-100 text-red-800';
      case 'RETURN_PICKED_UP': return 'bg-purple-100 text-purple-800';
      case 'RETURN_RECEIVED': return 'bg-blue-100 text-blue-800';
      case 'REFUND_PROCESSING': return 'bg-yellow-100 text-yellow-800';
      case 'REFUND_COMPLETED': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'PENDING': return <Clock className="w-4 h-4" />;
      case 'REJECTED': return <XCircle className="w-4 h-4" />;
      case 'PROCESSING': return <Package className="w-4 h-4" />;
      case 'READY_FOR_DISPATCH': return <Package className="w-4 h-4" />;
      case 'DISPATCHED': return <Truck className="w-4 h-4" />;
      case 'DELIVERED': return <CheckCircle className="w-4 h-4" />;
      case 'CANCELLED': return <XCircle className="w-4 h-4" />;
      case 'RETURN_REQUESTED': return <RotateCcw className="w-4 h-4" />;
      case 'RETURN_APPROVED': return <CheckCircle className="w-4 h-4" />;
      case 'RETURN_REJECTED': return <XCircle className="w-4 h-4" />;
      case 'RETURN_PICKED_UP': return <Package className="w-4 h-4" />;
      case 'RETURN_RECEIVED': return <CheckCircle className="w-4 h-4" />;
      case 'REFUND_PROCESSING': return <Clock className="w-4 h-4" />;
      case 'REFUND_COMPLETED': return <CheckCircle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const formatStatus = (status: string) => {
    return status.toLowerCase().replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getPaymentStatusLabel = (paymentStatus: string) => {
    switch (paymentStatus) {
      case 'cod_pending': return 'Cash on Delivery';
      case 'cod_collected': return 'Payment Collected';
      case 'paid': return 'Paid Online';
      case 'refunded': return 'Refunded';
      default: return paymentStatus.replace('_', ' ');
    }
  };

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [statusFilter, paymentFilter]);

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
        <h1 className="text-2xl font-bold text-secondary-900">Order Management</h1>
        <p className="text-secondary-600">Process and manage customer orders</p>
      </div>

      {/* Filters */}
      <div className="card p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Order number..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    setActiveSearchTerm(searchTerm);
                  }
                }}
                className="w-full pl-10 pr-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              {searchTerm && (
                <button
                  onClick={() => {
                    setSearchTerm('');
                    setActiveSearchTerm('');
                  }}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-secondary-400 hover:text-secondary-600"
                  title="Clear search"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
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
              <option value="return requested">Return Requested</option>
              <option value="return approved">Return Approved</option>
              <option value="return rejected">Return Rejected</option>
              <option value="return picked up">Return Picked Up</option>
              <option value="return received">Return Received</option>
              <option value="refund processing">Refund Processing</option>
              <option value="refund completed">Refund Completed</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">Payment</label>
            <select
              value={paymentFilter}
              onChange={(e) => setPaymentFilter(e.target.value)}
              className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Payments</option>
              <option value="cod_pending">Cash on Delivery</option>
              <option value="cod_collected">Payment Collected</option>
              <option value="paid">Paid Online</option>
              <option value="refunded">Refunded</option>
            </select>
          </div>
          <div className="flex items-end gap-2">
            <button
              onClick={() => setActiveSearchTerm(searchTerm)}
              className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
            >
              <Search className="w-4 h-4" />
              Search
            </button>
            <button
              onClick={fetchOrders}
              className="px-4 py-2 bg-secondary-600 text-white rounded-lg hover:bg-secondary-700 transition-colors"
              title="Refresh"
            >
              <RefreshCw className="w-4 h-4" />
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
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Commission</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Payable Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Payment</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-secondary-200">
              {orders.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-secondary-500">
                    No orders found
                  </td>
                </tr>
              ) : (
                orders.map((order) => (
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
                        ₹{order.grand_total_amount?.toFixed(2) || order.total_customer_amount.toFixed(2)}
                      </div>
                      {order.total_tax_amount && (
                        <div className="text-xs text-secondary-500">
                          Tax: ₹{order.total_tax_amount.toFixed(2)}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-secondary-900">
                        ₹{order.commission_amount?.toFixed(2) || '0.00'}
                      </div>
                      <div className="text-xs text-secondary-500">Commission</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-primary-600">
                        ₹{order.payable_amount?.toFixed(2) || '0.00'}
                      </div>
                      <div className="text-xs text-secondary-500">To Seller</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}>
                        {getStatusIcon(order.status)}
                        {formatStatus(order.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        order.payment_status === 'paid' ? 'bg-green-100 text-green-800' :
                        order.payment_status === 'cod_collected' ? 'bg-blue-100 text-blue-800' :
                        order.payment_status === 'cod_pending' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {getPaymentStatusLabel(order.payment_status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">
                      {new Date(order.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center gap-2">
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
                        {order.status === 'DELIVERED' && (
                          <button
                            onClick={() => handleDownloadInvoice(order.id, order.order_number)}
                            className="text-green-600 hover:text-green-900 flex items-center gap-1"
                            title="Download Invoice"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          totalItems={totalItems}
          itemsPerPage={itemsPerPage}
          onPageChange={(page) => {
            setCurrentPage(page);
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }}
        />
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
                  {(selectedOrder.customer_name || selectedOrder.phone) && (
                    <p className="text-sm text-secondary-500 mt-1">
                      {selectedOrder.customer_name && <span>{selectedOrder.customer_name}</span>}
                      {selectedOrder.customer_name && selectedOrder.phone && <span> • </span>}
                      {selectedOrder.phone && <span>{selectedOrder.phone}</span>}
                    </p>
                  )}
                  {selectedOrder.delivery_address && (
                    <p className="text-xs text-secondary-500 mt-1">
                      {selectedOrder.delivery_address}
                      {selectedOrder.delivery_city && `, ${selectedOrder.delivery_city}`}
                      {selectedOrder.delivery_state && `, ${selectedOrder.delivery_state}`}
                      {selectedOrder.delivery_pincode && ` - ${selectedOrder.delivery_pincode}`}
                    </p>
                  )}
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
                        {item.seller_name && (
                          <p className="text-sm text-secondary-500">Seller: {item.seller_name}</p>
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

              {/* Order Summary */}
              <div className="border-t border-secondary-200 pt-4">
                <h3 className="text-lg font-semibold text-secondary-900 mb-4">Order Summary</h3>
                <div className="bg-secondary-50 rounded-lg p-4 space-y-2">
                  {(selectedOrder.customer_name || selectedOrder.phone) && (
                    <div className="flex justify-between text-sm pb-2 border-b border-secondary-200">
                      <span className="text-secondary-600">Customer:</span>
                      <span className="font-medium text-secondary-900">
                        {selectedOrder.customer_name || 'Customer'}
                        {selectedOrder.phone && ` • ${selectedOrder.phone}`}
                      </span>
                    </div>
                  )}
                  <div className="flex justify-between text-sm">
                    <span className="text-secondary-600">Subtotal:</span>
                    <span className="font-medium">₹{selectedOrder.total_customer_amount.toFixed(2)}</span>
                  </div>
                  {selectedOrder.total_tax_amount && (
                    <div className="flex justify-between text-sm">
                      <span className="text-secondary-600">Tax:</span>
                      <span className="font-medium">₹{selectedOrder.total_tax_amount.toFixed(2)}</span>
                    </div>
                  )}
                  {selectedOrder.commission_amount !== undefined && (
                    <div className="flex justify-between text-sm">
                      <span className="text-secondary-600">Commission (Admin):</span>
                      <span className="font-medium">₹{selectedOrder.commission_amount.toFixed(2)}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-sm font-semibold pt-2 border-t border-secondary-200">
                    <span className="text-secondary-900">Grand Total:</span>
                    <span className="text-secondary-900">₹{selectedOrder.grand_total_amount?.toFixed(2) || selectedOrder.total_customer_amount.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm pt-2 border-t border-secondary-200">
                    <span className="text-secondary-600">Payable to Seller:</span>
                    <span className="font-medium text-primary-600">₹{selectedOrder.payable_amount?.toFixed(2) || '0.00'}</span>
                  </div>
                </div>
              </div>

              {/* Return & Refund Information */}
              {(selectedOrder.status.includes('return') || selectedOrder.status.includes('refund')) && (
                <div className="border-t border-secondary-200 pt-4">
                  <h3 className="text-lg font-semibold text-secondary-900 mb-4">Return & Refund Information</h3>
                  <div className="bg-orange-50 rounded-lg p-4 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-secondary-600">Return Status:</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedOrder.status)}`}>
                        {formatStatus(selectedOrder.status)}
                      </span>
                    </div>
                    {selectedOrder.return_reason && (
                      <div className="flex flex-col text-sm">
                        <span className="text-secondary-600 mb-1">Return Reason:</span>
                        <span className="font-medium text-secondary-900">{selectedOrder.return_reason}</span>
                      </div>
                    )}
                    {selectedOrder.return_requested_at && (
                      <div className="flex justify-between text-sm">
                        <span className="text-secondary-600">Requested At:</span>
                        <span className="font-medium">{new Date(selectedOrder.return_requested_at).toLocaleString()}</span>
                      </div>
                    )}
                    {selectedOrder.refund_amount && (
                      <div className="flex justify-between text-sm">
                        <span className="text-secondary-600">Refund Amount:</span>
                        <span className="font-medium text-primary-600">₹{selectedOrder.refund_amount.toFixed(2)}</span>
                      </div>
                    )}
                    {selectedOrder.refund_date && (
                      <div className="flex justify-between text-sm">
                        <span className="text-secondary-600">Refund Date:</span>
                        <span className="font-medium">{new Date(selectedOrder.refund_date).toLocaleString()}</span>
                      </div>
                    )}
                    {selectedOrder.refund_notes && (
                      <div className="flex flex-col text-sm">
                        <span className="text-secondary-600 mb-1">Refund Notes:</span>
                        <span className="font-medium text-secondary-900">{selectedOrder.refund_notes}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Invoice Actions */}
              {selectedOrder.status === 'DELIVERED' && (
                <div>
                  <h3 className="text-lg font-semibold text-secondary-900 mb-4">Invoice</h3>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleViewInvoice(selectedOrder.id)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                    >
                      <FileText className="w-4 h-4" />
                      View Invoice
                    </button>
                    <button
                      onClick={() => handleDownloadInvoice(selectedOrder.id, selectedOrder.order_number)}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                    >
                      <Download className="w-4 h-4" />
                      Download Invoice
                    </button>
                  </div>
                </div>
              )}

              {/* Status Update */}
              <div>
                <h3 className="text-lg font-semibold text-secondary-900 mb-4">Update Status</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {selectedOrder.status === 'PENDING' || selectedOrder.status === 'PROCESSING' ? (
                    <button
                      onClick={() => handleStatusUpdate(selectedOrder.id, 'READY_FOR_DISPATCH')}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm"
                    >
                      Ready for Dispatch
                    </button>
                  ) : null}
                  {selectedOrder.status === 'READY_FOR_DISPATCH' ? (
                    <button
                      onClick={() => handleStatusUpdate(selectedOrder.id, 'DISPATCHED')}
                      className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm"
                    >
                      Dispatch
                    </button>
                  ) : null}
                  {(selectedOrder.status === 'READY_FOR_DISPATCH' || selectedOrder.status === 'DISPATCHED') ? (
                    <button
                      onClick={() => handleStatusUpdate(selectedOrder.id, 'DELIVERED')}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                    >
                      Mark Delivered
                    </button>
                  ) : null}
                  {selectedOrder.status === 'RETURN_REQUESTED' ? (
                    <>
                      <button
                        onClick={() => handleReturnAction(selectedOrder.id, 'RETURN_APPROVED')}
                        className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 text-sm"
                      >
                        Approve Return
                      </button>
                      <button
                        onClick={() => handleReturnAction(selectedOrder.id, 'RETURN_REJECTED')}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
                      >
                        Reject Return
                      </button>
                    </>
                  ) : null}
                  {selectedOrder.status === 'RETURN_APPROVED' ? (
                    <button
                      onClick={() => handleReturnAction(selectedOrder.id, 'RETURN_PICKED_UP')}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm"
                    >
                      Mark as Picked Up
                    </button>
                  ) : null}
                  {selectedOrder.status === 'RETURN_PICKED_UP' ? (
                    <button
                      onClick={() => handleReturnAction(selectedOrder.id, 'RETURN_RECEIVED')}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                    >
                      Mark as Received
                    </button>
                  ) : null}
                  {selectedOrder.status === 'RETURN_RECEIVED' ? (
                    <button
                      onClick={handleInitiateRefund}
                      className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 text-sm"
                    >
                      Process Refund
                    </button>
                  ) : null}
                  {selectedOrder.status === 'REFUND_PROCESSING' ? (
                    <button
                      onClick={() => handleCompleteRefund(selectedOrder.id)}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                    >
                      Mark Refund Completed
                    </button>
                  ) : null}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Refund Modal */}
      {showRefundModal && selectedOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="p-6 border-b border-secondary-200">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-bold text-secondary-900">Process Refund</h2>
                  <p className="text-sm text-secondary-500">Order: {selectedOrder.order_number}</p>
                </div>
                <button
                  onClick={() => {
                    setShowRefundModal(false);
                    setRefundAmount('');
                    setRefundNotes('');
                  }}
                  className="text-secondary-400 hover:text-secondary-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Refund Amount <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-500">
                    ₹
                  </span>
                  <input
                    type="number"
                    value={refundAmount}
                    onChange={(e) => setRefundAmount(e.target.value)}
                    placeholder="Enter refund amount"
                    step="0.01"
                    min="0"
                    max={selectedOrder.total_customer_amount}
                    className="w-full pl-8 pr-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <p className="text-xs text-secondary-500 mt-1">
                  Order Total: ₹{selectedOrder.total_customer_amount.toFixed(2)}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Refund Notes (Optional)
                </label>
                <textarea
                  value={refundNotes}
                  onChange={(e) => setRefundNotes(e.target.value)}
                  placeholder="Add notes about the refund..."
                  rows={3}
                  className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                />
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setShowRefundModal(false);
                    setRefundAmount('');
                    setRefundNotes('');
                  }}
                  className="flex-1 px-4 py-2 border border-secondary-300 text-secondary-700 rounded-lg hover:bg-secondary-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleProcessRefund}
                  disabled={!refundAmount || parseFloat(refundAmount) <= 0}
                  className="flex-1 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors disabled:bg-secondary-300 disabled:cursor-not-allowed"
                >
                  Process Refund
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Orders;
