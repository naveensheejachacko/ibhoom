import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

interface SellerLayoutProps {
  children: React.ReactNode;
}

const SellerLayout: React.FC<SellerLayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen bg-secondary-50">
      <Sidebar userRole="seller" />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title="Seller Dashboard" />
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default SellerLayout; 