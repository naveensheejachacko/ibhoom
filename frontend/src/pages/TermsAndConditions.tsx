import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

const TermsAndConditions: React.FC = () => {
  return (
    <div className="min-h-screen bg-secondary-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <Link
          to="/login"
          className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-6"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Login
        </Link>

        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-secondary-900 mb-2">
              Terms and Conditions
            </h1>
            <p className="text-sm text-secondary-600">
              Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
          </div>

          <div className="prose prose-sm max-w-none text-secondary-700 space-y-6">
            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">1. Acceptance of Terms</h2>
              <p>
                By accessing and using the ibhoom marketplace platform ("Platform"), you agree to be bound by these Terms and Conditions ("Terms"). 
                If you do not agree to these Terms, please do not use our Platform. These Terms apply to all users, including sellers, customers, 
                and administrators.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">2. Platform Description</h2>
              <p>
                ibhoom is a local vendor marketplace platform that connects sellers with customers. The Platform facilitates transactions between 
                sellers and customers but is not a party to any transaction. We provide the technology and services to enable these transactions.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">3. User Accounts</h2>
              <div className="space-y-3">
                <h3 className="text-lg font-medium text-secondary-900">3.1 Account Registration</h3>
                <p>
                  To use certain features of the Platform, you must register for an account. You agree to:
                </p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Provide accurate, current, and complete information during registration</li>
                  <li>Maintain and update your information to keep it accurate, current, and complete</li>
                  <li>Maintain the security of your password and identification</li>
                  <li>Accept all responsibility for activities that occur under your account</li>
                  <li>Notify us immediately of any unauthorized use of your account</li>
                </ul>

                <h3 className="text-lg font-medium text-secondary-900 mt-4">3.2 Seller Accounts</h3>
                <p>
                  Seller accounts require approval from the Platform administrators. We reserve the right to approve or reject any seller 
                  registration at our sole discretion. Approved sellers must comply with all Platform policies and guidelines.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">4. Seller Responsibilities</h2>
              <p>Sellers agree to:</p>
              <ul className="list-disc pl-6 space-y-1">
                <li>Provide accurate product descriptions, images, and pricing information</li>
                <li>Maintain adequate stock levels and update inventory in real-time</li>
                <li>Fulfill orders in a timely manner and as described</li>
                <li>Handle customer inquiries and complaints professionally</li>
                <li>Comply with all applicable laws and regulations</li>
                <li>Pay all applicable commissions and fees as agreed</li>
                <li>Not engage in fraudulent, deceptive, or illegal activities</li>
                <li>Not list prohibited items or services</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">5. Customer Responsibilities</h2>
              <p>Customers agree to:</p>
              <ul className="list-disc pl-6 space-y-1">
                <li>Provide accurate shipping and billing information</li>
                <li>Pay for orders in a timely manner</li>
                <li>Review product information carefully before purchasing</li>
                <li>Contact sellers directly for order-related inquiries</li>
                <li>Not engage in fraudulent activities or chargebacks without valid reason</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">6. Commissions and Fees</h2>
              <p>
                The Platform charges commissions on sales made through the marketplace. Commission rates are set by the Platform administrators 
                and may vary. Sellers will be notified of applicable commission rates. All fees are non-refundable unless otherwise stated.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">7. Product Listings</h2>
              <div className="space-y-3">
                <p>
                  Sellers are responsible for the accuracy of their product listings. The Platform reserves the right to:
                </p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Review and approve or reject product listings</li>
                  <li>Remove listings that violate our policies</li>
                  <li>Require sellers to modify listings for compliance</li>
                  <li>Suspend or terminate accounts that repeatedly violate policies</li>
                </ul>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">8. Orders and Transactions</h2>
              <p>
                All orders are subject to acceptance by the seller. The Platform facilitates transactions but is not responsible for:
              </p>
              <ul className="list-disc pl-6 space-y-1">
                <li>Product quality, safety, or legality</li>
                <li>Accuracy of product descriptions or images</li>
                <li>Seller's ability to complete a transaction</li>
                <li>Customer's ability to pay for items</li>
                <li>Disputes between sellers and customers</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">9. Prohibited Activities</h2>
              <p>Users are prohibited from:</p>
              <ul className="list-disc pl-6 space-y-1">
                <li>Using the Platform for any illegal purpose</li>
                <li>Violating any applicable laws or regulations</li>
                <li>Infringing on intellectual property rights</li>
                <li>Posting false, misleading, or fraudulent information</li>
                <li>Interfering with or disrupting the Platform's operation</li>
                <li>Attempting to gain unauthorized access to the Platform</li>
                <li>Using automated systems to access the Platform without permission</li>
                <li>Harassing, threatening, or abusing other users</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">10. Intellectual Property</h2>
              <p>
                All content on the Platform, including but not limited to text, graphics, logos, images, and software, is the property of 
                ibhoom or its content suppliers and is protected by copyright and other intellectual property laws. Users may not reproduce, 
                distribute, or create derivative works without express written permission.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">11. Privacy</h2>
              <p>
                Your use of the Platform is also governed by our Privacy Policy. By using the Platform, you consent to the collection and 
                use of your information as described in the Privacy Policy.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">12. Dispute Resolution</h2>
              <p>
                In the event of disputes between sellers and customers, the Platform may provide assistance but is not obligated to resolve 
                disputes. Users are encouraged to resolve disputes directly. The Platform reserves the right to suspend or terminate accounts 
                involved in disputes that violate these Terms.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">13. Limitation of Liability</h2>
              <p>
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, THE PLATFORM IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, 
                EITHER EXPRESS OR IMPLIED. WE DO NOT WARRANT THAT THE PLATFORM WILL BE UNINTERRUPTED, SECURE, OR ERROR-FREE. WE SHALL NOT BE 
                LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING OUT OF YOUR USE OF THE PLATFORM.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">14. Account Termination</h2>
              <p>
                We reserve the right to suspend or terminate your account at any time, with or without notice, for any reason, including but 
                not limited to violation of these Terms. Upon termination, your right to use the Platform will immediately cease.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">15. Changes to Terms</h2>
              <p>
                We reserve the right to modify these Terms at any time. We will notify users of material changes by posting the updated Terms 
                on the Platform. Your continued use of the Platform after such changes constitutes acceptance of the modified Terms.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">16. Governing Law</h2>
              <p>
                These Terms shall be governed by and construed in accordance with applicable local laws. Any disputes arising from these Terms 
                or your use of the Platform shall be subject to the exclusive jurisdiction of the courts in the applicable jurisdiction.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-secondary-900 mb-3">17. Contact Information</h2>
              <p>
                If you have any questions about these Terms and Conditions, please contact us through the Platform's support channels.
              </p>
            </section>

            <section className="pt-6 border-t border-secondary-200">
              <p className="text-sm text-secondary-600">
                By using the ibhoom marketplace platform, you acknowledge that you have read, understood, and agree to be bound by these 
                Terms and Conditions.
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TermsAndConditions;


