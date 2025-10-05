import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Upload, X, Plus, Minus } from 'lucide-react';
import { sellerApi } from '../../lib/api';

interface ProductFormData {
  name: string;
  description: string;
  short_description: string;
  sku: string;
  seller_price: number;
  stock_quantity: number;
  commission_rate: number;
  customer_price: number;
  category_id: string;
  tags: string[];
  meta_title: string;
  meta_description: string;
  images: ProductImage[];
}

interface ProductImage {
  image_url: string;
  alt_text: string;
  sort_order: number;
}

interface Category {
  id: string;
  name: string;
  parent_id?: string;
}

const ProductForm: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [formData, setFormData] = useState<ProductFormData>({
    name: '',
    description: '',
    short_description: '',
    sku: '',
    seller_price: 0,
    stock_quantity: 0,
    commission_rate: 8,
    customer_price: 0,
    category_id: '',
    tags: [],
    meta_title: '',
    meta_description: '',
    images: []
  });

  const [categories, setCategories] = useState<Category[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    loadCategories();
    if (isEdit) {
      loadProduct();
    }
  }, [id]);

  const loadCategories = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/categories');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setCategories(data);
    } catch (error) {
      console.error('Error loading categories:', error);
      setError('Failed to load categories. Please try again.');
    }
  };

  const loadProduct = async () => {
    if (!id) return;
    
    try {
      setIsLoading(true);
      const product = await sellerApi.getProduct(id);
      setFormData({
        name: product.name || '',
        description: product.description || '',
        short_description: product.short_description || '',
        sku: product.sku || '',
        seller_price: product.seller_price || 0,
        stock_quantity: product.stock_quantity || 0,
        commission_rate: product.commission_rate || 8,
        customer_price: product.customer_price || 0,
        category_id: product.category_id || '',
        tags: product.tags ? JSON.parse(product.tags) : [],
        meta_title: product.meta_title || '',
        meta_description: product.meta_description || '',
        images: product.images || []
      });
    } catch (error) {
      console.error('Error loading product:', error);
      setError('Failed to load product details');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    // For numeric fields, remove leading zeros and parse
    if (name === 'seller_price' || name === 'commission_rate' || name === 'customer_price' || name === 'stock_quantity') {
      // Remove leading zeros from the string value, but keep '0' if the value is just zeros
      let cleanValue = value.replace(/^0+/, '');
      if (cleanValue === '' && value !== '') {
        cleanValue = '0';
      }
      
      const numericValue = parseFloat(cleanValue) || 0;
      
      setFormData(prev => ({
        ...prev,
        [name]: numericValue
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleNumericKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    const { name, value } = e.currentTarget;
    
    // Prevent typing '0' at the beginning if there's already content
    if (e.key === '0' && value === '' && (name === 'seller_price' || name === 'commission_rate' || name === 'customer_price' || name === 'stock_quantity')) {
      e.preventDefault();
    }
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tagInput.trim()]
      }));
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    Array.from(files).forEach((file) => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (event) => {
          const imageUrl = event.target?.result as string;
          const newImage: ProductImage = {
            image_url: imageUrl,
            alt_text: file.name,
            sort_order: formData.images.length
          };
          
          setFormData(prev => ({
            ...prev,
            images: [...prev.images, newImage]
          }));
        };
        reader.readAsDataURL(file);
      }
    });
  };

  const handleRemoveImage = (index: number) => {
    setFormData(prev => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== index)
    }));
  };

  const handleImageAltTextChange = (index: number, altText: string) => {
    setFormData(prev => ({
      ...prev,
      images: prev.images.map((img, i) => 
        i === index ? { ...img, alt_text: altText } : img
      )
    }));
  };

  const calculateCustomerPrice = () => {
    const commission = (formData.seller_price * formData.commission_rate) / 100;
    return formData.seller_price + commission;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const productData = {
        ...formData,
        customer_price: calculateCustomerPrice(),
        tags: JSON.stringify(formData.tags)
      };

      if (isEdit) {
        await sellerApi.updateProduct(id, productData);
        alert('Product updated successfully!');
      } else {
        await sellerApi.createProduct(productData);
        alert('Product created successfully! It will be reviewed by admin.');
      }
      
      navigate('/seller/products');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save product. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-2 text-secondary-600">Loading product...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-secondary-900">
          {isEdit ? 'Edit Product' : 'Add Product'}
        </h1>
        <p className="text-secondary-600">
          {isEdit ? 'Update product information' : 'Create a new product for approval'}
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-secondary-900">Basic Information</h3>
            
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-secondary-700 mb-2">
                Product Name *
              </label>
              <input
                id="name"
                name="name"
                type="text"
                required
                value={formData.name}
                onChange={handleInputChange}
                className="input-field"
                placeholder="Enter product name"
              />
            </div>

            <div>
              <label htmlFor="short_description" className="block text-sm font-medium text-secondary-700 mb-2">
                Short Description
              </label>
              <input
                id="short_description"
                name="short_description"
                type="text"
                value={formData.short_description}
                onChange={handleInputChange}
                className="input-field"
                placeholder="Brief product description"
              />
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-secondary-700 mb-2">
                Description *
              </label>
              <textarea
                id="description"
                name="description"
                required
                rows={4}
                value={formData.description}
                onChange={handleInputChange}
                className="input-field"
                placeholder="Detailed product description"
              />
            </div>

            <div>
              <label htmlFor="sku" className="block text-sm font-medium text-secondary-700 mb-2">
                SKU *
              </label>
              <input
                id="sku"
                name="sku"
                type="text"
                required
                value={formData.sku}
                onChange={handleInputChange}
                className="input-field"
                placeholder="Product SKU"
              />
            </div>

            <div>
              <label htmlFor="category_id" className="block text-sm font-medium text-secondary-700 mb-2">
                Category *
              </label>
              <select
                id="category_id"
                name="category_id"
                required
                value={formData.category_id}
                onChange={handleInputChange}
                className="input-field"
              >
                <option value="">Select a category</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Pricing Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-secondary-900">Pricing Information</h3>
            
            <div>
              <label htmlFor="seller_price" className="block text-sm font-medium text-secondary-700 mb-2">
                Your Price (₹) *
              </label>
              <input
                id="seller_price"
                name="seller_price"
                type="number"
                step="0.01"
                min="0"
                required
                value={formData.seller_price}
                onChange={handleInputChange}
                onKeyDown={handleNumericKeyDown}
                className="input-field"
                placeholder="0.00"
              />
            </div>

            <div>
              <label htmlFor="stock_quantity" className="block text-sm font-medium text-secondary-700 mb-2">
                Stock Quantity *
              </label>
              <input
                id="stock_quantity"
                name="stock_quantity"
                type="number"
                min="0"
                required
                value={formData.stock_quantity}
                onChange={handleInputChange}
                onKeyDown={handleNumericKeyDown}
                className="input-field"
                placeholder="0"
              />
            </div>

            <div>
              <label htmlFor="commission_rate" className="block text-sm font-medium text-secondary-700 mb-2">
                Commission Rate (%)
              </label>
              <input
                id="commission_rate"
                name="commission_rate"
                type="number"
                step="0.01"
                min="0"
                max="30"
                value={formData.commission_rate}
                onChange={handleInputChange}
                onKeyDown={handleNumericKeyDown}
                className="input-field"
                placeholder="8.00"
              />
            </div>

            <div className="bg-secondary-50 p-4 rounded-lg">
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Customer Price (₹)
              </label>
              <div className="text-lg font-semibold text-secondary-900">
                ₹{calculateCustomerPrice().toFixed(2)}
              </div>
              <p className="text-sm text-secondary-600 mt-1">
                Commission: ₹{((formData.seller_price * formData.commission_rate) / 100).toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        {/* Tags */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-secondary-900">Tags</h3>
          
          <div className="flex gap-2">
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
              className="input-field flex-1"
              placeholder="Add a tag"
            />
            <button
              type="button"
              onClick={handleAddTag}
              className="btn-secondary"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>

          {formData.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {formData.tags.map((tag, index) => (
                <span
                  key={index}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm"
                >
                  {tag}
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(tag)}
                    className="hover:text-primary-600"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Product Images */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-secondary-900">Product Images</h3>
          
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Upload Images
            </label>
            <div className="border-2 border-dashed border-secondary-300 rounded-lg p-6 text-center">
              <input
                type="file"
                multiple
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
                id="image-upload"
              />
              <label
                htmlFor="image-upload"
                className="cursor-pointer flex flex-col items-center space-y-2"
              >
                <Upload className="w-8 h-8 text-secondary-400" />
                <span className="text-sm text-secondary-600">
                  Click to upload images or drag and drop
                </span>
                <span className="text-xs text-secondary-500">
                  PNG, JPG, GIF up to 10MB each
                </span>
              </label>
            </div>
          </div>

          {formData.images.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {formData.images.map((image, index) => (
                <div key={index} className="relative group">
                  <img
                    src={image.image_url}
                    alt={image.alt_text}
                    className="w-full h-32 object-cover rounded-lg border"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveImage(index)}
                    className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-4 h-4" />
                  </button>
                  <div className="mt-2">
                    <input
                      type="text"
                      value={image.alt_text}
                      onChange={(e) => handleImageAltTextChange(index, e.target.value)}
                      placeholder="Alt text for image"
                      className="w-full text-xs px-2 py-1 border rounded"
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* SEO Information */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-secondary-900">SEO Information</h3>
          
          <div>
            <label htmlFor="meta_title" className="block text-sm font-medium text-secondary-700 mb-2">
              Meta Title
            </label>
            <input
              id="meta_title"
              name="meta_title"
              type="text"
              value={formData.meta_title}
              onChange={handleInputChange}
              className="input-field"
              placeholder="SEO title for search engines"
            />
      </div>

          <div>
            <label htmlFor="meta_description" className="block text-sm font-medium text-secondary-700 mb-2">
              Meta Description
            </label>
            <textarea
              id="meta_description"
              name="meta_description"
              rows={3}
              value={formData.meta_description}
              onChange={handleInputChange}
              className="input-field"
              placeholder="SEO description for search engines"
            />
      </div>
        </div>

        {/* Submit Buttons */}
        <div className="flex gap-4 pt-6 border-t">
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Saving...' : (isEdit ? 'Update Product' : 'Create Product')}
          </button>
          
          <button
            type="button"
            onClick={() => navigate('/seller/products')}
            className="btn-secondary"
          >
            Cancel
          </button>
      </div>
      </form>
    </div>
  );
};

export default ProductForm; 