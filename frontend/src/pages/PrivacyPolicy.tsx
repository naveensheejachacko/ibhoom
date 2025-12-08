import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

const PrivacyPolicy: React.FC = () => {
  const location = useLocation();
  const isAdminRoute = location.pathname.startsWith('/admin/');

  return (
    <div className="min-h-screen bg-secondary-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {!isAdminRoute && (
          <Link
            to="/login"
            className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-6"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Login
          </Link>
        )}

        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-secondary-900 mb-2">
              Privacy Policy
            </h1>
            <p className="text-sm text-secondary-600">
              Last updated: December 5, 2025
            </p>
          </div>

          <div className="prose prose-sm max-w-none text-secondary-700 space-y-6">
            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">Introduction</h2>
              <p>
                Welcome to ibhoom ("we," "our," or "us"). We are committed to protecting your privacy 
                and ensuring you have a positive experience on our platform. This Privacy Policy explains how we collect, 
                use, disclose, and safeguard your information when you use ibhoom, including our website, 
                mobile application, and services (collectively, the "Service").
              </p>
              <p>
                By using our Service, you agree to the collection and use of information in accordance with this Privacy Policy. 
                If you do not agree with our policies and practices, please do not use our Service.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">1. Information We Collect</h2>
              
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">1.1 Information You Provide to Us</h3>
                  <p>We collect information that you provide directly to us, including:</p>
                  <ul className="list-disc pl-6 space-y-1 mt-2">
                    <li><strong>Account Information</strong>: Name, email address, phone number, password, and profile picture</li>
                    <li><strong>Seller Information</strong>: Business name, business type, address, city, state, pincode, GST number, PAN number, bank account details, and business documents</li>
                    <li><strong>Customer Information</strong>: Delivery address, billing address, payment information, and order history</li>
                    <li><strong>Product Information</strong>: Product details, images, descriptions, pricing, and inventory information (for sellers)</li>
                    <li><strong>Communication Data</strong>: Messages, reviews, ratings, and feedback you submit through our platform</li>
                    <li><strong>Support Data</strong>: Information you provide when contacting our customer support team</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">1.2 Information We Collect Automatically</h3>
                  <p>When you use our Service, we automatically collect certain information, including:</p>
                  <ul className="list-disc pl-6 space-y-1 mt-2">
                    <li><strong>Device Information</strong>: Device type, operating system, browser type, IP address, and device identifiers</li>
                    <li><strong>Usage Information</strong>: Pages visited, time spent on pages, links clicked, search queries, and interaction with features</li>
                    <li><strong>Location Information</strong>: General location data based on your IP address or device settings (with your permission)</li>
                    <li><strong>Log Data</strong>: Server logs, error reports, and performance data</li>
                    <li><strong>Cookies and Tracking Technologies</strong>: We use cookies, web beacons, and similar technologies to track your activity and preferences</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">1.3 Information from Third Parties</h3>
                  <p>We may receive information about you from third-party services, including:</p>
                  <ul className="list-disc pl-6 space-y-1 mt-2">
                    <li><strong>Payment Processors</strong>: Transaction details and payment method information</li>
                    <li><strong>Authentication Services</strong>: Social media account information if you choose to sign in using social media</li>
                    <li><strong>Analytics Providers</strong>: Usage statistics and user behavior data</li>
                    <li><strong>Marketing Partners</strong>: Information about your interests and preferences</li>
                  </ul>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">2. How We Use Your Information</h2>
              <p>We use the information we collect for the following purposes:</p>
              
              <div className="space-y-3 mt-3">
                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">2.1 Service Provision</h3>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>Create and manage your account</li>
                    <li>Process and fulfill your orders</li>
                    <li>Facilitate transactions between buyers and sellers</li>
                    <li>Provide customer support and respond to your inquiries</li>
                    <li>Send you service-related notifications (order updates, delivery status, etc.)</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">2.2 Communication</h3>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>Send you transactional emails (order confirmations, shipping updates)</li>
                    <li>Respond to your customer service requests</li>
                    <li>Send you marketing communications (with your consent)</li>
                    <li>Notify you about important changes to our Service or policies</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">2.3 Platform Improvement</h3>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>Analyze usage patterns to improve our Service</li>
                    <li>Develop new features and functionality</li>
                    <li>Personalize your experience</li>
                    <li>Conduct research and analytics</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">2.4 Security and Fraud Prevention</h3>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>Detect and prevent fraud, abuse, and security threats</li>
                    <li>Verify your identity</li>
                    <li>Protect the rights and safety of our users</li>
                    <li>Comply with legal obligations</li>
                  </ul>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">3. How We Share Your Information</h2>
              <p>We do not sell your personal information. We may share your information in the following circumstances:</p>
              
              <div className="space-y-3 mt-3">
                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">3.1 With Sellers (for Customers)</h3>
                  <p>
                    When you place an order, we share your name, delivery address, phone number, and order details with the seller 
                    to fulfill your order. We may share your contact information for delivery and customer service purposes.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">3.2 With Customers (for Sellers)</h3>
                  <p>
                    Your business name, contact information, and product listings are visible to customers. Customer reviews and 
                    ratings may be displayed on your seller profile.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">3.3 Service Providers</h3>
                  <p>We share information with third-party service providers who perform services on our behalf, including:</p>
                  <ul className="list-disc pl-6 space-y-1 mt-2">
                    <li>Payment processors</li>
                    <li>Shipping and logistics companies</li>
                    <li>Cloud hosting and storage providers</li>
                    <li>Analytics and marketing service providers</li>
                    <li>Customer support tools</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">3.4 Legal Requirements</h3>
                  <p>We may disclose your information if required by law or in response to:</p>
                  <ul className="list-disc pl-6 space-y-1 mt-2">
                    <li>Court orders or legal processes</li>
                    <li>Government requests</li>
                    <li>Law enforcement investigations</li>
                    <li>Protection of rights, property, or safety</li>
                  </ul>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">4. Data Security</h2>
              <p>We implement appropriate technical and organizational security measures to protect your personal information, including:</p>
              <ul className="list-disc pl-6 space-y-1 mt-2">
                <li><strong>Encryption</strong>: We use encryption (SSL/TLS) to protect data in transit</li>
                <li><strong>Secure Storage</strong>: Personal information is stored on secure servers with restricted access</li>
                <li><strong>Access Controls</strong>: We limit access to personal information to authorized personnel only</li>
                <li><strong>Regular Audits</strong>: We conduct regular security assessments and audits</li>
                <li><strong>Incident Response</strong>: We have procedures in place to respond to security incidents</li>
              </ul>
              <p className="mt-3">
                However, no method of transmission over the internet or electronic storage is 100% secure. While we strive to use 
                commercially acceptable means to protect your information, we cannot guarantee absolute security.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">5. Your Rights and Choices</h2>
              <p>You have the following rights regarding your personal information:</p>
              
              <div className="space-y-2 mt-3">
                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-1">5.1 Access and Portability</h3>
                  <p>Request access to your personal information and request a copy of your data in a portable format.</p>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-1">5.2 Correction and Updates</h3>
                  <p>Update or correct your account information through your account settings or request correction of inaccurate information.</p>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-1">5.3 Deletion</h3>
                  <p>
                    Request deletion of your account and associated data. Note: We may retain certain information as required by law 
                    or for legitimate business purposes.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-1">5.4 Opt-Out</h3>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>Unsubscribe from marketing emails using the link in the email</li>
                    <li>Adjust your notification preferences in account settings</li>
                    <li>Disable cookies through your browser settings (may affect Service functionality)</li>
                  </ul>
                </div>
              </div>
              <p className="mt-3">
                To exercise these rights, please contact us using the information provided in the "Contact Us" section below.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">6. Cookies and Tracking Technologies</h2>
              
              <div>
                <h3 className="text-lg font-medium text-secondary-900 mb-2">6.1 Types of Cookies We Use</h3>
                <ul className="list-disc pl-6 space-y-1">
                  <li><strong>Essential Cookies</strong>: Required for the Service to function properly</li>
                  <li><strong>Analytics Cookies</strong>: Help us understand how users interact with our Service</li>
                  <li><strong>Functional Cookies</strong>: Remember your preferences and settings</li>
                  <li><strong>Advertising Cookies</strong>: Used to deliver relevant advertisements (with your consent)</li>
                </ul>
              </div>

              <div className="mt-3">
                <h3 className="text-lg font-medium text-secondary-900 mb-2">6.2 Managing Cookies</h3>
                <p>
                  You can control cookies through your browser settings. However, disabling certain cookies may limit your ability 
                  to use some features of our Service.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">7. Third-Party Services</h2>
              <p>
                Our Service may contain links to third-party websites or integrate with third-party services. We are not responsible 
                for the privacy practices of these third parties. We encourage you to review their privacy policies.
              </p>
              
              <div className="mt-3">
                <h3 className="text-lg font-medium text-secondary-900 mb-2">7.1 Payment Processors</h3>
                <p>
                  When you make a purchase, your payment information is processed by third-party payment processors. We do not store 
                  your complete payment card information.
                </p>
              </div>

              <div className="mt-3">
                <h3 className="text-lg font-medium text-secondary-900 mb-2">7.2 Social Media</h3>
                <p>
                  If you choose to sign in using social media accounts, those services may collect information about you. 
                  Please review their privacy policies.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">8. Children's Privacy</h2>
              <p>
                Our Service is not intended for individuals under the age of 18. We do not knowingly collect personal information 
                from children. If you believe we have collected information from a child, please contact us immediately, and we will 
                take steps to delete such information.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">9. Data Retention</h2>
              <p>We retain your personal information for as long as necessary to:</p>
              <ul className="list-disc pl-6 space-y-1 mt-2">
                <li>Provide our Service to you</li>
                <li>Comply with legal obligations</li>
                <li>Resolve disputes</li>
                <li>Enforce our agreements</li>
              </ul>
              <p className="mt-3">
                When you delete your account, we will delete or anonymize your personal information, except where we are required 
                to retain it by law.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">10. International Data Transfers</h2>
              <p>
                Your information may be transferred to and processed in countries other than your country of residence. These countries 
                may have data protection laws that differ from those in your country. By using our Service, you consent to the transfer 
                of your information to these countries.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">11. Changes to This Privacy Policy</h2>
              <p>We may update this Privacy Policy from time to time. We will notify you of any material changes by:</p>
              <ul className="list-disc pl-6 space-y-1 mt-2">
                <li>Posting the new Privacy Policy on this page</li>
                <li>Updating the "Last Updated" date</li>
                <li>Sending you an email notification (for significant changes)</li>
                <li>Displaying a notice on our Service</li>
              </ul>
              <p className="mt-3">
                Your continued use of the Service after such changes constitutes acceptance of the updated Privacy Policy.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">12. Contact Us</h2>
              <p>If you have any questions, concerns, or requests regarding this Privacy Policy or our privacy practices, please contact us:</p>
              <div className="mt-3 space-y-1">
                <p>
                  <strong>Email</strong>:{' '}
                  <a 
                    href="mailto:ibhoomstore@gmail.com" 
                    className="text-primary-600 hover:text-primary-700 underline"
                  >
                    ibhoomstore@gmail.com
                  </a>
                </p>
              </div>
              <p className="mt-3">
                For data protection inquiries or to exercise your rights, please contact us at the email address above.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">13. Additional Information for Specific Regions</h2>
              
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">13.1 European Economic Area (EEA) Users</h3>
                  <p>If you are located in the EEA, you have additional rights under the General Data Protection Regulation (GDPR), including:</p>
                  <ul className="list-disc pl-6 space-y-1 mt-2">
                    <li>Right to erasure ("right to be forgotten")</li>
                    <li>Right to restrict processing</li>
                    <li>Right to data portability</li>
                    <li>Right to object to processing</li>
                    <li>Right to withdraw consent</li>
                  </ul>
                  <p className="mt-2">Our legal basis for processing your information includes:</p>
                  <ul className="list-disc pl-6 space-y-1 mt-2">
                    <li>Performance of a contract (providing our Service)</li>
                    <li>Legitimate interests (improving our Service, security)</li>
                    <li>Consent (marketing communications)</li>
                    <li>Legal obligations (tax, fraud prevention)</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">13.2 California Residents</h3>
                  <p>If you are a California resident, you have additional rights under the California Consumer Privacy Act (CCPA), including:</p>
                  <ul className="list-disc pl-6 space-y-1 mt-2">
                    <li>Right to know what personal information is collected</li>
                    <li>Right to delete personal information</li>
                    <li>Right to opt-out of the sale of personal information (we do not sell personal information)</li>
                    <li>Right to non-discrimination for exercising your privacy rights</li>
                  </ul>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">14. Complaints</h2>
              <p>
                If you have concerns about how we handle your personal information, you have the right to lodge a complaint with your 
                local data protection authority.
              </p>
            </section>

            <section className="pt-6 border-t border-secondary-200">
              <p className="text-sm text-secondary-600 mb-3">
                By using the ibhoom platform, you acknowledge that you have read, understood, and agree to be bound by 
                this Privacy Policy.
              </p>
              <p className="text-sm text-secondary-600">
                You may also want to review our{' '}
                <Link to="/terms" className="text-primary-600 hover:text-primary-500 underline">
                  Terms and Conditions
                </Link>
                .
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicy;

