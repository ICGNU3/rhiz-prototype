import React from 'react';
import ContactUpload from '../components/ContactUpload';

const ContactUploadTest: React.FC = () => {
  const handleUploadSuccess = (result: any) => {
    console.log('Upload successful:', result);
    // Redirect to contacts page after successful upload
    window.location.href = '/app/contacts';
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Upload Contacts</h1>
      
      <div className="bg-white shadow-sm rounded-lg p-6">
        <ContactUpload onUploadSuccess={handleUploadSuccess} />
      </div>
      
      <div className="mt-6">
        <a 
          href="/app/contacts" 
          className="text-blue-600 hover:text-blue-700 hover:underline"
        >
          ← Back to Contacts
        </a>
      </div>
    </div>
  );
};

export default ContactUploadTest;