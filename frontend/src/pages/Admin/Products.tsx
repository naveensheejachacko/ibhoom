import React, { useState, useEffect } from 'react';
import { Package, Eye, Check, X, Search, Filter, Ban, Trash2, AlertTriangle } from 'lucide-react';
import { adminApi } from '../../lib/api';
import { Product } from '../../types/api';

interface ProductCardProps {
  product: Product;
  onApprove: (product: Product) => void;
  onReject: (product: Product) => void;
  onView: (product: Product) => void;
  onBlock: (product: Product) => void;
  onUnblock: (product: Product) => void;
  onDelete: (product: Product) => void;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, onApprove, onReject, onView, onBlock, onUnblock, onDelete }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'blocked': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="card p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="font-semibold text-secondary-900 mb-2">{product.name}</h3>
          <p className="text-sm text-secondary-600 mb-2">
            by {product.seller_name || product.seller?.first_name} {product.seller?.last_name || ''} ({product.seller_email || product.seller?.user?.email || ''})
          </p>
          <p className="text-sm text-secondary-500 line-clamp-2">{product.description}</p>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(product.status)}`}>
          {product.status}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
        <div>
          <span className="text-secondary-600">Seller Price:</span>
          <span className="font-medium ml-2">₹{product.seller_price?.toLocaleString()}</span>
        </div>
        <div>
          <span className="text-secondary-600">Customer Price:</span>
          <span className="font-medium ml-2">₹{product.customer_price?.toLocaleString()}</span>
        </div>
        <div>
          <span className="text-secondary-600">Commission:</span>
          <span className="font-medium ml-2">{product.commission_rate}%</span>
        </div>
        <div>
          <span className="text-secondary-600">Stock:</span>
          <span className="font-medium ml-2">{product.stock_quantity}</span>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <button
          onClick={() => onView(product)}
          className="flex items-center space-x-2 text-primary-600 hover:text-primary-700"
        >
          <Eye className="w-4 h-4" />
          <span className="text-sm">View Details</span>
        </button>

        {product.status === 'pending' && (
          <div className="flex space-x-2">
            <button
              onClick={() => onReject(product)}
              className="flex items-center space-x-1 px-3 py-1 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
            >
              <X className="w-4 h-4" />
              <span className="text-sm">Reject</span>
            </button>
            <button
              onClick={() => onApprove(product)}
              className="flex items-center space-x-1 px-3 py-1 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
            >
              <Check className="w-4 h-4" />
              <span className="text-sm">Approve</span>
            </button>
          </div>
        )}

        {product.status === 'approved' && (
          <div className="flex space-x-2">
            <button
              onClick={() => onBlock(product)}
              className="flex items-center space-x-1 px-3 py-1 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-colors"
            >
              <Ban className="w-4 h-4" />
              <span className="text-sm">Block</span>
            </button>
            <button
              onClick={() => onDelete(product)}
              className="flex items-center space-x-1 px-3 py-1 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              <span className="text-sm">Delete</span>
            </button>
          </div>
        )}

        {product.status === 'blocked' && (
          <div className="flex space-x-2">
            <button
              onClick={() => onUnblock(product)}
              className="flex items-center space-x-1 px-3 py-1 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
            >
              <Check className="w-4 h-4" />
              <span className="text-sm">Unblock</span>
            </button>
            <button
              onClick={() => onDelete(product)}
              className="flex items-center space-x-1 px-3 py-1 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              <span className="text-sm">Delete</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

const Products: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [actionNotes, setActionNotes] = useState('');
  const [commissionRate, setCommissionRate] = useState(0);
  const [modalAction, setModalAction] = useState<'approve' | 'reject' | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  useEffect(() => {
    fetchProducts();
  }, []);

  useEffect(() => {
    filterProducts();
  }, [products, searchTerm, statusFilter]);

  const fetchProducts = async () => {
    try {
      setIsLoading(true);
      const data = await adminApi.getProducts();
      setProducts(data);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filterProducts = () => {
    let filtered = products;

    if (searchTerm) {
      filtered = filtered.filter(product =>
        product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(product => product.status === statusFilter);
    }

    setFilteredProducts(filtered);
  };

  const handleApprove = (product: Product) => {
    setSelectedProduct(product);
    setModalAction('approve');
    setCommissionRate(product.commission_rate);
    setActionNotes('');
    setShowModal(true);
  };

  const handleReject = (product: Product) => {
    setSelectedProduct(product);
    setModalAction('reject');
    setCommissionRate(product.commission_rate);
    setActionNotes('');
    setShowModal(true);
  };

  const handleModalSubmit = async () => {
    if (!selectedProduct || !modalAction) return;

    try {
      const status = modalAction === 'approve' ? 'approved' : 'rejected';
      await adminApi.approveProduct(selectedProduct.id, {
        status,
        admin_notes: actionNotes,
        commission_rate: commissionRate
      });
      
      setShowModal(false);
      setActionNotes('');
      setCommissionRate(0);
      setSelectedProduct(null);
      setModalAction(null);
      fetchProducts();
    } catch (error) {
      console.error('Error updating product:', error);
    }
  };

  const handleView = (product: Product) => {
    setSelectedProduct(product);
    setShowDetailsModal(true);
  };

  const handleBlock = async (product: Product) => {
    if (window.confirm('Are you sure you want to block this product?')) {
      try {
        await adminApi.approveProduct(product.id, {
          status: 'blocked',
          admin_notes: 'Product blocked by admin'
        });
        fetchProducts();
      } catch (error) {
        console.error('Error blocking product:', error);
      }
    }
  };

  const handleUnblock = async (product: Product) => {
    if (window.confirm('Are you sure you want to unblock this product?')) {
      try {
        await adminApi.approveProduct(product.id, {
          status: 'approved',
          admin_notes: 'Product unblocked by admin'
        });
        fetchProducts();
      } catch (error) {
        console.error('Error unblocking product:', error);
      }
    }
  };

  const handleDelete = async (product: Product) => {
    if (window.confirm('Are you sure you want to permanently delete this product? This action cannot be undone.')) {
      try {
        await adminApi.deleteProduct(product.id);
        fetchProducts();
      } catch (error) {
        console.error('Error deleting product:', error);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Product Management</h1>
          <p className="text-secondary-600">Review and approve seller products</p>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0 md:space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 input-field"
            />
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-secondary-600" />
              <span className="text-sm font-medium text-secondary-700">Status:</span>
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-field w-auto"
            >
              <option value="all">All</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="blocked">Blocked</option>
            </select>
          </div>
        </div>
      </div>

      {/* Products Grid */}
      {filteredProducts.length === 0 ? (
        <div className="card p-12 text-center">
          <Package className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-secondary-900 mb-2">No Products Found</h3>
          <p className="text-secondary-600">No products match your current filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onApprove={handleApprove}
              onReject={handleReject}
              onView={handleView}
              onBlock={handleBlock}
              onUnblock={handleUnblock}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {/* Approval Modal */}
      {showModal && selectedProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">
              {modalAction === 'approve' ? 'Approve' : 'Reject'} Product
            </h3>
            
            <p className="text-secondary-600 mb-4">
              Product: <span className="font-medium">{selectedProduct.name}</span>
            </p>
            
            {modalAction === 'approve' && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Commission Rate (%)
                </label>
                <input
                  type="number"
                  value={commissionRate}
                  onChange={(e) => setCommissionRate(parseFloat(e.target.value) || 0)}
                  min="0"
                  max="100"
                  step="0.01"
                  className="input-field"
                  placeholder="Enter commission rate"
                />
                <p className="text-xs text-secondary-500 mt-1">
                  Current rate: {selectedProduct.commission_rate}%
                </p>
              </div>
            )}
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Admin Notes (Optional)
              </label>
              <textarea
                value={actionNotes}
                onChange={(e) => setActionNotes(e.target.value)}
                placeholder="Add any notes about this decision..."
                className="input-field h-24 resize-none"
              />
            </div>
            
            <div className="flex space-x-3">
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleModalSubmit}
                className="flex-1 btn-primary"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Product Details Modal */}
      {showDetailsModal && selectedProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-secondary-900">
                Product Details
              </h3>
              <button
                onClick={() => setShowDetailsModal(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Product Name</label>
                  <p className="text-secondary-900">{selectedProduct.name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Status</label>
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                    selectedProduct.status === 'approved' ? 'bg-green-100 text-green-800' :
                    selectedProduct.status === 'rejected' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {selectedProduct.status}
                  </span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Seller Price</label>
                  <p className="text-secondary-900">₹{selectedProduct.seller_price}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Customer Price</label>
                  <p className="text-secondary-900">₹{selectedProduct.customer_price}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Commission Rate</label>
                  <p className="text-secondary-900">{selectedProduct.commission_rate}%</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Stock Quantity</label>
                  <p className="text-secondary-900">{selectedProduct.stock_quantity}</p>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary-700">Description</label>
                <p className="text-secondary-900 mt-1 whitespace-pre-wrap">{selectedProduct.description || 'No description provided'}</p>
              </div>
              
              {selectedProduct.tags && (
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Tags</label>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {JSON.parse(selectedProduct.tags).map((tag: string, index: number) => (
                      <span key={index} className="inline-flex px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selectedProduct.images && selectedProduct.images.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Product Images</label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-2">
                    {selectedProduct.images.map((image: any, index: number) => (
                      <div key={index} className="relative">
                        <img
                          src={image.image_url}
                          alt={image.alt_text || `Product image ${index + 1}`}
                          className="w-full h-32 object-cover rounded-lg border"
                        />
                        <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs p-2 rounded-b-lg">
                          {image.alt_text || `Image ${index + 1}`}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Products; 