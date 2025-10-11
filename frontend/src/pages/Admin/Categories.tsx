import React, { useState, useEffect } from 'react';
import { FolderTree, Plus, Edit2, Trash2, Settings } from 'lucide-react';
import { adminApi } from '../../lib/api';
import { useToast } from '../../components/Toast';
import { Category } from '../../types/api';

interface Attribute {
  id: string;
  name: string;
  type: string;
  is_required: boolean;
  sort_order: number;
  attribute_values: any[];
}

interface CategoryAttribute {
  id: string;
  category_id: string;
  attribute_id: string;
  is_required: boolean;
  is_variant: boolean;
  attribute: Attribute;
}

const Categories: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const toast = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    parent_id: '',
  });

  const [showAttributesModal, setShowAttributesModal] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [allAttributes, setAllAttributes] = useState<Attribute[]>([]);
  const [categoryAttributes, setCategoryAttributes] = useState<CategoryAttribute[]>([]);
  const [availableAttributes, setAvailableAttributes] = useState<Attribute[]>([]);
  const [selectedAttributeId, setSelectedAttributeId] = useState('');
  const [attributeSettings, setAttributeSettings] = useState({
    is_required: false,
    is_variant: false,
  });

  // Flatten tree for parent selector with indentation
  const flattenCategories = (nodes: Category[], depth = 0): { id: string; label: string }[] => {
    const out: { id: string; label: string }[] = [];
    nodes.forEach((n) => {
      out.push({ id: n.id, label: `${'\u00A0'.repeat(depth * 2)}${depth > 0 ? '└ ' : ''}${n.name}` });
      if ((n as any).children && (n as any).children.length > 0) {
        out.push(...flattenCategories((n as any).children, depth + 1));
      }
    });
    return out;
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  const buildTreeFromFlat = (flat: any[]): Category[] => {
    const idToNode: Record<string, any> = {};
    flat.forEach((c) => (idToNode[c.id] = { ...c, children: [] }));
    const roots: any[] = [];
    flat.forEach((c) => {
      const node = idToNode[c.id];
      const pid = (c as any).parent_id || null;
      if (pid && idToNode[pid]) {
        idToNode[pid].children.push(node);
      } else {
        roots.push(node);
      }
    });
    return roots as Category[];
  };

  const fetchCategories = async () => {
    try {
      setIsLoading(true);
      const data = await adminApi.getCategoryTree();
      if (Array.isArray(data) && data.length > 0) {
        setCategories(data);
      } else {
        // Fallback: build tree client-side from flat list
        const flat = await adminApi.getCategories();
        setCategories(buildTreeFromFlat(flat));
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
      toast.show('Failed to load categories for admin. Showing nothing.', { type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingCategory) {
        await adminApi.updateCategory(editingCategory.id, formData);
      } else {
        await adminApi.createCategory(formData);
      }
      setShowModal(false);
      setEditingCategory(null);
      setFormData({ name: '', description: '', parent_id: '' });
      fetchCategories();
    } catch (error) {
      console.error('Error saving category:', error);
    }
  };

  const handleEdit = (category: Category) => {
    setEditingCategory(category);
    setFormData({
      name: category.name,
      description: category.description || '',
      parent_id: category.parent_id || '',
    });
    setShowModal(true);
  };

  const handleDelete = async (categoryId: string) => {
    if (window.confirm('Are you sure you want to delete this category?')) {
      try {
        await adminApi.deleteCategory(categoryId);
        fetchCategories();
      } catch (error) {
        console.error('Error deleting category:', error);
      }
    }
  };

  const handleManageAttributes = async (category: Category) => {
    setSelectedCategory(category);
    try {
      const [attrs, catAttrs] = await Promise.all([
        adminApi.getAttributes(),
        adminApi.getCategoryAttributes(category.id),
      ]);
      setAllAttributes(attrs);
      setCategoryAttributes(catAttrs);
      
      // Calculate available attributes (not yet linked)
      const linkedIds = catAttrs.map((ca: CategoryAttribute) => ca.attribute_id);
      setAvailableAttributes(attrs.filter((a: Attribute) => !linkedIds.includes(a.id)));
      
      setShowAttributesModal(true);
    } catch (error) {
      console.error('Error loading attributes:', error);
      toast.show('Failed to load attributes', { type: 'error' });
    }
  };

  const handleAddCategoryAttribute = async () => {
    if (!selectedCategory || !selectedAttributeId) return;

    try {
      await adminApi.createCategoryAttribute({
        category_id: selectedCategory.id,
        attribute_id: selectedAttributeId,
        is_required: attributeSettings.is_required,
        is_variant: attributeSettings.is_variant,
      });
      toast.show('Attribute linked successfully', { type: 'success' });
      setSelectedAttributeId('');
      setAttributeSettings({ is_required: false, is_variant: false });
      
      // Refresh category attributes
      const catAttrs = await adminApi.getCategoryAttributes(selectedCategory.id);
      setCategoryAttributes(catAttrs);
      
      // Update available attributes
      const linkedIds = catAttrs.map((ca: CategoryAttribute) => ca.attribute_id);
      setAvailableAttributes(allAttributes.filter((a: Attribute) => !linkedIds.includes(a.id)));
    } catch (error: any) {
      console.error('Error adding attribute:', error);
      toast.show(error.response?.data?.detail || 'Failed to add attribute', { type: 'error' });
    }
  };

  const handleUpdateCategoryAttribute = async (categoryAttributeId: string, updates: any) => {
    try {
      await adminApi.updateCategoryAttribute(categoryAttributeId, updates);
      toast.show('Attribute settings updated', { type: 'success' });
      
      // Refresh
      if (selectedCategory) {
        const catAttrs = await adminApi.getCategoryAttributes(selectedCategory.id);
        setCategoryAttributes(catAttrs);
      }
    } catch (error: any) {
      console.error('Error updating attribute:', error);
      toast.show(error.response?.data?.detail || 'Failed to update attribute', { type: 'error' });
    }
  };

  const handleRemoveCategoryAttribute = async (categoryAttributeId: string) => {
    if (!window.confirm('Remove this attribute from the category?')) return;

    try {
      await adminApi.deleteCategoryAttribute(categoryAttributeId);
      toast.show('Attribute removed', { type: 'success' });
      
      // Refresh
      if (selectedCategory) {
        const catAttrs = await adminApi.getCategoryAttributes(selectedCategory.id);
        setCategoryAttributes(catAttrs);
        
        // Update available attributes
        const linkedIds = catAttrs.map((ca: CategoryAttribute) => ca.attribute_id);
        setAvailableAttributes(allAttributes.filter((a: Attribute) => !linkedIds.includes(a.id)));
      }
    } catch (error: any) {
      console.error('Error removing attribute:', error);
      toast.show(error.response?.data?.detail || 'Failed to remove attribute', { type: 'error' });
    }
  };

  const renderCategoryTree = (categories: Category[], level = 0) => {
    return categories.map((category) => (
      <div key={category.id} style={{ marginLeft: level * 16 }}>
        <div className="flex items-center justify-between p-3 border border-secondary-200 rounded-lg mb-2">
          <div className="flex items-center space-x-3">
            <FolderTree className="w-5 h-5 text-secondary-600" />
            <div>
              <h4 className="font-medium text-secondary-900">{category.name}</h4>
              <p className="text-sm text-secondary-600">{category.description}</p>
            </div>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => handleManageAttributes(category)}
              className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg"
              title="Manage Attributes"
            >
              <Settings className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleEdit(category)}
              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
            >
              <Edit2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleDelete(category.id)}
              className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
        {category.children && category.children.length > 0 && (
          <div className="ml-6">
            {renderCategoryTree(category.children, level + 1)}
          </div>
        )}
      </div>
    ));
  };

  // Render uses pre-built tree in `categories`

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
          <h1 className="text-2xl font-bold text-secondary-900">Categories</h1>
          <p className="text-secondary-600">Manage product categories and subcategories</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>Add Category</span>
        </button>
      </div>

      <div className="card p-6">
        {categories.length === 0 ? (
          <div className="text-center py-12">
            <FolderTree className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-secondary-900 mb-2">No Categories</h3>
            <p className="text-secondary-600">Start by creating your first category.</p>
          </div>
        ) : (
          renderCategoryTree(categories)
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">
              {editingCategory ? 'Edit Category' : 'Add Category'}
            </h3>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Category Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="input-field"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Parent Category (optional)
                </label>
                <select
                  value={formData.parent_id}
                  onChange={(e) => setFormData({ ...formData, parent_id: e.target.value })}
                  className="input-field"
                >
                  <option value="">None (create root category)</option>
                  {flattenCategories(categories).map((opt) => (
                    <option key={opt.id} value={opt.id}>{opt.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="input-field h-24 resize-none"
                />
              </div>
              
              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingCategory(null);
                    setFormData({ name: '', description: '', parent_id: '' });
                  }}
                  className="flex-1 btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" className="flex-1 btn-primary">
                  {editingCategory ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Category Attributes Modal */}
      {showAttributesModal && selectedCategory && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold text-secondary-900">
                  Manage Attributes: {selectedCategory.name}
                </h3>
                <p className="text-sm text-secondary-600 mt-1">
                  Configure which attributes are available for products in this category
                </p>
              </div>
              <button
                onClick={() => {
                  setShowAttributesModal(false);
                  setSelectedCategory(null);
                }}
                className="text-secondary-400 hover:text-secondary-600"
              >
                ✕
              </button>
            </div>

            {/* Add New Attribute */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h4 className="font-medium text-secondary-900 mb-3">Add Attribute</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <select
                    value={selectedAttributeId}
                    onChange={(e) => setSelectedAttributeId(e.target.value)}
                    className="input-field"
                  >
                    <option value="">Select an attribute...</option>
                    {availableAttributes.map((attr) => (
                      <option key={attr.id} value={attr.id}>
                        {attr.name} ({attr.type})
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="attr_required"
                    checked={attributeSettings.is_required}
                    onChange={(e) =>
                      setAttributeSettings({ ...attributeSettings, is_required: e.target.checked })
                    }
                    className="rounded border-secondary-300"
                  />
                  <label htmlFor="attr_required" className="text-sm">Required</label>
                </div>
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="attr_variant"
                    checked={attributeSettings.is_variant}
                    onChange={(e) =>
                      setAttributeSettings({ ...attributeSettings, is_variant: e.target.checked })
                    }
                    className="rounded border-secondary-300"
                  />
                  <label htmlFor="attr_variant" className="text-sm">
                    Is Variant (affects pricing/inventory)
                  </label>
                </div>
              </div>
              <button
                onClick={handleAddCategoryAttribute}
                disabled={!selectedAttributeId}
                className="btn-primary mt-3 disabled:opacity-50"
              >
                Add Attribute
              </button>
            </div>

            {/* Current Attributes */}
            <div>
              <h4 className="font-medium text-secondary-900 mb-3">Current Attributes</h4>
              {categoryAttributes.length === 0 ? (
                <p className="text-sm text-secondary-500 text-center py-8">
                  No attributes configured for this category yet
                </p>
              ) : (
                <div className="space-y-2">
                  {categoryAttributes.map((ca) => (
                    <div
                      key={ca.id}
                      className="flex items-center justify-between p-3 border border-secondary-200 rounded-lg"
                    >
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h5 className="font-medium text-secondary-900">
                            {ca.attribute?.name || 'Unknown'}
                          </h5>
                          <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                            {ca.attribute?.type}
                          </span>
                          {ca.is_required && (
                            <span className="text-xs px-2 py-1 bg-red-100 text-red-700 rounded">
                              Required
                            </span>
                          )}
                          {ca.is_variant && (
                            <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">
                              Variant
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-secondary-500 mt-1">
                          {ca.attribute?.attribute_values?.length || 0} value(s) available
                        </p>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id={`req_${ca.id}`}
                            checked={ca.is_required}
                            onChange={(e) =>
                              handleUpdateCategoryAttribute(ca.id, { is_required: e.target.checked })
                            }
                            className="rounded border-secondary-300"
                          />
                          <label htmlFor={`req_${ca.id}`} className="text-xs">Req</label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id={`var_${ca.id}`}
                            checked={ca.is_variant}
                            onChange={(e) =>
                              handleUpdateCategoryAttribute(ca.id, { is_variant: e.target.checked })
                            }
                            className="rounded border-secondary-300"
                          />
                          <label htmlFor={`var_${ca.id}`} className="text-xs">Variant</label>
                        </div>
                        <button
                          onClick={() => handleRemoveCategoryAttribute(ca.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex justify-end mt-6">
              <button
                onClick={() => {
                  setShowAttributesModal(false);
                  setSelectedCategory(null);
                }}
                className="btn-primary"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Categories; 