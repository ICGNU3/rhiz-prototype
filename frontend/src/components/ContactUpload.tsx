import React, { useState } from 'react';

interface ContactUploadProps {
  onUploadSuccess?: (result: any) => void;
}

interface UploadResult {
  imported: number;
  duplicates: number;
  errors: number;
  contacts: Array<{
    id: string;
    name: string;
    email: string;
    company: string;
  }>;
}

const ContactUpload: React.FC<ContactUploadProps> = ({ onUploadSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
        setError('Please select a CSV file');
        return;
      }
      setFile(selectedFile);
      setError(null);
      setResult(null);
    }
  };

  const uploadFile = async () => {
    if (!file) return;

    setIsUploading(true);
    setError(null);

    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/contacts/upload', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Upload failed');
      }

      setResult(data);
      if (onUploadSuccess) {
        onUploadSuccess(data);
      }

      // Clear file input
      setFile(null);
      const fileInput = document.getElementById('csvFile') as HTMLInputElement;
      if (fileInput) fileInput.value = '';

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="contact-upload">
      <div className="mb-4">
        <label htmlFor="csvFile" className="block text-sm font-medium text-gray-700 mb-2">
          Upload Contacts CSV
        </label>
        <input
          id="csvFile"
          type="file"
          accept=".csv"
          onChange={handleFileSelect}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
        {file && (
          <p className="mt-2 text-sm text-gray-600">
            Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
          </p>
        )}
      </div>

      {file && (
        <button
          onClick={uploadFile}
          disabled={isUploading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isUploading ? 'Uploading...' : 'Upload Contacts'}
        </button>
      )}

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {result && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <h3 className="text-green-800 font-medium mb-2">Upload Complete!</h3>
          <ul className="text-green-700 text-sm">
            <li>✅ {result.imported} contacts imported</li>
            {result.duplicates > 0 && <li>⚠️ {result.duplicates} duplicates skipped</li>}
            {result.errors > 0 && <li>❌ {result.errors} errors</li>}
          </ul>
          
          {result.contacts.length > 0 && (
            <div className="mt-3">
              <p className="text-sm font-medium text-green-800">Imported contacts:</p>
              <ul className="text-sm text-green-700 mt-1">
                {result.contacts.slice(0, 5).map((contact, index) => (
                  <li key={index}>
                    {contact.name} {contact.email && `(${contact.email})`}
                    {contact.company && ` - ${contact.company}`}
                  </li>
                ))}
                {result.contacts.length > 5 && (
                  <li className="text-green-600">...and {result.contacts.length - 5} more</li>
                )}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="mt-4 text-sm text-gray-600">
        <p>Expected CSV format: name, email, company, title, phone, linkedin, notes</p>
        <p>Download <a href="/attached_assets/sample_contacts_upload.csv" className="text-blue-600 hover:underline">sample CSV</a> for reference.</p>
      </div>
    </div>
  );
};

export default ContactUpload;