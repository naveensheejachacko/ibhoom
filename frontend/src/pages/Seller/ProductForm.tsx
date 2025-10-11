import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Upload, X, Plus, Minus } from 'lucide-react';
import { sellerApi } from '../../lib/api';
import DynamicCategorySelector from '../../components/DynamicCategorySelector';

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

interface VariantRow {
  variant_name: string; // e.g., "Red / M" or "64 GB / Blue"
  sku: string;
  seller_price: number;
  stock_quantity: number;
  attributes: { [key: string]: string }; // attribute_id -> attribute_value_id
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
  const [variants, setVariants] = useState<VariantRow[]>([]);
  const [categoryAttributes, setCategoryAttributes] = useState<any[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedVariantAttributes, setSelectedVariantAttributes] = useState<{ [attrId: string]: string[] }>({});

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

  // Load category attributes when category changes
  useEffect(() => {
    if (formData.category_id) {
      console.log('🔍 Fetching attributes for category:', formData.category_id);
      fetch(`http://localhost:8000/api/v1/customer/categories/${formData.category_id}/attributes`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token') || ''}`
        }
      })
        .then(r => (r.ok ? r.json() : Promise.reject(r.status)))
        .then(json => {
          console.log('✅ Received attributes:', json.attributes);
          console.log('🎯 Variant attributes:', json.attributes?.filter((a: any) => a.is_variant));
          setCategoryAttributes(json.attributes || []);
        })
        .catch((err) => {
          console.error('❌ Failed to load attributes:', err);
          setCategoryAttributes([]);
        });
    } else {
      setCategoryAttributes([]);
    }
  }, [formData.category_id]);

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

  // Generate variants based on selected attribute values
  const generateVariants = () => {
    const variantAttributes = categoryAttributes.filter(attr => attr.is_variant);
    
    if (variantAttributes.length === 0 || Object.keys(selectedVariantAttributes).length === 0) {
      setVariants([]);
      return;
    }

    // Get all selected attributes with values
    const selectedAttrs = variantAttributes
      .filter(attr => selectedVariantAttributes[attr.attribute_id]?.length > 0)
      .map(attr => ({
        id: attr.attribute_id,
        name: attr.name,
        values: selectedVariantAttributes[attr.attribute_id].map(valueId => {
          const value = attr.values.find((v: any) => v.id === valueId);
          return { id: valueId, value: value?.value || '' };
        })
      }));

    if (selectedAttrs.length === 0) {
      setVariants([]);
      return;
    }

    // Generate all combinations
    const generateCombinations = (attrs: typeof selectedAttrs, index: number = 0): any[] => {
      if (index === attrs.length) {
        return [{ name: [], attributes: {} }];
      }

      const currentAttr = attrs[index];
      const restCombinations = generateCombinations(attrs, index + 1);
      const result: any[] = [];

      currentAttr.values.forEach(value => {
        restCombinations.forEach(combo => {
          result.push({
            name: [value.value, ...combo.name],
            attributes: { ...combo.attributes, [currentAttr.id]: value.id }
          });
        });
      });

      return result;
    };

    const combinations = generateCombinations(selectedAttrs);
    
    // Create variant rows
    const newVariants: VariantRow[] = combinations.map(combo => {
      const variantName = combo.name.join(' / ');
      return {
        variant_name: variantName,
        sku: `${formData.sku || 'SKU'}-${combo.name.join('-').replace(/\s+/g, '-')}`,
        seller_price: formData.seller_price || 0,
        stock_quantity: 0,
        attributes: combo.attributes
      };
    });

    setVariants(newVariants);
  };

  const handleVariantAttributeChange = (attrId: string, valueIds: string[]) => {
    setSelectedVariantAttributes(prev => ({
      ...prev,
      [attrId]: valueIds
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const productData = {
        ...formData,
        customer_price: calculateCustomerPrice(),
        tags: JSON.stringify(formData.tags),
        variants: variants.map(v => ({
          variant_name: v.variant_name,
          sku: v.sku,
          seller_price: v.seller_price,
          stock_quantity: v.stock_quantity,
          attributes: Object.keys(v.attributes || {}).map(attrId => ({
            attribute_id: attrId,
            attribute_value_id: v.attributes[attrId]
          }))
        }))
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

            <DynamicCategorySelector
              categories={categories}
              selectedCategoryId={formData.category_id}
              onCategorySelect={(categoryId) => setFormData(prev => ({ ...prev, category_id: categoryId }))}
              error={formData.category_id === '' ? 'Please select a category.' : undefined}
            />
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

        {/* Variants */}
        {categoryAttributes.filter(attr => attr.is_variant).length > 0 && (
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="text-lg font-medium text-secondary-900 mb-2">Product Variants</h3>
              <p className="text-sm text-secondary-600 mb-4">
                Select attribute values to create product variants. Variants allow different combinations like colors, sizes, storage options, etc.
              </p>

              {/* Variant Attribute Selectors */}
              <div className="space-y-4">
                {categoryAttributes
                  .filter(attr => attr.is_variant)
                  .map(attr => (
                    <div key={attr.attribute_id}>
                      <label className="block text-sm font-medium text-secondary-700 mb-2">
                        {attr.name} {attr.is_required && <span className="text-red-500">*</span>}
                      </label>
                      <div className="flex flex-wrap gap-2">
                        {attr.values.map((value: any) => {
                          const isSelected = selectedVariantAttributes[attr.attribute_id]?.includes(value.id);
                          return (
                            <button
                              key={value.id}
                              type="button"
                              onClick={() => {
                                const current = selectedVariantAttributes[attr.attribute_id] || [];
                                const newValues = isSelected
                                  ? current.filter(id => id !== value.id)
                                  : [...current, value.id];
                                handleVariantAttributeChange(attr.attribute_id, newValues);
                              }}
                              className={`px-3 py-2 rounded-lg border-2 transition-colors ${
                                isSelected
                                  ? 'border-primary-500 bg-primary-100 text-primary-800'
                                  : 'border-secondary-300 bg-white text-secondary-700 hover:border-secondary-400'
                              }`}
                            >
                              {value.value}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
              </div>

              <button
                type="button"
                onClick={generateVariants}
                className="btn-primary mt-4"
              >
                Generate Variants
              </button>
            </div>

            {/* Generated Variants Table */}
            {variants.length > 0 && (
              <div>
                <h4 className="text-md font-medium text-secondary-900 mb-3">
                  Generated Variants ({variants.length})
                </h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-secondary-200">
                    <thead className="bg-secondary-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-secondary-700 uppercase tracking-wider">
                          Variant
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-secondary-700 uppercase tracking-wider">
                          SKU
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-secondary-700 uppercase tracking-wider">
                          Your Price (₹)
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-secondary-700 uppercase tracking-wider">
                          Stock
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-secondary-700 uppercase tracking-wider">
                          Customer Price (₹)
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-secondary-200">
                      {variants.map((variant, idx) => {
                        const commission = (variant.seller_price * formData.commission_rate) / 100;
                        const customerPrice = variant.seller_price + commission;
                        
                        return (
                          <tr key={idx}>
                            <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-secondary-900">
                              {variant.variant_name}
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-secondary-600">
                              <input
                                type="text"
                                value={variant.sku}
                                onChange={e => setVariants(prev => prev.map((v, i) => i === idx ? { ...v, sku: e.target.value } : v))}
                                className="input-field w-full"
                                placeholder="SKU"
                              />
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-secondary-600">
                              <input
                                type="number"
                                min="0"
                                step="0.01"
                                value={variant.seller_price}
                                onChange={e => setVariants(prev => prev.map((v, i) => i === idx ? { ...v, seller_price: parseFloat(e.target.value || '0') } : v))}
                                className="input-field w-24"
                              />
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-secondary-600">
                              <input
                                type="number"
                                min="0"
                                value={variant.stock_quantity}
                                onChange={e => setVariants(prev => prev.map((v, i) => i === idx ? { ...v, stock_quantity: parseInt(e.target.value || '0') } : v))}
                                className="input-field w-20"
                              />
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-secondary-600">
                              ₹{customerPrice.toFixed(2)}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

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