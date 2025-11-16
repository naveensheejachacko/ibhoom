import React, { useState, useEffect } from 'react';
import { Image, Plus, Edit2, Trash2, Eye, Filter, Search, Calendar, Link as LinkIcon } from 'lucide-react';
import { adminApi } from '../../lib/api';
import { useToast } from '../../components/Toast';
import Pagination from '../../components/Pagination';

interface Banner {
  id: string;
  title: string;
  description?: string;
  image_url: string;
  link_url?: string;
  position: 'home_top' | 'home_middle' | 'home_bottom' | 'category_top' | 'product_top' | 'cart_top' | 'checkout_top';
  status: 'active' | 'inactive' | 'draft';
  sort_order: number;
  start_date?: string;
  end_date?: string;
  click_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const Banners: React.FC = () => {
  const [banners, setBanners] = useState<Banner[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingBanner, setEditingBanner] = useState<Banner | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [positionFilter, setPositionFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPerPage = 20;
  const toast = useToast();

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    link_url: '',
    position: 'home_top' as Banner['position'],
    status: 'draft' as Banner['status'],
    sort_order: 0,
    start_date: '',
    end_date: '',
  });
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  useEffect(() => {
    fetchBanners();
  }, [currentPage, positionFilter, statusFilter]);

  const fetchBanners = async () => {
    try {
      setIsLoading(true);
      const params: any = {
        page: currentPage,
        limit: itemsPerPage,
      };
      if (positionFilter !== 'all') {
        params.position = positionFilter;
      }
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      const response = await adminApi.getBanners(params);
      setBanners(response.items || []);
      setTotalPages(response.pages || 1);
      setTotalItems(response.total || 0);
    } catch (error: any) {
      console.error('Error fetching banners:', error);
      toast.show(error.response?.data?.detail || 'Failed to load banners', { type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate image file for new banners
    if (!editingBanner && !imageFile) {
      toast.show('Please select an image file', { type: 'error' });
      return;
    }
    
    try {
      const bannerData: any = {
        ...formData,
        sort_order: parseInt(formData.sort_order.toString()) || 0,
      };
      
      // Only include dates if they have values
      if (formData.start_date) {
        bannerData.start_date = formData.start_date;
      }
      if (formData.end_date) {
        bannerData.end_date = formData.end_date;
      }

      if (editingBanner) {
        await adminApi.updateBanner(editingBanner.id, bannerData, imageFile || undefined);
        toast.show('Banner updated successfully', { type: 'success' });
      } else {
        await adminApi.createBanner(bannerData, imageFile || undefined);
        toast.show('Banner created successfully', { type: 'success' });
      }
      setShowModal(false);
      resetForm();
      fetchBanners();
    } catch (error: any) {
      console.error('Error saving banner:', error);
      toast.show(error.response?.data?.detail || 'Failed to save banner', { type: 'error' });
    }
  };

  const handleDelete = async (banner: Banner) => {
    if (!window.confirm(`Are you sure you want to delete "${banner.title}"?`)) {
      return;
    }
    try {
      await adminApi.deleteBanner(banner.id);
      toast.show('Banner deleted successfully', { type: 'success' });
      fetchBanners();
    } catch (error: any) {
      console.error('Error deleting banner:', error);
      toast.show(error.response?.data?.detail || 'Failed to delete banner', { type: 'error' });
    }
  };

  const handleEdit = (banner: Banner) => {
    setEditingBanner(banner);
    setFormData({
      title: banner.title,
      description: banner.description || '',
      link_url: banner.link_url || '',
      position: banner.position,
      status: banner.status,
      sort_order: banner.sort_order,
      start_date: banner.start_date ? banner.start_date.split('T')[0] : '',
      end_date: banner.end_date ? banner.end_date.split('T')[0] : '',
    });
    setImageFile(null);
    setImagePreview(banner.image_url);
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      link_url: '',
      position: 'home_top',
      status: 'draft',
      sort_order: 0,
      start_date: '',
      end_date: '',
    });
    setImageFile(null);
    setImagePreview(null);
    setEditingBanner(null);
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        toast.show('Please select an image file', { type: 'error' });
        return;
      }
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast.show('Image size must be less than 10MB', { type: 'error' });
        return;
      }
      setImageFile(file);
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      case 'draft': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPositionLabel = (position: string) => {
    return position.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  const filteredBanners = banners.filter(banner =>
    banner.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (banner.description && banner.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Banner Management</h1>
          <p className="text-secondary-600 mt-1">Manage promotional banners for your marketplace</p>
        </div>
        <button
          onClick={() => {
            resetForm();
            setShowModal(true);
          }}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>Create Banner</span>
        </button>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search banners..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 input-field"
            />
          </div>
          <select
            value={positionFilter}
            onChange={(e) => {
              setPositionFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="input-field"
          >
            <option value="all">All Positions</option>
            <option value="home_top">Home Top</option>
            <option value="home_middle">Home Middle</option>
            <option value="home_bottom">Home Bottom</option>
            <option value="category_top">Category Top</option>
            <option value="product_top">Product Top</option>
            <option value="cart_top">Cart Top</option>
            <option value="checkout_top">Checkout Top</option>
          </select>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="input-field"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="draft">Draft</option>
          </select>
        </div>
      </div>

      {/* Banners List */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-secondary-600">Loading banners...</p>
        </div>
      ) : filteredBanners.length === 0 ? (
        <div className="card p-12 text-center">
          <Image className="w-16 h-16 mx-auto text-secondary-400 mb-4" />
          <h3 className="text-lg font-semibold text-secondary-900 mb-2">No banners found</h3>
          <p className="text-secondary-600 mb-4">Get started by creating your first banner</p>
          <button
            onClick={() => {
              resetForm();
              setShowModal(true);
            }}
            className="btn-primary"
          >
            Create Banner
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredBanners.map((banner) => (
              <div key={banner.id} className="card overflow-hidden">
                <div className="relative">
                  <img
                    src={banner.image_url}
                    alt={banner.title}
                    className="w-full h-48 object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = '/placeholder-image.png';
                    }}
                  />
                  <div className="absolute top-2 right-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(banner.status)}`}>
                      {banner.status}
                    </span>
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-secondary-900 mb-1">{banner.title}</h3>
                  {banner.description && (
                    <p className="text-sm text-secondary-600 mb-2 line-clamp-2">{banner.description}</p>
                  )}
                  <div className="flex items-center justify-between text-xs text-secondary-500 mb-3">
                    <span>{getPositionLabel(banner.position)}</span>
                    <span>Order: {banner.sort_order}</span>
                  </div>
                  {banner.link_url && (
                    <div className="flex items-center text-xs text-primary-600 mb-3">
                      <LinkIcon className="w-3 h-3 mr-1" />
                      <span className="truncate">{banner.link_url}</span>
                    </div>
                  )}
                  <div className="flex items-center justify-between text-xs text-secondary-500 mb-4">
                    <span>Clicks: {banner.click_count}</span>
                    {banner.start_date && banner.end_date && (
                      <span className="flex items-center">
                        <Calendar className="w-3 h-3 mr-1" />
                        {new Date(banner.start_date).toLocaleDateString()} - {new Date(banner.end_date).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEdit(banner)}
                      className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 bg-primary-50 text-primary-700 rounded-lg hover:bg-primary-100 transition-colors"
                    >
                      <Edit2 className="w-4 h-4" />
                      <span className="text-sm">Edit</span>
                    </button>
                    <button
                      onClick={() => handleDelete(banner)}
                      className="flex items-center justify-center space-x-1 px-3 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
          {totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
            />
          )}
        </>
      )}

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-secondary-200">
              <h2 className="text-xl font-bold text-secondary-900">
                {editingBanner ? 'Edit Banner' : 'Create Banner'}
              </h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Title *
                </label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="input-field"
                  placeholder="Banner title"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="input-field"
                  rows={3}
                  placeholder="Banner description"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Banner Image {!editingBanner && '*'}
                </label>
                <input
                  type="file"
                  accept="image/*"
                  required={!editingBanner}
                  onChange={handleImageChange}
                  className="input-field"
                />
                <p className="text-xs text-secondary-500 mt-1">
                  {editingBanner ? 'Leave empty to keep current image' : 'Select an image file (max 10MB)'}
                </p>
                {(imagePreview || (editingBanner && !imageFile)) && (
                  <img
                    src={imagePreview || (editingBanner ? editingBanner.image_url : '')}
                    alt="Preview"
                    className="mt-2 w-full h-32 object-cover rounded-lg border border-secondary-200"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Link URL
                </label>
                <input
                  type="url"
                  value={formData.link_url}
                  onChange={(e) => setFormData({ ...formData, link_url: e.target.value })}
                  className="input-field"
                  placeholder="https://example.com (optional)"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Position *
                  </label>
                  <select
                    required
                    value={formData.position}
                    onChange={(e) => setFormData({ ...formData, position: e.target.value as Banner['position'] })}
                    className="input-field"
                  >
                    <option value="home_top">Home Top</option>
                    <option value="home_middle">Home Middle</option>
                    <option value="home_bottom">Home Bottom</option>
                    <option value="category_top">Category Top</option>
                    <option value="product_top">Product Top</option>
                    <option value="cart_top">Cart Top</option>
                    <option value="checkout_top">Checkout Top</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Status *
                  </label>
                  <select
                    required
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value as Banner['status'] })}
                    className="input-field"
                  >
                    <option value="draft">Draft</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Sort Order
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={formData.sort_order}
                    onChange={(e) => setFormData({ ...formData, sort_order: parseInt(e.target.value) || 0 })}
                    className="input-field"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    className="input-field"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                    className="input-field"
                  />
                </div>
              </div>

              <div className="flex space-x-3 pt-4 border-t border-secondary-200">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    resetForm();
                  }}
                  className="flex-1 btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" className="flex-1 btn-primary">
                  {editingBanner ? 'Update Banner' : 'Create Banner'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Banners;

