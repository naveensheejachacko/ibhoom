import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ArrowLeft, Mail, Phone, MapPin, MessageCircle } from 'lucide-react';

const ContactUs: React.FC = () => {
  const location = useLocation();
  const isAdminRoute = location.pathname.startsWith('/admin/');
  const isSellerRoute = location.pathname.startsWith('/seller/');
  
  // WhatsApp number: +91 99475 53510 (formatted for WhatsApp link: +919947553510)
  const whatsappNumber = '+919947553510';
  const whatsappMessage = encodeURIComponent('Hello, I need help with ibhoom.');
  const whatsappUrl = `https://wa.me/${whatsappNumber.replace(/\s/g, '')}?text=${whatsappMessage}`;

  return (
    <div className="min-h-screen bg-secondary-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {!isAdminRoute && !isSellerRoute && (
          <Link
            to="/login"
            className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-6"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Login
          </Link>
        )}

        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-secondary-900 mb-4">
            Contact Us
          </h1>
          <p className="text-lg text-secondary-600 max-w-2xl mx-auto">
            We'd love to hear from you. Reach out to us via WhatsApp or email and we'll respond as soon as possible.
          </p>
        </div>

        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-semibold text-secondary-900 mb-6">
              Get in Touch
            </h2>
            
            <div className="space-y-6">
              {/* WhatsApp Contact */}
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <MessageCircle className="w-6 h-6 text-green-600" />
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">WhatsApp</h3>
                  <a 
                    href={whatsappUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-2 bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors duration-200 mb-2"
                  >
                    <MessageCircle className="w-5 h-5" />
                    <span>Chat with us on WhatsApp</span>
                  </a>
                  <p className="text-sm text-secondary-600">
                    +91 99475 53510
                  </p>
                </div>
              </div>

              {/* Email Contact */}
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Mail className="w-6 h-6 text-primary-600" />
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">Email</h3>
                  <p className="text-secondary-700 mb-3">
                    Or email us directly at{' '}
                    <a 
                      href="mailto:ibhoomstore@gmail.com" 
                      className="text-primary-600 hover:text-primary-700 font-medium underline"
                    >
                      ibhoomstore@gmail.com
                    </a>
                  </p>
                  <p className="text-sm text-secondary-600">
                    We'll respond within 24 hours
                  </p>
                </div>
              </div>

              {/* Support Hours */}
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Phone className="w-6 h-6 text-primary-600" />
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-1">Support Hours</h3>
                  <p className="text-secondary-700">
                    Monday - Friday: 9:00 AM - 6:00 PM
                  </p>
                  <p className="text-secondary-700">
                    Saturday: 10:00 AM - 4:00 PM
                  </p>
                  <p className="text-sm text-secondary-600 mt-1">
                    Closed on Sundays
                  </p>
                </div>
              </div>

              {/* Address */}
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <MapPin className="w-6 h-6 text-primary-600" />
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-1">Address</h3>
                  <p className="text-secondary-700">
                    ibhoom
                  </p>
                  <p className="text-sm text-secondary-600 mt-1">
                    Serving customers and sellers nationwide
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-8 pt-8 border-t border-secondary-200">
              <h3 className="text-lg font-medium text-secondary-900 mb-4">
                Quick Links
              </h3>
              <div className="space-y-2">
                <Link 
                  to={isAdminRoute ? "/admin/terms" : isSellerRoute ? "/seller/terms" : "/terms"} 
                  className="block text-primary-600 hover:text-primary-700 transition-colors"
                >
                  Terms and Conditions
                </Link>
                <Link 
                  to={isAdminRoute ? "/admin/privacy" : isSellerRoute ? "/seller/privacy" : "/privacy"} 
                  className="block text-primary-600 hover:text-primary-700 transition-colors"
                >
                  Privacy Policy
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactUs;

