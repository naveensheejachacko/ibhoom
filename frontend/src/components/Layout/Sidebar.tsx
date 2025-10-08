import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Package, 
  Users, 
  ShoppingCart, 
  Settings, 
  LogOut,
  FolderTree,
  Percent,
  UserCheck,
  PackageCheck,
  User
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface SidebarProps {
  userRole: 'admin' | 'seller';
}

const Sidebar: React.FC<SidebarProps> = ({ userRole }) => {
  const { logout, user } = useAuth();

  const adminNavItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/admin' },
    { icon: FolderTree, label: 'Categories', path: '/admin/categories' },
    { icon: PackageCheck, label: 'Product Approvals', path: '/admin/products' },
    { icon: ShoppingCart, label: 'Orders', path: '/admin/orders' },
    { icon: Users, label: 'Users', path: '/admin/users' },
    { icon: UserCheck, label: 'Sellers', path: '/admin/sellers' },
    { icon: Percent, label: 'Commissions', path: '/admin/commissions' },
    { icon: Settings, label: 'Settings', path: '/admin/settings' },
  ];

  const sellerNavItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/seller' },
    { icon: Package, label: 'My Products', path: '/seller/products' },
    { icon: PackageCheck, label: 'Add Product', path: '/seller/products/new' },
    { icon: User, label: 'Profile', path: '/seller/profile' },
    { icon: Settings, label: 'Settings', path: '/seller/settings' },
  ];

  const navItems = userRole === 'admin' ? adminNavItems : sellerNavItems;

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <div className="w-64 bg-white border-r border-secondary-200 min-h-screen">
      <div className="p-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center">
            <img src="/ibhoom-logo.png" alt="ibhoom logo" className="w-10 h-10 object-contain" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-secondary-900">Local Vendor</h1>
            <p className="text-xs text-secondary-500 capitalize">{userRole} Panel</p>
          </div>
        </div>
      </div>

      <nav className="px-4 pb-4">
        <div className="space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? 'active' : ''}`
              }
              end={item.path === `/admin` || item.path === `/seller`}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          ))}
        </div>

        <div className="mt-8 pt-8 border-t border-secondary-200">
          <div className="px-3 py-2">
            <p className="text-sm font-medium text-secondary-900">
              {user?.first_name} {user?.last_name}
            </p>
            <p className="text-xs text-secondary-500">{user?.email}</p>
          </div>
          
          <button
            onClick={handleLogout}
            className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-red-600 hover:bg-red-50 transition-colors duration-200"
          >
            <LogOut className="w-5 h-5" />
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </nav>
    </div>
  );
};

export default Sidebar; 