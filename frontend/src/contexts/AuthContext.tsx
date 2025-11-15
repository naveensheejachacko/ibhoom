import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { User, AuthContextType, LoginRequest } from '../types/auth';
import { authApi } from '../lib/api';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user && !!token;

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      try {
        const savedToken = localStorage.getItem('token');
        const savedRefreshToken = localStorage.getItem('refresh_token');
        const savedUser = localStorage.getItem('user');

        if (savedToken && savedUser) {
          setToken(savedToken);
          setUser(JSON.parse(savedUser));
          
          // Verify token is still valid
          try {
            const currentUser = await authApi.getCurrentUser();
            setUser(currentUser);
            localStorage.setItem('user', JSON.stringify(currentUser));
          } catch (error) {
            // Token might be expired, try to refresh if we have refresh token
            if (savedRefreshToken) {
              try {
                const response = await authApi.refreshToken(savedRefreshToken);
                setToken(response.access_token);
                localStorage.setItem('token', response.access_token);
                localStorage.setItem('refresh_token', response.refresh_token);
                setUser(response.user);
                localStorage.setItem('user', JSON.stringify(response.user));
              } catch (refreshError) {
                // Refresh failed, clear auth state
                logout();
              }
            } else {
              // No refresh token, clear auth state
              logout();
            }
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        logout();
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginRequest) => {
    try {
      setIsLoading(true);
      const response = await authApi.login(credentials);
      
      setToken(response.access_token);
      setUser(response.user);
      
      // Store both access and refresh tokens
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      
      // Initialize Firebase notifications after successful login
      try {
        const userRole = response.user.role as 'admin' | 'seller' | 'customer';
        if (userRole === 'admin' || userRole === 'seller') {
          const { initializeFirebaseNotifications } = await import('../lib/firebase');
          await initializeFirebaseNotifications(userRole);
        }
      } catch (firebaseError) {
        // Don't fail login if Firebase initialization fails
        console.warn('Firebase notification initialization failed:', firebaseError);
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    // Delete FCM token before logout
    try {
      const savedToken = localStorage.getItem('fcm_token');
      const savedUser = localStorage.getItem('user');
      if (savedToken && savedUser) {
        const user = JSON.parse(savedUser);
        const userRole = user.role as 'admin' | 'seller' | 'customer';
        if (userRole === 'admin' || userRole === 'seller') {
          const { deleteFCMToken } = await import('../lib/firebase');
          await deleteFCMToken(savedToken, userRole);
        }
        localStorage.removeItem('fcm_token');
      }
    } catch (error) {
      console.warn('Failed to delete FCM token on logout:', error);
    }
    
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  };

  const updateUser = (updatedUser: User) => {
    setUser(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    updateUser,
    isLoading,
    isAuthenticated,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 