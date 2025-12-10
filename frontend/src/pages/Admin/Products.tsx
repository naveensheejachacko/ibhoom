import React, { useState, useEffect } from 'react';
import { Package, Eye, Check, X, Search, Filter, Ban, Trash2, AlertTriangle, Sparkles, Edit, Upload } from 'lucide-react';
import { adminApi } from '../../lib/api';
import Pagination from '../../components/Pagination';
import { Product } from '../../types/api';
import DynamicCategorySelector from '../../components/DynamicCategorySelector';
import ImageCropModal from '../../components/ImageCropModal';

interface ProductCardProps {
  product: Product;
  onApprove: (product: Product) => void;
  onReject: (product: Product) => void;
  onView: (product: Product) => void;
  onEdit: (product: Product) => void;
  onBlock: (product: Product) => void;
  onUnblock: (product: Product) => void;
  onDelete: (product: Product) => void;
  onToggleNewlyArrived?: (product: Product, isNewlyArrived: boolean) => void;
  isToggling?: boolean;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, onApprove, onReject, onView, onEdit, onBlock, onUnblock, onDelete, onToggleNewlyArrived, isToggling }) => {
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
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-semibold text-secondary-900">{product.name}</h3>
            {product.is_newly_arrived && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                <Sparkles className="w-3 h-3 mr-1" />
                Newly Arrived
              </span>
            )}
          </div>
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
          <span className="text-secondary-600">Tax Rate:</span>
          <span className="font-medium ml-2">{product.tax_rate || 18}%</span>
        </div>
        <div>
          <span className="text-secondary-600">Stock:</span>
          <span className="font-medium ml-2">{product.stock_quantity}</span>
        </div>
      </div>

      <div className="flex items-center space-x-2 flex-wrap">
        <button
          onClick={() => onView(product)}
          className="flex items-center space-x-2 text-primary-600 hover:text-primary-700"
        >
          <Eye className="w-4 h-4" />
          <span className="text-sm">View Details</span>
        </button>
        <button
          onClick={() => onEdit(product)}
          className="flex items-center space-x-2 text-blue-600 hover:text-blue-700"
        >
          <Edit className="w-4 h-4" />
          <span className="text-sm">Edit</span>
        </button>

        {product.status === 'pending' && (
          <>
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
          </>
        )}

        {product.status === 'approved' && (
          <>
            {onToggleNewlyArrived && (
              <button
                onClick={() => onToggleNewlyArrived(product, !product.is_newly_arrived)}
                disabled={isToggling}
                className={`flex items-center space-x-1 px-3 py-1 rounded-lg text-sm transition-colors ${
                  product.is_newly_arrived
                    ? 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                } ${isToggling ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <Sparkles className="w-4 h-4" />
                <span className="text-sm">{product.is_newly_arrived ? 'Remove from New Arrivals' : 'Mark as New Arrival'}</span>
              </button>
            )}
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
          </>
        )}

        {product.status === 'blocked' && (
          <>
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
          </>
        )}
      </div>
    </div>
  );
};

const Products: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [actionNotes, setActionNotes] = useState('');
  const [commissionRate, setCommissionRate] = useState(0);
  const [taxRate, setTaxRate] = useState(18);
  const [isNewlyArrived, setIsNewlyArrived] = useState(false);
  const [modalAction, setModalAction] = useState<'approve' | 'reject' | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [editFormData, setEditFormData] = useState<any>({});
  const [editImages, setEditImages] = useState<any[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [categories, setCategories] = useState<any[]>([]);
  // Image cropping state
  const [showCropModal, setShowCropModal] = useState(false);
  const [imageToCrop, setImageToCrop] = useState<string | null>(null);
  const [pendingImageFile, setPendingImageFile] = useState<{ file: File; name: string } | null>(null);
  const [pendingImageQueue, setPendingImageQueue] = useState<{ file: File; name: string }[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPerPage = 20;

  // Debounce search term to avoid triggering search on every keystroke
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 500); // Wait 500ms after user stops typing

    return () => clearTimeout(timer);
  }, [searchTerm]);

  useEffect(() => {
    fetchProducts();
    loadCategories();
  }, [currentPage, statusFilter, debouncedSearchTerm]);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [statusFilter, debouncedSearchTerm]);

  const loadCategories = async () => {
    try {
      const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/categories`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setCategories(data);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const fetchProducts = async () => {
    try {
      setIsLoading(true);
      const params: any = {
        page: currentPage,
        limit: itemsPerPage,
      };
      
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      
      if (debouncedSearchTerm) {
        params.search = debouncedSearchTerm;
      }
      
      const data = await adminApi.getProducts(params);
      
      // Handle paginated response
      if (data.items) {
        setProducts(data.items);
        setTotalPages(data.pages);
        setTotalItems(data.total);
      } else {
        // Fallback for non-paginated response
        setProducts(Array.isArray(data) ? data : []);
      }
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = (product: Product) => {
    setSelectedProduct(product);
    setModalAction('approve');
    setCommissionRate(product.commission_rate);
    setTaxRate(product.tax_rate || 18);
    setIsNewlyArrived(product.is_newly_arrived || false);
    setActionNotes('');
    setShowModal(true);
  };

  const handleReject = (product: Product) => {
    setSelectedProduct(product);
    setModalAction('reject');
    setCommissionRate(product.commission_rate);
    setTaxRate(product.tax_rate || 18);
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
        commission_rate: commissionRate,
        tax_rate: taxRate,
        is_newly_arrived: modalAction === 'approve' ? isNewlyArrived : undefined
      });
      
      setShowModal(false);
      setActionNotes('');
      setCommissionRate(0);
      setTaxRate(18);
      setIsNewlyArrived(false);
      setSelectedProduct(null);
      setModalAction(null);
      fetchProducts();
    } catch (error) {
      console.error('Error updating product:', error);
    }
  };

  const handleView = async (product: Product) => {
    try {
      // Fetch full product details including variants
      const fullProduct = await adminApi.getProduct(product.id);
      setSelectedProduct(fullProduct);
      setShowDetailsModal(true);
    } catch (error) {
      console.error('Error fetching product details:', error);
      // Fallback to basic product data
      setSelectedProduct(product);
      setShowDetailsModal(true);
    }
  };

  const handleEdit = async (product: Product) => {
    try {
      // Fetch full product details for editing
      const fullProduct = await adminApi.getProduct(product.id);
      
      if (!fullProduct) {
        alert('Product not found');
        return;
      }
      
      setEditingProduct(fullProduct);
      
      // Parse tags safely
      let tagsString = '';
      try {
        if (fullProduct.tags) {
          const parsedTags = typeof fullProduct.tags === 'string' 
            ? JSON.parse(fullProduct.tags) 
            : fullProduct.tags;
          tagsString = Array.isArray(parsedTags) ? parsedTags.join(', ') : '';
        }
      } catch (e) {
        console.warn('Error parsing tags:', e);
        tagsString = '';
      }
      
      // Initialize form data
      setEditFormData({
        name: fullProduct.name || '',
        description: fullProduct.description || '',
        short_description: fullProduct.short_description || '',
        sku: fullProduct.sku || '',
        category_id: fullProduct.category_id || '',
        seller_price: fullProduct.seller_price || 0,
        stock_quantity: fullProduct.stock_quantity || 0,
        tags: tagsString,
        meta_title: fullProduct.meta_title || '',
        meta_description: fullProduct.meta_description || '',
        has_return_policy: fullProduct.has_return_policy || false,
        return_period_days: fullProduct.return_period_days || 7,
        return_policy_description: fullProduct.return_policy_description || '',
        is_newly_arrived: fullProduct.is_newly_arrived || false,
      });
      
      // Initialize images
      setEditImages(Array.isArray(fullProduct.images) ? fullProduct.images : []);
      setShowEditModal(true);
    } catch (error: any) {
      console.error('Error fetching product for editing:', error);
      alert(error.response?.data?.detail || 'Failed to load product details for editing');
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    const imageFiles = Array.from(files).filter(file => file.type.startsWith('image/'));
    if (imageFiles.length === 0) return;

    // Process first file
    const firstFile = imageFiles[0];
    const reader = new FileReader();
    reader.onload = (event) => {
      const imageUrl = event.target?.result as string;
      // Show crop modal for first image
      setImageToCrop(imageUrl);
      setPendingImageFile({ file: firstFile, name: firstFile.name });
      // Queue remaining files
      if (imageFiles.length > 1) {
        setPendingImageQueue(imageFiles.slice(1).map(f => ({ file: f, name: f.name })));
      }
      setShowCropModal(true);
    };
    reader.readAsDataURL(firstFile);
    
    // Reset input to allow selecting the same file again
    e.target.value = '';
  };

  const processNextImageInQueue = () => {
    if (pendingImageQueue.length > 0) {
      const nextImage = pendingImageQueue[0];
      const reader = new FileReader();
      reader.onload = (event) => {
        const imageUrl = event.target?.result as string;
        setImageToCrop(imageUrl);
        setPendingImageFile(nextImage);
        setPendingImageQueue(prev => prev.slice(1));
        setShowCropModal(true);
      };
      reader.readAsDataURL(nextImage.file);
    }
  };

  const handleCropComplete = (croppedImage: string) => {
    if (!pendingImageFile) return;
    
    const newImage = {
      image_url: croppedImage,
      alt_text: pendingImageFile.name,
      sort_order: editImages.length
    };
    
    setEditImages([...editImages, newImage]);
    
    // Reset current crop state
    setImageToCrop(null);
    setPendingImageFile(null);
    setShowCropModal(false);
    
    // Process next image in queue if any
    setTimeout(() => {
      processNextImageInQueue();
    }, 100);
  };

  const handleCropCancel = () => {
    setImageToCrop(null);
    setPendingImageFile(null);
    setShowCropModal(false);
    // Clear queue on cancel
    setPendingImageQueue([]);
  };

  const handleRemoveImage = (index: number) => {
    setEditImages(editImages.filter((_, i) => i !== index));
  };

  const handleSaveEdit = async () => {
    if (!editingProduct) return;

    try {
      setIsSaving(true);
      
      // Prepare update data
      const updateData: any = {
        name: editFormData.name,
        description: editFormData.description,
        short_description: editFormData.short_description,
        sku: editFormData.sku,
        category_id: editFormData.category_id,
        seller_price: parseFloat(editFormData.seller_price),
        stock_quantity: parseInt(editFormData.stock_quantity),
        meta_title: editFormData.meta_title,
        meta_description: editFormData.meta_description,
        has_return_policy: editFormData.has_return_policy,
        return_period_days: parseInt(editFormData.return_period_days),
        return_policy_description: editFormData.return_policy_description,
        is_newly_arrived: editFormData.is_newly_arrived,
      };

      // Handle tags
      if (editFormData.tags) {
        const tagsArray = editFormData.tags.split(',').map((tag: string) => tag.trim()).filter((tag: string) => tag);
        updateData.tags = JSON.stringify(tagsArray);
      }

      // Handle images
      if (editImages.length > 0) {
        updateData.images = editImages.map((img, index) => ({
          image_url: img.image_url,
          alt_text: img.alt_text || `Product image ${index + 1}`,
          sort_order: index,
        }));
      }

      await adminApi.updateProduct(editingProduct.id, updateData);
      
      setShowEditModal(false);
      setEditingProduct(null);
      setEditFormData({});
      setEditImages([]);
      fetchProducts();
    } catch (error: any) {
      console.error('Error updating product:', error);
      alert(error.response?.data?.detail || 'Failed to update product');
    } finally {
      setIsSaving(false);
    }
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

  const [togglingNewlyArrived, setTogglingNewlyArrived] = useState<string | null>(null);

  const handleToggleNewlyArrived = async (product: Product, isNewlyArrived: boolean) => {
    setTogglingNewlyArrived(product.id);
    try {
      await adminApi.toggleNewlyArrived(product.id, isNewlyArrived);
      fetchProducts();
    } catch (error: any) {
      console.error('Error toggling newly arrived:', error);
      alert(error.response?.data?.detail || 'Failed to update newly arrived status');
    } finally {
      setTogglingNewlyArrived(null);
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
      {products.length === 0 ? (
        <div className="card p-12 text-center">
          <Package className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-secondary-900 mb-2">No Products Found</h3>
          <p className="text-secondary-600">No products match your current filters.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onApprove={handleApprove}
              onReject={handleReject}
              onView={handleView}
              onEdit={handleEdit}
              onBlock={handleBlock}
              onUnblock={handleUnblock}
              onDelete={handleDelete}
              onToggleNewlyArrived={handleToggleNewlyArrived}
              isToggling={togglingNewlyArrived === product.id}
            />
          ))}
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
        </>
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
              <>
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
                <div className="mb-4">
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Tax Rate (%)
                  </label>
                  <input
                    type="number"
                    value={taxRate}
                    onChange={(e) => setTaxRate(parseFloat(e.target.value) || 18)}
                    min="0"
                    max="100"
                    step="0.01"
                    className="input-field"
                    placeholder="Enter tax rate"
                  />
                  <p className="text-xs text-secondary-500 mt-1">
                    Current rate: {selectedProduct.tax_rate || 18}% (Default: 18%)
                  </p>
                </div>
                <div className="mb-4">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={isNewlyArrived}
                      onChange={(e) => setIsNewlyArrived(e.target.checked)}
                      className="rounded"
                    />
                    <span className="text-sm font-medium text-secondary-700 flex items-center">
                      <Sparkles className="w-4 h-4 mr-1" />
                      Mark as Newly Arrived
                    </span>
                  </label>
                  <p className="text-xs text-secondary-500 mt-1 ml-6">
                    This product will appear in the "Newly Arrived" section for customers
                  </p>
                </div>
              </>
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
                {selectedProduct.seller_price !== undefined && (
                  <div>
                    <label className="block text-sm font-medium text-secondary-700">Seller Price</label>
                    <p className="text-secondary-900">₹{selectedProduct.seller_price}</p>
                  </div>
                )}
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Customer Price</label>
                  <p className="text-secondary-900">₹{selectedProduct.customer_price?.toFixed(2)}</p>
                </div>
                {selectedProduct.commission_rate !== undefined && (
                  <div>
                    <label className="block text-sm font-medium text-secondary-700">Commission Rate</label>
                    <p className="text-secondary-900">{selectedProduct.commission_rate}%</p>
                  </div>
                )}
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Tax Rate</label>
                  <p className="text-secondary-900">{selectedProduct.tax_rate || 18}%</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Stock Quantity</label>
                  <p className="text-secondary-900">{selectedProduct.stock_quantity}</p>
                </div>
                {selectedProduct.seller && (
                  <div>
                    <label className="block text-sm font-medium text-secondary-700">Seller</label>
                    <p className="text-secondary-900">{selectedProduct.seller.business_name}</p>
                  </div>
                )}
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Return Policy</label>
                  <p className="text-secondary-900">
                    {selectedProduct.has_return_policy ? (
                      <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                        ✓ Enabled
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
                        ✗ Not Available
                      </span>
                    )}
                  </p>
                </div>
                {selectedProduct.has_return_policy && (
                  <div>
                    <label className="block text-sm font-medium text-secondary-700">Return Period</label>
                    <p className="text-secondary-900">{selectedProduct.return_period_days || 30} Days</p>
                  </div>
                )}
              </div>
              
              {selectedProduct.has_return_policy && selectedProduct.return_policy_description && (
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Return Policy Details</label>
                  <p className="text-secondary-900 mt-1 whitespace-pre-wrap bg-gray-50 p-3 rounded-lg">
                    {selectedProduct.return_policy_description}
                  </p>
                </div>
              )}
              
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
                          <th className="px-4 py-2 text-right text-xs font-medium text-secondary-700 uppercase">Customer Price</th>
                          <th className="px-4 py-2 text-right text-xs font-medium text-secondary-700 uppercase">Tax Rate</th>
                          <th className="px-4 py-2 text-right text-xs font-medium text-secondary-700 uppercase">Stock</th>
                          <th className="px-4 py-2 text-center text-xs font-medium text-secondary-700 uppercase">Status</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-secondary-200">
                        {selectedProduct.variants.map((variant: any) => (
                          <tr key={variant.id}>
                            <td className="px-4 py-2 text-sm text-secondary-900">{variant.variant_name || 'Default'}</td>
                            <td className="px-4 py-2 text-sm text-secondary-600">{variant.sku}</td>
                            <td className="px-4 py-2 text-sm text-secondary-900 text-right">₹{variant.customer_price?.toFixed(2) || 'N/A'}</td>
                            <td className="px-4 py-2 text-sm text-secondary-600 text-right">{variant.tax_rate || 18}%</td>
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

      {/* Edit Product Modal */}
      {showEditModal && editingProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl my-8 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-secondary-900">
                Edit Product
              </h3>
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setEditingProduct(null);
                  setEditFormData({});
                  setEditImages([]);
                }}
                className="text-secondary-400 hover:text-secondary-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {categories.length === 0 ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                <span className="ml-3 text-secondary-600">Loading categories...</span>
              </div>
            ) : (
            <div className="space-y-4">
              {/* Basic Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Product Name *
                  </label>
                  <input
                    type="text"
                    value={editFormData.name || ''}
                    onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                    className="input-field"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    SKU
                  </label>
                  <input
                    type="text"
                    value={editFormData.sku || ''}
                    onChange={(e) => setEditFormData({ ...editFormData, sku: e.target.value })}
                    className="input-field"
                  />
                </div>
                <div>
                  <DynamicCategorySelector
                    categories={categories}
                    selectedCategoryId={editFormData.category_id || ''}
                    onCategorySelect={(categoryId) => setEditFormData({ ...editFormData, category_id: categoryId })}
                    error={!editFormData.category_id ? 'Please select a category.' : undefined}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Seller Price (₹) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={editFormData.seller_price || 0}
                    onChange={(e) => setEditFormData({ ...editFormData, seller_price: e.target.value })}
                    className="input-field"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Stock Quantity *
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={editFormData.stock_quantity || 0}
                    onChange={(e) => setEditFormData({ ...editFormData, stock_quantity: e.target.value })}
                    className="input-field"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Short Description
                </label>
                <input
                  type="text"
                  value={editFormData.short_description || ''}
                  onChange={(e) => setEditFormData({ ...editFormData, short_description: e.target.value })}
                  className="input-field"
                  placeholder="Brief description (max 500 characters)"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Description *
                </label>
                <textarea
                  value={editFormData.description || ''}
                  onChange={(e) => setEditFormData({ ...editFormData, description: e.target.value })}
                  className="input-field h-32 resize-none"
                  required
                />
              </div>

              {/* Images */}
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Product Images
                </label>
                <div className="border-2 border-dashed border-secondary-300 rounded-lg p-4 mb-4">
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                    id="edit-image-upload"
                  />
                  <label
                    htmlFor="edit-image-upload"
                    className="cursor-pointer flex items-center space-x-2 text-secondary-600 hover:text-secondary-700"
                  >
                    <Upload className="w-5 h-5" />
                    <span>Add Images</span>
                  </label>
                </div>
                {editImages.length > 0 && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {editImages.map((img, index) => (
                      <div key={index} className="relative">
                        <img
                          src={img.image_url}
                          alt={img.alt_text || `Image ${index + 1}`}
                          className="w-full h-32 object-cover rounded-lg border"
                        />
                        <button
                          onClick={() => handleRemoveImage(index)}
                          className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                        >
                          <X className="w-4 h-4" />
                        </button>
                        <input
                          type="text"
                          value={img.alt_text || ''}
                          onChange={(e) => {
                            const updated = [...editImages];
                            updated[index].alt_text = e.target.value;
                            setEditImages(updated);
                          }}
                          placeholder="Alt text"
                          className="mt-1 input-field text-xs"
                        />
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Tags */}
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={editFormData.tags || ''}
                  onChange={(e) => setEditFormData({ ...editFormData, tags: e.target.value })}
                  className="input-field"
                  placeholder="tag1, tag2, tag3"
                />
              </div>

              {/* SEO */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Meta Title
                  </label>
                  <input
                    type="text"
                    value={editFormData.meta_title || ''}
                    onChange={(e) => setEditFormData({ ...editFormData, meta_title: e.target.value })}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Meta Description
                  </label>
                  <input
                    type="text"
                    value={editFormData.meta_description || ''}
                    onChange={(e) => setEditFormData({ ...editFormData, meta_description: e.target.value })}
                    className="input-field"
                  />
                </div>
              </div>

              {/* Return Policy */}
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={editFormData.has_return_policy || false}
                    onChange={(e) => setEditFormData({ ...editFormData, has_return_policy: e.target.checked })}
                    className="rounded"
                  />
                  <label className="text-sm font-medium text-secondary-700">
                    Allow returns for this product
                  </label>
                </div>
                {editFormData.has_return_policy && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-2">
                        Return Period (Days) <span className="text-red-500">*</span>
                      </label>
                      <select
                        value={editFormData.return_period_days || 7}
                        onChange={(e) => setEditFormData({ ...editFormData, return_period_days: parseInt(e.target.value) })}
                        className="input-field"
                        required={editFormData.has_return_policy}
                      >
                        <option value="7">7 Days</option>
                        <option value="14">14 Days</option>
                        <option value="30">30 Days</option>
                        <option value="60">60 Days</option>
                        <option value="90">90 Days</option>
                      </select>
                      <p className="text-xs text-secondary-600 mt-1">
                        Customers can return within this period after delivery
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-2">
                        Return Policy Description
                      </label>
                      <textarea
                        value={editFormData.return_policy_description || ''}
                        onChange={(e) => setEditFormData({ ...editFormData, return_policy_description: e.target.value })}
                        className="input-field h-24 resize-none"
                        placeholder="e.g., Easy 30-day returns. Items must be in original condition with tags attached."
                      />
                      <p className="text-xs text-secondary-600 mt-1">
                        Describe your return policy terms and conditions
                      </p>
                    </div>
                  </>
                )}
              </div>

              {/* Newly Arrived */}
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={editFormData.is_newly_arrived || false}
                  onChange={(e) => setEditFormData({ ...editFormData, is_newly_arrived: e.target.checked })}
                  className="rounded"
                />
                <label className="text-sm font-medium text-secondary-700 flex items-center">
                  <Sparkles className="w-4 h-4 mr-1" />
                  Mark as Newly Arrived
                </label>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-3 pt-4 border-t">
                <button
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingProduct(null);
                    setEditFormData({});
                    setEditImages([]);
                  }}
                  className="flex-1 btn-secondary"
                  disabled={isSaving}
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveEdit}
                  className="flex-1 btn-primary"
                  disabled={isSaving}
                >
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>
            )}
          </div>
        </div>
      )}

      {/* Image Crop Modal */}
      {showCropModal && imageToCrop && (
        <ImageCropModal
          image={imageToCrop}
          onClose={handleCropCancel}
          onCropComplete={handleCropComplete}
          aspectRatio={1}
          cropShape="rect"
          outputWidth={800}
          outputHeight={800}
          queueCount={pendingImageQueue.length}
        />
      )}
    </div>
  );
};

export default Products; 