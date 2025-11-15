import React from 'react';
import { Search } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import NotificationDropdown from '../Notifications/NotificationDropdown';

interface HeaderProps {
  title: string;
}

const Header: React.FC<HeaderProps> = ({ title }) => {
  const { user } = useAuth();
  const userRole = user?.role as 'admin' | 'seller';

  return (
    <header className="bg-white border-b border-secondary-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-secondary-900">{title}</h2>
          <p className="text-sm text-secondary-500">
            Welcome back, {user?.first_name || 'User'}!
          </p>
        </div>

        <div className="flex items-center space-x-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search..."
              className="pl-10 pr-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent w-64"
            />
          </div>

          {/* Notifications - Only show for admin and seller */}
          {(userRole === 'admin' || userRole === 'seller') && (
            <NotificationDropdown userRole={userRole} />
          )}

          {/* User Avatar */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
              <span className="text-white font-medium text-sm">
                {user?.first_name?.[0] || user?.email?.[0]?.toUpperCase() || 'U'}
                {user?.last_name?.[0] || ''}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 