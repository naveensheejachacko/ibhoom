import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

interface AdminLayoutProps {
  children: React.ReactNode;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen bg-secondary-50">
      <Sidebar userRole="admin" />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title="Admin Panel" />
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default AdminLayout; 