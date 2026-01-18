/**
 * Knowledge Base Page - Light Theme
 * Manage documents and knowledge for AI agents
 */
"use client";

import * as React from "react";
import {
    Database,
    Plus,
    Search,
    Upload,
    FileText,
    Trash2,
    Eye,
    Download,
    CheckCircle,
    AlertCircle,
    Loader2,
    X,
} from "lucide-react";

// Mock knowledge base data
const mockDocuments = [
    {
        id: "doc-1",
        ragId: "RAG_abc123",
        filename: "Product Catalog 2025.pdf",
        uploadedOn: "2025-01-10",
        status: "processed",
    },
    {
        id: "doc-2",
        ragId: "RAG_def456",
        filename: "FAQ Document.pdf",
        uploadedOn: "2025-01-09",
        status: "processing",
    },
    {
        id: "doc-3",
        ragId: "RAG_ghi789",
        filename: "Company Overview.pdf",
        uploadedOn: "2025-01-08",
        status: "processed",
    },
];

export default function KnowledgeBasePage() {
    const [documents] = React.useState(mockDocuments);
    const [search, setSearch] = React.useState("");
    const [showUploadModal, setShowUploadModal] = React.useState(false);

    const getStatusBadge = (status: string) => {
        switch (status) {
            case "processed":
                return (
                    <span className="flex items-center gap-1 px-2 py-1 text-xs font-medium bg-emerald-100 text-emerald-700 rounded-full">
                        <CheckCircle className="w-3 h-3" />
                        Processed
                    </span>
                );
            case "processing":
                return (
                    <span className="flex items-center gap-1 px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
                        <Loader2 className="w-3 h-3 animate-spin" />
                        Processing
                    </span>
                );
            case "failed":
                return (
                    <span className="flex items-center gap-1 px-2 py-1 text-xs font-medium bg-red-100 text-red-700 rounded-full">
                        <AlertCircle className="w-3 h-3" />
                        Failed
                    </span>
                );
            default:
                return null;
        }
    };

    return (
        <div className="max-w-full">
            {/* Page Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-xl font-semibold text-gray-900">Knowledge Base</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Upload documents to enhance your AI agents with custom knowledge
                    </p>
                </div>
                <button
                    onClick={() => setShowUploadModal(true)}
                    className="flex items-center gap-2 px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                >
                    <Upload className="w-4 h-4" />
                    Upload PDF
                </button>
            </div>

            {/* Search */}
            <div className="relative max-w-sm mb-6">
                <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none" style={{ paddingLeft: '14px' }}>
                    <Search className="w-4 h-4 text-gray-400" />
                </div>
                <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search documents..."
                    style={{ paddingLeft: '40px' }}
                    className="w-full pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 hover:border-gray-300 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 focus:bg-white transition-all duration-200"
                />
            </div>




            {/* Documents Table */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <table className="w-full">
                    <thead>
                        <tr className="bg-gray-50 border-b border-gray-200">
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">RAG ID</th>
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Filename</th>
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Uploaded on</th>
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Status</th>
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Delete</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {documents.map((doc) => (
                            <tr key={doc.id} className="hover:bg-gray-50 transition-colors">
                                <td className="px-4 py-3">
                                    <span className="font-mono text-sm text-gray-600">{doc.ragId}</span>
                                </td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-2">
                                        <FileText className="w-4 h-4 text-blue-600" />
                                        <span className="text-sm text-gray-900">{doc.filename}</span>
                                    </div>
                                </td>
                                <td className="px-4 py-3 text-sm text-gray-600">{doc.uploadedOn}</td>
                                <td className="px-4 py-3">{getStatusBadge(doc.status)}</td>
                                <td className="px-4 py-3">
                                    <button className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded">
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {documents.length === 0 && (
                    <div className="text-center py-16">
                        <Database className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                        <p className="text-sm text-gray-600">No documents uploaded yet</p>
                        <p className="text-xs text-gray-400 mt-1">Upload PDFs to enhance your agents</p>
                    </div>
                )}
            </div>

            {/* Upload Modal */}
            {showUploadModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-xl max-w-md w-full">
                        <div className="flex items-center justify-between p-4 border-b border-gray-200">
                            <h3 className="text-lg font-semibold text-gray-900">Upload Document</h3>
                            <button onClick={() => setShowUploadModal(false)} className="text-gray-400 hover:text-gray-600">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-4">
                            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors cursor-pointer">
                                <Upload className="w-10 h-10 mx-auto mb-3 text-gray-400" />
                                <p className="text-sm text-gray-600 mb-1">Drop your PDF here or click to browse</p>
                                <p className="text-xs text-gray-400">Maximum file size: 10MB</p>
                            </div>
                        </div>
                        <div className="flex justify-end gap-3 p-4 border-t border-gray-200">
                            <button onClick={() => setShowUploadModal(false)} className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
                                Cancel
                            </button>
                            <button className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg">
                                Upload
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
