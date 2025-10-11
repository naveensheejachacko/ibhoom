import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, List, Tag } from 'lucide-react';
import { adminApi } from '../../lib/api';
import { useToast } from '../../components/Toast';

interface Attribute {
  id: string;
  name: string;
  type: 'text' | 'select' | 'multiselect' | 'number';
  is_required: boolean;
  sort_order: number;
  created_at: string;
  attribute_values: AttributeValue[];
}

interface AttributeValue {
  id: string;
  attribute_id: string;
  value: string;
  sort_order: number;
  created_at: string;
}

const Attributes: React.FC = () => {
  const [attributes, setAttributes] = useState<Attribute[]>([]);
  const toast = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [showAttributeModal, setShowAttributeModal] = useState(false);
  const [showValueModal, setShowValueModal] = useState(false);
  const [editingAttribute, setEditingAttribute] = useState<Attribute | null>(null);
  const [selectedAttribute, setSelectedAttribute] = useState<Attribute | null>(null);
  const [editingValue, setEditingValue] = useState<AttributeValue | null>(null);
  
  const [attributeFormData, setAttributeFormData] = useState({
    name: '',
    type: 'select' as 'text' | 'select' | 'multiselect' | 'number',
    is_required: false,
    sort_order: 0,
  });

  const [valueFormData, setValueFormData] = useState({
    value: '',
    sort_order: 0,
  });

  useEffect(() => {
    fetchAttributes();
  }, []);

  const fetchAttributes = async () => {
    try {
      setIsLoading(true);
      const data = await adminApi.getAttributes();
      setAttributes(data);
    } catch (error) {
      console.error('Error fetching attributes:', error);
      toast.show('Failed to load attributes', { type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAttributeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingAttribute) {
        await adminApi.updateAttribute(editingAttribute.id, attributeFormData);
        toast.show('Attribute updated successfully', { type: 'success' });
      } else {
        await adminApi.createAttribute(attributeFormData);
        toast.show('Attribute created successfully', { type: 'success' });
      }
      setShowAttributeModal(false);
      setEditingAttribute(null);
      setAttributeFormData({ name: '', type: 'select', is_required: false, sort_order: 0 });
      fetchAttributes();
    } catch (error: any) {
      console.error('Error saving attribute:', error);
      toast.show(error.response?.data?.detail || 'Failed to save attribute', { type: 'error' });
    }
  };

  const handleValueSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAttribute) return;

    try {
      if (editingValue) {
        await adminApi.updateAttributeValue(editingValue.id, valueFormData);
        toast.show('Value updated successfully', { type: 'success' });
      } else {
        await adminApi.createAttributeValue({
          ...valueFormData,
          attribute_id: selectedAttribute.id,
        });
        toast.show('Value created successfully', { type: 'success' });
      }
      setShowValueModal(false);
      setEditingValue(null);
      setValueFormData({ value: '', sort_order: 0 });
      fetchAttributes();
    } catch (error: any) {
      console.error('Error saving value:', error);
      toast.show(error.response?.data?.detail || 'Failed to save value', { type: 'error' });
    }
  };

  const handleEditAttribute = (attribute: Attribute) => {
    setEditingAttribute(attribute);
    setAttributeFormData({
      name: attribute.name,
      type: attribute.type,
      is_required: attribute.is_required,
      sort_order: attribute.sort_order,
    });
    setShowAttributeModal(true);
  };

  const handleDeleteAttribute = async (attributeId: string) => {
    if (window.confirm('Are you sure you want to delete this attribute? This will also delete all its values.')) {
      try {
        await adminApi.deleteAttribute(attributeId);
        toast.show('Attribute deleted successfully', { type: 'success' });
        fetchAttributes();
      } catch (error: any) {
        console.error('Error deleting attribute:', error);
        toast.show(error.response?.data?.detail || 'Failed to delete attribute', { type: 'error' });
      }
    }
  };

  const handleManageValues = (attribute: Attribute) => {
    setSelectedAttribute(attribute);
  };

  const handleAddValue = () => {
    setEditingValue(null);
    setValueFormData({ value: '', sort_order: 0 });
    setShowValueModal(true);
  };

  const handleEditValue = (value: AttributeValue) => {
    setEditingValue(value);
    setValueFormData({
      value: value.value,
      sort_order: value.sort_order,
    });
    setShowValueModal(true);
  };

  const handleDeleteValue = async (valueId: string) => {
    if (window.confirm('Are you sure you want to delete this value?')) {
      try {
        await adminApi.deleteAttributeValue(valueId);
        toast.show('Value deleted successfully', { type: 'success' });
        fetchAttributes();
      } catch (error: any) {
        console.error('Error deleting value:', error);
        toast.show(error.response?.data?.detail || 'Failed to delete value', { type: 'error' });
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

  if (selectedAttribute) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <button
              onClick={() => setSelectedAttribute(null)}
              className="text-primary-600 hover:text-primary-700 mb-2 flex items-center"
            >
              ← Back to Attributes
            </button>
            <h1 className="text-2xl font-bold text-secondary-900">
              Manage Values: {selectedAttribute.name}
            </h1>
            <p className="text-secondary-600">
              Add and manage values for this attribute
            </p>
          </div>
          <button
            onClick={handleAddValue}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>Add Value</span>
          </button>
        </div>

        <div className="card p-6">
          {selectedAttribute.attribute_values.length === 0 ? (
            <div className="text-center py-12">
              <Tag className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-secondary-900 mb-2">No Values</h3>
              <p className="text-secondary-600">Start by creating your first value.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {selectedAttribute.attribute_values
                .sort((a, b) => a.sort_order - b.sort_order)
                .map((value) => (
                  <div
                    key={value.id}
                    className="flex items-center justify-between p-3 border border-secondary-200 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <Tag className="w-5 h-5 text-secondary-600" />
                      <div>
                        <h4 className="font-medium text-secondary-900">{value.value}</h4>
                        <p className="text-xs text-secondary-500">Sort Order: {value.sort_order}</p>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEditValue(value)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteValue(value.id)}
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

        {/* Value Modal */}
        {showValueModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold text-secondary-900 mb-4">
                {editingValue ? 'Edit Value' : 'Add Value'}
              </h3>

              <form onSubmit={handleValueSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Value *
                  </label>
                  <input
                    type="text"
                    value={valueFormData.value}
                    onChange={(e) => setValueFormData({ ...valueFormData, value: e.target.value })}
                    className="input-field"
                    required
                    placeholder="e.g., Red, Large, 128GB"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Sort Order
                  </label>
                  <input
                    type="number"
                    value={valueFormData.sort_order}
                    onChange={(e) => setValueFormData({ ...valueFormData, sort_order: parseInt(e.target.value) })}
                    className="input-field"
                    min="0"
                  />
                </div>

                <div className="flex space-x-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowValueModal(false);
                      setEditingValue(null);
                      setValueFormData({ value: '', sort_order: 0 });
                    }}
                    className="flex-1 btn-secondary"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="flex-1 btn-primary">
                    {editingValue ? 'Update' : 'Create'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Attributes</h1>
          <p className="text-secondary-600">Manage product attributes like color, size, storage, etc.</p>
        </div>
        <button
          onClick={() => {
            setEditingAttribute(null);
            setAttributeFormData({ name: '', type: 'select', is_required: false, sort_order: 0 });
            setShowAttributeModal(true);
          }}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>Add Attribute</span>
        </button>
      </div>

      <div className="card p-6">
        {attributes.length === 0 ? (
          <div className="text-center py-12">
            <List className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-secondary-900 mb-2">No Attributes</h3>
            <p className="text-secondary-600">Start by creating your first attribute.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {attributes
              .sort((a, b) => a.sort_order - b.sort_order)
              .map((attribute) => (
                <div
                  key={attribute.id}
                  className="flex items-center justify-between p-4 border border-secondary-200 rounded-lg hover:border-secondary-300 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <List className="w-5 h-5 text-secondary-600" />
                    <div>
                      <div className="flex items-center space-x-2">
                        <h4 className="font-medium text-secondary-900">{attribute.name}</h4>
                        <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                          {attribute.type}
                        </span>
                        {attribute.is_required && (
                          <span className="text-xs px-2 py-1 bg-red-100 text-red-700 rounded">
                            Required
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-secondary-600">
                        {attribute.attribute_values.length} value(s) • Sort Order: {attribute.sort_order}
                      </p>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleManageValues(attribute)}
                      className="px-3 py-2 text-sm text-primary-600 hover:bg-primary-50 rounded-lg"
                    >
                      Manage Values
                    </button>
                    <button
                      onClick={() => handleEditAttribute(attribute)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteAttribute(attribute.id)}
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

      {/* Attribute Modal */}
      {showAttributeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">
              {editingAttribute ? 'Edit Attribute' : 'Add Attribute'}
            </h3>

            <form onSubmit={handleAttributeSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Attribute Name *
                </label>
                <input
                  type="text"
                  value={attributeFormData.name}
                  onChange={(e) => setAttributeFormData({ ...attributeFormData, name: e.target.value })}
                  className="input-field"
                  required
                  placeholder="e.g., Color, Size, Storage"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Type *
                </label>
                <select
                  value={attributeFormData.type}
                  onChange={(e) => setAttributeFormData({ ...attributeFormData, type: e.target.value as any })}
                  className="input-field"
                  required
                >
                  <option value="select">Select (dropdown)</option>
                  <option value="multiselect">Multi-Select</option>
                  <option value="text">Text Input</option>
                  <option value="number">Number</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Sort Order
                </label>
                <input
                  type="number"
                  value={attributeFormData.sort_order}
                  onChange={(e) => setAttributeFormData({ ...attributeFormData, sort_order: parseInt(e.target.value) })}
                  className="input-field"
                  min="0"
                />
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="is_required"
                  checked={attributeFormData.is_required}
                  onChange={(e) => setAttributeFormData({ ...attributeFormData, is_required: e.target.checked })}
                  className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
                />
                <label htmlFor="is_required" className="text-sm font-medium text-secondary-700">
                  Required Attribute
                </label>
              </div>

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowAttributeModal(false);
                    setEditingAttribute(null);
                    setAttributeFormData({ name: '', type: 'select', is_required: false, sort_order: 0 });
                  }}
                  className="flex-1 btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" className="flex-1 btn-primary">
                  {editingAttribute ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Attributes;

