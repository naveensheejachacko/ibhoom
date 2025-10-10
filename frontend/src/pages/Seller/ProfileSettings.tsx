import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { User, Camera, Eye, EyeOff, Save, X } from 'lucide-react';
import { sellerApi } from '../../lib/api';

interface ProfileData {
  first_name: string;
  last_name: string;
  email: string;
  pincode: string;
  profile_picture?: string;
}

const ProfileSettings: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [profileData, setProfileData] = useState<ProfileData>({
    first_name: '',
    last_name: '',
    email: '',
    pincode: '',
    profile_picture: ''
  });
  
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [profileImage, setProfileImage] = useState<File | null>(null);
  const [profileImagePreview, setProfileImagePreview] = useState<string>('');

  useEffect(() => {
    // Initialize profile data from user context
    if (user) {
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        pincode: user.pincode || '',
        profile_picture: user.profile_picture || ''
      });
      
      if (user.profile_picture) {
        // Convert relative path to full URL
        const fullImageUrl = user.profile_picture.startsWith('http') 
          ? user.profile_picture 
          : `http://localhost:8000/${user.profile_picture}`;
        setProfileImagePreview(fullImageUrl);
      }
    }
  }, [user]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setProfileImage(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setProfileImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setProfileImage(null);
    setProfileImagePreview('');
  };

  const refreshProfile = async () => {
    try {
      const profileData = await sellerApi.getProfile();
      if (profileData) {
        setProfileData({
          first_name: profileData.first_name || '',
          last_name: profileData.last_name || '',
          email: profileData.email || '',
          pincode: profileData.pincode || '',
          profile_picture: profileData.profile_picture || ''
        });
        
        if (profileData.profile_picture) {
          const fullImageUrl = profileData.profile_picture.startsWith('http') 
            ? profileData.profile_picture 
            : `http://localhost:8000/${profileData.profile_picture}`;
          setProfileImagePreview(fullImageUrl);
        } else {
          setProfileImagePreview('');
        }
        
        // Update user context with the fresh data
        updateUser(profileData);
      }
    } catch (error) {
      console.error('Failed to refresh profile:', error);
    }
  };

  const validateForm = () => {
    if (!profileData.first_name.trim()) {
      setError('First name is required');
      return false;
    }
    if (!profileData.last_name.trim()) {
      setError('Last name is required');
      return false;
    }
    if (!profileData.email.trim()) {
      setError('Email is required');
      return false;
    }
    if (!profileData.pincode.trim()) {
      setError('Pincode is required');
      return false;
    }
    if (profileData.pincode.length !== 6) {
      setError('Pincode must be 6 digits');
      return false;
    }
    return true;
  };

  const validatePasswordForm = () => {
    if (passwordData.current_password && !passwordData.new_password) {
      setError('New password is required when changing password');
      return false;
    }
    if (passwordData.new_password && passwordData.new_password.length < 6) {
      setError('New password must be at least 6 characters');
      return false;
    }
    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('New passwords do not match');
      return false;
    }
    return true;
  };

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!validateForm()) return;

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('first_name', profileData.first_name);
      formData.append('last_name', profileData.last_name);
      formData.append('email', profileData.email);
      formData.append('pincode', profileData.pincode);
      
      if (profileImage) {
        formData.append('profile_picture', profileImage);
      }

      const response = await sellerApi.updateProfile(formData);
      
      if (response.data) {
        // Convert profile picture path to full URL if needed
        const updatedUser = {
          ...response.data,
          profile_picture: response.data.profile_picture 
            ? (response.data.profile_picture.startsWith('http') 
                ? response.data.profile_picture 
                : `http://localhost:8000/${response.data.profile_picture}`)
            : response.data.profile_picture
        };
        
        // Update local state
        setProfileData({
          first_name: updatedUser.first_name || '',
          last_name: updatedUser.last_name || '',
          email: updatedUser.email || '',
          pincode: updatedUser.pincode || '',
          profile_picture: updatedUser.profile_picture || ''
        });
        
        // Update profile image preview
        if (updatedUser.profile_picture) {
          setProfileImagePreview(updatedUser.profile_picture);
        }
        
        // Update user context
        updateUser(updatedUser);
        setSuccess('Profile updated successfully');
        setProfileImage(null);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!validatePasswordForm()) return;

    setIsLoading(true);
    try {
      await sellerApi.updatePassword({
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      });
      
      setSuccess('Password updated successfully');
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-secondary-200">
        <div className="px-6 py-4 border-b border-secondary-200">
          <h1 className="text-2xl font-bold text-secondary-900">Profile Settings</h1>
          <p className="text-sm text-secondary-600 mt-1">Manage your account information and preferences</p>
        </div>

        <div className="p-6 space-y-8">
          {/* Profile Picture Section */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-secondary-900">Profile Picture</h2>
            <div className="flex items-center space-x-6">
              <div className="relative">
                <div className="w-24 h-24 rounded-full bg-secondary-100 flex items-center justify-center overflow-hidden">
                  {profileImagePreview ? (
                    <img 
                      src={profileImagePreview} 
                      alt="Profile" 
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <User className="w-8 h-8 text-secondary-400" />
                  )}
                </div>
                {profileImagePreview && (
                  <button
                    type="button"
                    onClick={removeImage}
                    className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </div>
              <div className="space-y-2">
                <label className="block">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    className="hidden"
                    id="profile-image"
                  />
                  <span className="btn-secondary cursor-pointer inline-flex items-center space-x-2">
                    <Camera className="w-4 h-4" />
                    <span>Choose Image</span>
                  </span>
                </label>
                <p className="text-xs text-secondary-500">JPG, PNG up to 2MB</p>
              </div>
            </div>
          </div>

          {/* Profile Information Form */}
          <form onSubmit={handleProfileUpdate} className="space-y-6">
            <h2 className="text-lg font-semibold text-secondary-900">Personal Information</h2>
            
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}
            
            {success && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                {success}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium text-secondary-700 mb-2">
                  First Name *
                </label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={profileData.first_name}
                  onChange={handleInputChange}
                  className="input-field"
                  placeholder="Enter your first name"
                  required
                />
              </div>

              <div>
                <label htmlFor="last_name" className="block text-sm font-medium text-secondary-700 mb-2">
                  Last Name *
                </label>
                <input
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={profileData.last_name}
                  onChange={handleInputChange}
                  className="input-field"
                  placeholder="Enter your last name"
                  required
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-secondary-700 mb-2">
                  Email Address *
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={profileData.email}
                  onChange={handleInputChange}
                  className="input-field"
                  placeholder="Enter your email"
                  required
                />
              </div>

              <div>
                <label htmlFor="pincode" className="block text-sm font-medium text-secondary-700 mb-2">
                  Pincode *
                </label>
                <input
                  type="text"
                  id="pincode"
                  name="pincode"
                  value={profileData.pincode}
                  onChange={handleInputChange}
                  className="input-field"
                  placeholder="Enter 6-digit pincode"
                  maxLength={6}
                  pattern="[0-9]{6}"
                  required
                />
              </div>
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <Save className="w-4 h-4" />
                <span>{isLoading ? 'Updating...' : 'Update Profile'}</span>
              </button>
            </div>
          </form>

          {/* Password Change Form */}
          <div className="border-t border-secondary-200 pt-8">
            <form onSubmit={handlePasswordUpdate} className="space-y-6">
              <h2 className="text-lg font-semibold text-secondary-900">Change Password</h2>
              
              <div className="space-y-4">
                <div>
                  <label htmlFor="current_password" className="block text-sm font-medium text-secondary-700 mb-2">
                    Current Password
                  </label>
                  <div className="relative">
                    <input
                      type={showCurrentPassword ? 'text' : 'password'}
                      id="current_password"
                      name="current_password"
                      value={passwordData.current_password}
                      onChange={handlePasswordChange}
                      className="input-field pr-10"
                      placeholder="Enter current password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-secondary-400 hover:text-secondary-600"
                    >
                      {showCurrentPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                <div>
                  <label htmlFor="new_password" className="block text-sm font-medium text-secondary-700 mb-2">
                    New Password
                  </label>
                  <div className="relative">
                    <input
                      type={showNewPassword ? 'text' : 'password'}
                      id="new_password"
                      name="new_password"
                      value={passwordData.new_password}
                      onChange={handlePasswordChange}
                      className="input-field pr-10"
                      placeholder="Enter new password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-secondary-400 hover:text-secondary-600"
                    >
                      {showNewPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                <div>
                  <label htmlFor="confirm_password" className="block text-sm font-medium text-secondary-700 mb-2">
                    Confirm New Password
                  </label>
                  <div className="relative">
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      id="confirm_password"
                      name="confirm_password"
                      value={passwordData.confirm_password}
                      onChange={handlePasswordChange}
                      className="input-field pr-10"
                      placeholder="Confirm new password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-secondary-400 hover:text-secondary-600"
                    >
                      {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={isLoading || (!passwordData.current_password && !passwordData.new_password)}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  <Save className="w-4 h-4" />
                  <span>{isLoading ? 'Updating...' : 'Update Password'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileSettings;
