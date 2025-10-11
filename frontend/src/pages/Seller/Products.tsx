import React, { useState, useEffect } from 'react';
import { Package, Eye, Edit, Trash2, Plus, Search, Filter, X } from 'lucide-react';
import { Link } from 'react-router-dom';
import { sellerApi } from '../../lib/api';
import { Product } from '../../types/api';

const Products: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
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
      const data = await sellerApi.getProducts();
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'draft': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleDelete = async (productId: string) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await sellerApi.deleteProduct(productId);
        fetchProducts();
      } catch (error) {
        console.error('Error deleting product:', error);
      }
    }
  };

  const handleView = async (product: Product) => {
    try {
      // Fetch full product details including variants
      const fullProduct = await sellerApi.getProduct(product.id);
      setSelectedProduct(fullProduct);
      setShowDetailsModal(true);
    } catch (error) {
      console.error('Error fetching product details:', error);
      // Fallback to basic product data
      setSelectedProduct(product);
      setShowDetailsModal(true);
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
      <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold text-secondary-900">My Products</h1>
        <p className="text-secondary-600">Manage your product catalog</p>
        </div>
        <Link
          to="/seller/products/new"
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>Add Product</span>
        </Link>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400" />
              <input
                type="text"
                placeholder="Search products..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-field pl-10"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-field"
            >
              <option value="all">All Status</option>
              <option value="draft">Draft</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>
      </div>

      {/* Products List */}
      {filteredProducts.length === 0 ? (
      <div className="card p-12 text-center">
        <Package className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-secondary-900 mb-2">No Products Found</h3>
          <p className="text-secondary-600 mb-4">
            {searchTerm || statusFilter !== 'all' 
              ? 'No products match your current filters.' 
              : 'You haven\'t created any products yet.'}
          </p>
          <Link to="/seller/products/new" className="btn-primary">
            Create Your First Product
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {filteredProducts.map((product) => (
            <div key={product.id} className="card p-6">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-medium text-secondary-900">{product.name}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(product.status)}`}>
                      {product.status}
                    </span>
                  </div>
                  <p className="text-sm text-secondary-600 mb-2 line-clamp-2">{product.description}</p>
                  <div className="flex items-center space-x-4 text-sm text-secondary-500">
                    <span>Price: ₹{product.seller_price}</span>
                    <span>Stock: {product.stock_quantity}</span>
                    <span>Created: {new Date(product.created_at).toLocaleDateString()}</span>
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-secondary-500 mt-1">
                    <span>By: {product.seller_name || 'Unknown Seller'}</span>
                    <span>{product.seller_email || ''}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleView(product)}
                    className="p-2 text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg"
                    title="View Details"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  {product.status !== 'approved' && (
                    <Link
                      to={`/seller/products/edit/${product.id}`}
                      className="p-2 text-secondary-600 hover:text-secondary-700 hover:bg-secondary-50 rounded-lg"
                      title="Edit Product"
                    >
                      <Edit className="w-4 h-4" />
                    </Link>
                  )}
                  <button
                    onClick={() => handleDelete(product.id)}
                    className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg"
                    title="Delete Product"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
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
                    selectedProduct.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
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
                <div>
                  <label className="block text-sm font-medium text-secondary-700">SKU</label>
                  <p className="text-secondary-900">{selectedProduct.sku}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Created</label>
                  <p className="text-secondary-900">{new Date(selectedProduct.created_at).toLocaleDateString()}</p>
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

              {/* Product Variants */}
              {selectedProduct.variants && selectedProduct.variants.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">Product Variants</label>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-secondary-200">
                      <thead className="bg-secondary-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-secondary-700 uppercase">Variant</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-secondary-700 uppercase">SKU</th>
                          <th className="px-4 py-2 text-right text-xs font-medium text-secondary-700 uppercase">Seller Price</th>
                          <th className="px-4 py-2 text-right text-xs font-medium text-secondary-700 uppercase">Customer Price</th>
                          <th className="px-4 py-2 text-right text-xs font-medium text-secondary-700 uppercase">Stock</th>
                          <th className="px-4 py-2 text-center text-xs font-medium text-secondary-700 uppercase">Status</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-secondary-200">
                        {selectedProduct.variants.map((variant: any) => (
                          <tr key={variant.id}>
                            <td className="px-4 py-2 text-sm text-secondary-900">{variant.variant_name || 'Default'}</td>
                            <td className="px-4 py-2 text-sm text-secondary-600">{variant.sku}</td>
                            <td className="px-4 py-2 text-sm text-secondary-900 text-right">₹{variant.seller_price.toFixed(2)}</td>
                            <td className="px-4 py-2 text-sm text-secondary-900 text-right">₹{variant.customer_price.toFixed(2)}</td>
                            <td className="px-4 py-2 text-sm text-secondary-900 text-right">{variant.stock_quantity}</td>
                            <td className="px-4 py-2 text-center">
                              <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                                variant.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                              }`}>
                                {variant.is_active ? 'Active' : 'Inactive'}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
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