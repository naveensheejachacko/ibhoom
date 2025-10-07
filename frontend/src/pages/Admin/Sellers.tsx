import React, { useState, useEffect } from 'react';
import { UserCheck, Search, Building, MapPin, Phone, Mail, Calendar, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { adminApi } from '../../lib/api';

interface Seller {
  id: string;
  business_name: string;
  business_type: string;
  address: string;
  city: string;
  state: string;
  pincode: string;
  is_approved: boolean;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    phone: string;
    is_active: boolean;
    created_at: string;
  };
}

const Sellers: React.FC = () => {
  const [sellers, setSellers] = useState<Seller[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [approvalFilter, setApprovalFilter] = useState('');

  useEffect(() => {
    fetchSellers();
  }, []);

  const fetchSellers = async () => {
    try {
      setIsLoading(true);
      const data = await adminApi.getSellers();
      setSellers(data);
    } catch (error) {
      console.error('Error fetching sellers:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprovalToggle = async (sellerId: string, currentStatus: boolean) => {
    try {
      await adminApi.updateSellerStatus(sellerId, { is_approved: !currentStatus });
      setSellers(sellers.map(seller => 
        seller.id === sellerId ? { ...seller, is_approved: !currentStatus } : seller
      ));
    } catch (error: any) {
      console.error('Error updating seller approval:', error);
      if (error.response?.status === 404) {
        alert('Seller not found. Please refresh the page to get the latest data.');
        fetchSellers();
      } else {
        alert('Failed to update seller approval. Please try again.');
      }
    }
  };

  const handleUserStatusToggle = async (sellerId: string, currentStatus: boolean, userId?: string) => {
    try {
      const targetUserId = userId || sellers.find(s => s.id === sellerId)?.user.id;
      if (!targetUserId) throw new Error('Seller user id not found');
      await adminApi.updateUserStatus(targetUserId, { is_active: !currentStatus });
      setSellers(sellers.map(seller => 
        seller.id === sellerId ? { 
          ...seller, 
          user: { ...seller.user, is_active: !currentStatus }
        } : seller
      ));
    } catch (error: any) {
      console.error('Error updating user status:', error);
      if (error.response?.status === 404) {
        alert('Seller not found. Please refresh the page to get the latest data.');
        fetchSellers();
      } else {
        alert('Failed to update seller status. Please try again.');
      }
    }
  };

  const filteredSellers = sellers.filter(seller => {
    const matchesSearch = seller.business_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         seller.user.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         seller.user.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         seller.user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = !statusFilter || 
                         (statusFilter === 'active' && seller.user.is_active) ||
                         (statusFilter === 'inactive' && !seller.user.is_active);
    const matchesApproval = !approvalFilter || 
                           (approvalFilter === 'approved' && seller.is_approved) ||
                           (approvalFilter === 'pending' && !seller.is_approved);
    
    return matchesSearch && matchesStatus && matchesApproval;
  });

  const getApprovalColor = (isApproved: boolean) => {
    return isApproved ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800';
  };

  const getStatusColor = (isActive: boolean) => {
    return isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
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
      <div>
        <h1 className="text-2xl font-bold text-secondary-900">Seller Management</h1>
        <p className="text-secondary-600">Manage seller accounts and verifications</p>
      </div>

      {/* Filters */}
      <div className="card p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400 w-4 h-4" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-field pl-10"
                placeholder="Search sellers..."
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-field"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">Approval</label>
            <select
              value={approvalFilter}
              onChange={(e) => setApprovalFilter(e.target.value)}
              className="input-field"
            >
              <option value="">All Approval</option>
              <option value="approved">Approved</option>
              <option value="pending">Pending</option>
            </select>
          </div>
        </div>
      </div>

      {/* Sellers List */}
      <div className="card">
        <div className="p-6 border-b border-secondary-200">
          <h3 className="text-lg font-medium text-secondary-900">Sellers ({filteredSellers.length})</h3>
        </div>
        
        {filteredSellers.length === 0 ? (
          <div className="p-12 text-center">
            <UserCheck className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-secondary-900 mb-2">No Sellers Found</h3>
            <p className="text-secondary-600">No sellers match your current filters.</p>
          </div>
        ) : (
          <div className="divide-y divide-secondary-200">
            {filteredSellers.map((seller) => (
              <div key={seller.id} className="p-6 hover:bg-secondary-50">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <Building className="w-6 h-6 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-secondary-900 mb-1">
                        {seller.business_name}
                      </h4>
                      <p className="text-sm text-secondary-600 mb-2">
                        {seller.user.first_name} {seller.user.last_name} ({seller.user.email})
                      </p>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                        <div className="flex items-center text-sm text-secondary-600">
                          <Building className="w-4 h-4 mr-2" />
                          <span>{seller.business_type}</span>
                        </div>
                        <div className="flex items-center text-sm text-secondary-600">
                          <MapPin className="w-4 h-4 mr-2" />
                          <span>{seller.city}, {seller.state} - {seller.pincode}</span>
                        </div>
                        <div className="flex items-center text-sm text-secondary-600">
                          <Phone className="w-4 h-4 mr-2" />
                          <span>{seller.user.phone}</span>
                        </div>
                        <div className="flex items-center text-sm text-secondary-600">
                          <Calendar className="w-4 h-4 mr-2" />
                          <span>Joined {new Date(seller.user.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col items-end space-y-3">
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getApprovalColor(seller.is_approved)}`}>
                        {seller.is_approved ? 'Approved' : 'Pending'}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(seller.user.is_active)}`}>
                        {seller.user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleApprovalToggle(seller.id, seller.is_approved)}
                        className={`p-2 rounded-lg ${
                          seller.is_approved 
                            ? 'text-yellow-600 hover:bg-yellow-50' 
                            : 'text-green-600 hover:bg-green-50'
                        }`}
                        title={seller.is_approved ? 'Revoke Approval' : 'Approve Seller'}
                      >
                        {seller.is_approved ? <XCircle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}
                      </button>
                      
                      <button
                        onClick={() => handleUserStatusToggle(seller.id, seller.user.is_active)}
                        className={`p-2 rounded-lg ${
                          seller.user.is_active 
                            ? 'text-red-600 hover:bg-red-50' 
                            : 'text-green-600 hover:bg-green-50'
                        }`}
                        title={seller.user.is_active ? 'Deactivate Account' : 'Activate Account'}
                      >
                        {seller.user.is_active ? <XCircle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Sellers; 