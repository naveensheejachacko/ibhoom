import React, { useState, useEffect, useRef } from 'react';
import { Bell, X, Check, Package } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { adminApi, sellerApi } from '../../lib/api';

interface Notification {
  id: string;
  title: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  created_at: string;
  order_id?: string;
}

interface NotificationDropdownProps {
  userRole: 'admin' | 'seller';
}

const NotificationDropdown: React.FC<NotificationDropdownProps> = ({ userRole }) => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const api = userRole === 'admin' ? adminApi : sellerApi;

  // Fetch notifications
  const fetchNotifications = async () => {
    try {
      setIsLoading(true);
      const response = await api.getNotifications({ limit: 10, unread_only: false });
      if (response && response.notifications) {
        setNotifications(response.notifications);
        setUnreadCount(response.total_unread || 0);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch unread count
  const fetchUnreadCount = async () => {
    try {
      const response = await api.getUnreadCount();
      if (response && response.unread_count !== undefined) {
        setUnreadCount(response.unread_count);
      }
    } catch (error) {
      console.error('Error fetching unread count:', error);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchNotifications();
    fetchUnreadCount();

    // Poll for new notifications every 30 seconds
    const interval = setInterval(() => {
      fetchUnreadCount();
      if (isOpen) {
        fetchNotifications();
      }
    }, 30000);

    // Listen for Firebase push notifications
    const handleNotificationReceived = () => {
      fetchNotifications();
      fetchUnreadCount();
    };
    window.addEventListener('notification-received', handleNotificationReceived);

    return () => {
      clearInterval(interval);
      window.removeEventListener('notification-received', handleNotificationReceived);
    };
  }, [userRole, isOpen]);

  // Mark notification as read
  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await api.markNotificationRead(notificationId);
      setNotifications(prev =>
        prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  // Mark all as read
  const handleMarkAllAsRead = async () => {
    try {
      await api.markAllNotificationsRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  // Handle notification click
  const handleNotificationClick = (notification: Notification) => {
    if (!notification.is_read) {
      handleMarkAsRead(notification.id);
    }
    
    // Navigate to orders page if it's an order notification
    if (notification.order_id) {
      window.location.href = `/${userRole}/orders`;
    }
    
    setIsOpen(false);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  // Refresh when dropdown opens
  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen]);

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-secondary-600 hover:text-secondary-900 transition-colors duration-200"
        aria-label="Notifications"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-semibold">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-secondary-200 z-50 max-h-96 overflow-hidden flex flex-col">
          {/* Header */}
          <div className="px-4 py-3 border-b border-secondary-200 flex items-center justify-between">
            <h3 className="font-semibold text-secondary-900">Notifications</h3>
            <div className="flex items-center space-x-2">
              {unreadCount > 0 && (
                <button
                  onClick={handleMarkAllAsRead}
                  className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                >
                  Mark all read
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Notifications List */}
          <div className="overflow-y-auto flex-1">
            {isLoading ? (
              <div className="px-4 py-8 text-center text-secondary-500">
                Loading notifications...
              </div>
            ) : notifications.length === 0 ? (
              <div className="px-4 py-8 text-center text-secondary-500">
                <Package className="w-12 h-12 mx-auto mb-2 text-secondary-300" />
                <p>No notifications</p>
              </div>
            ) : (
              <div className="divide-y divide-secondary-100">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    onClick={() => handleNotificationClick(notification)}
                    className={`px-4 py-3 hover:bg-secondary-50 cursor-pointer transition-colors ${
                      !notification.is_read ? 'bg-primary-50' : ''
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`flex-shrink-0 w-2 h-2 rounded-full mt-2 ${
                        !notification.is_read ? 'bg-primary-600' : 'bg-transparent'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm font-medium ${
                          !notification.is_read ? 'text-secondary-900' : 'text-secondary-700'
                        }`}>
                          {notification.title}
                        </p>
                        <p className="text-xs text-secondary-500 mt-1 line-clamp-2">
                          {notification.message}
                        </p>
                        <p className="text-xs text-secondary-400 mt-1">
                          {formatTime(notification.created_at)}
                        </p>
                      </div>
                      {!notification.is_read && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleMarkAsRead(notification.id);
                          }}
                          className="flex-shrink-0 p-1 text-secondary-400 hover:text-primary-600"
                          aria-label="Mark as read"
                        >
                          <Check className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="px-4 py-2 border-t border-secondary-200 text-center">
              <button
                onClick={() => {
                  setIsOpen(false);
                  window.location.href = `/${userRole}/orders`;
                }}
                className="text-xs text-primary-600 hover:text-primary-700 font-medium"
              >
                View all orders
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationDropdown;

