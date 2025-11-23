import React, { useState, useEffect } from 'react';
import { Package, AlertTriangle, Search, Edit2, Save, X, RefreshCw } from 'lucide-react';
import { sellerApi } from '../../lib/api';

interface StockItem {
  product_id: string;
  product_name: string;
  product_slug: string;
  sku?: string;
  variant_id?: string;
  variant_name?: string;
  variant_sku?: string;
  stock_quantity: number;
  low_stock_threshold: number;
  is_low_stock: boolean;
  status: string;
}

const StockManagement: React.FC = () => {
  const [stockItems, setStockItems] = useState<StockItem[]>([]);
  const [filteredItems, setFilteredItems] = useState<StockItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showLowStockOnly, setShowLowStockOnly] = useState(false);
  const [editingItem, setEditingItem] = useState<string | null>(null);
  const [editValue, setEditValue] = useState<number>(0);
  const [lowStockCount, setLowStockCount] = useState(0);

  useEffect(() => {
    fetchStockInventory();
    fetchLowStockCount();
  }, []);

  useEffect(() => {
    filterItems();
  }, [stockItems, searchTerm, showLowStockOnly]);

  const fetchStockInventory = async () => {
    try {
      setIsLoading(true);
      const data = await sellerApi.getStockInventory();
      setStockItems(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching stock inventory:', error);
      setStockItems([]);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchLowStockCount = async () => {
    try {
      const data = await sellerApi.getLowStockCount();
      setLowStockCount(data.low_stock_count || 0);
    } catch (error) {
      console.error('Error fetching low stock count:', error);
    }
  };

  const filterItems = () => {
    let filtered = stockItems;

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(item =>
        item.product_name.toLowerCase().includes(term) ||
        item.variant_name?.toLowerCase().includes(term) ||
        item.variant_sku?.toLowerCase().includes(term) ||
        item.sku?.toLowerCase().includes(term)
      );
    }

    if (showLowStockOnly) {
      filtered = filtered.filter(item => item.is_low_stock);
    }

    setFilteredItems(filtered);
  };

  const handleEdit = (item: StockItem) => {
    const itemKey = item.variant_id || item.product_id;
    setEditingItem(itemKey);
    setEditValue(item.stock_quantity);
  };

  const handleSave = async (item: StockItem) => {
    try {
      if (item.variant_id) {
        await sellerApi.updateVariantStock(item.variant_id, editValue);
      } else {
        await sellerApi.updateProductStock(item.product_id, editValue);
      }
      
      // Update local state
      setStockItems(prevItems =>
        prevItems.map(i => {
          const iKey = i.variant_id || i.product_id;
          const itemKey = item.variant_id || item.product_id;
          if (iKey === itemKey) {
            return {
              ...i,
              stock_quantity: editValue,
              is_low_stock: editValue <= i.low_stock_threshold
            };
          }
          return i;
        })
      );
      
      setEditingItem(null);
      fetchLowStockCount();
    } catch (error: any) {
      console.error('Error updating stock:', error);
      alert(error.response?.data?.detail || 'Failed to update stock');
    }
  };

  const handleCancel = () => {
    setEditingItem(null);
    setEditValue(0);
  };

  const getStockStatusColor = (item: StockItem) => {
    if (item.stock_quantity === 0) return 'text-red-600 bg-red-50';
    if (item.is_low_stock) return 'text-orange-600 bg-orange-50';
    return 'text-green-600 bg-green-50';
  };

  const getStockStatusText = (item: StockItem) => {
    if (item.stock_quantity === 0) return 'Out of Stock';
    if (item.is_low_stock) return 'Low Stock';
    return 'In Stock';
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Stock Management</h1>
          <p className="text-secondary-600 mt-1">Manage inventory levels for your products</p>
        </div>
        <button
          onClick={fetchStockInventory}
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-secondary-600">Total Items</p>
              <p className="text-2xl font-bold text-secondary-900 mt-2">{stockItems.length}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Package className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-secondary-600">Low Stock Items</p>
              <p className="text-2xl font-bold text-orange-600 mt-2">{lowStockCount}</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-secondary-600">Out of Stock</p>
              <p className="text-2xl font-bold text-red-600 mt-2">
                {stockItems.filter(item => item.stock_quantity === 0).length}
              </p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <X className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-col md:flex-row md:items-center md:space-x-4 space-y-4 md:space-y-0">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search by product name, variant, or SKU..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showLowStockOnly}
              onChange={(e) => setShowLowStockOnly(e.target.checked)}
              className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-secondary-700">Show low stock only</span>
          </label>
        </div>
      </div>

      {/* Stock Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-secondary-200">
            <thead className="bg-secondary-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-700 uppercase tracking-wider">
                  Product
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-700 uppercase tracking-wider">
                  Variant/SKU
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-secondary-700 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-secondary-700 uppercase tracking-wider">
                  Stock Level
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-secondary-700 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-secondary-200">
              {filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-secondary-500">
                    No stock items found
                  </td>
                </tr>
              ) : (
                filteredItems.map((item) => {
                  const itemKey = item.variant_id || item.product_id;
                  const isEditing = editingItem === itemKey;
                  
                  return (
                    <tr key={itemKey} className="hover:bg-secondary-50">
                      <td className="px-6 py-4">
                        <div>
                          <div className="text-sm font-medium text-secondary-900">
                            {item.product_name}
                          </div>
                          <div className="text-xs text-secondary-500">
                            {item.status}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          {item.variant_name && (
                            <div className="text-sm text-secondary-900">{item.variant_name}</div>
                          )}
                          <div className="text-xs text-secondary-500">
                            SKU: {item.variant_sku || item.sku || 'N/A'}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStockStatusColor(item)}`}>
                          {getStockStatusText(item)}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-center">
                        {isEditing ? (
                          <input
                            type="number"
                            min="0"
                            value={editValue}
                            onChange={(e) => setEditValue(parseInt(e.target.value) || 0)}
                            className="w-24 px-3 py-1 border border-secondary-300 rounded-lg text-center focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            autoFocus
                          />
                        ) : (
                          <span className="text-sm font-medium text-secondary-900">
                            {item.stock_quantity} units
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-center">
                        {isEditing ? (
                          <div className="flex items-center justify-center space-x-2">
                            <button
                              onClick={() => handleSave(item)}
                              className="p-1 text-green-600 hover:bg-green-50 rounded transition-colors"
                              title="Save"
                            >
                              <Save className="w-4 h-4" />
                            </button>
                            <button
                              onClick={handleCancel}
                              className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                              title="Cancel"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => handleEdit(item)}
                            className="p-1 text-primary-600 hover:bg-primary-50 rounded transition-colors"
                            title="Edit stock"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Low Stock Alert */}
      {lowStockCount > 0 && !showLowStockOnly && (
        <div className="bg-orange-50 border-l-4 border-orange-400 p-4">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-orange-400 mr-3" />
            <div>
              <p className="text-sm font-medium text-orange-800">
                You have {lowStockCount} item{lowStockCount !== 1 ? 's' : ''} with low stock
              </p>
              <p className="text-sm text-orange-700 mt-1">
                Consider restocking soon to avoid running out of inventory.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockManagement;

