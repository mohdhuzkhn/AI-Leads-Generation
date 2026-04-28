"use client";
import { X, Mail, User, Building2, Send } from "lucide-react";

export interface Draft {
  to?: string;
  subject?: string;
  body?: string;
  lead_name?: string;
  company_name?: string;
}

interface DraftModalProps {
  draft: Draft | null;
  onClose: () => void;
}

export default function DraftModal({ draft, onClose }: DraftModalProps) {
  if (!draft) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative z-10 w-full max-w-2xl glass rounded-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-gradient-to-r from-indigo-500/10 to-purple-500/10">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center">
              <Mail size={16} className="text-indigo-400" />
            </div>
            <div>
              <p className="text-xs text-gray-400 font-medium">EMAIL DRAFT</p>
              <p className="text-sm text-white font-semibold">{draft.company_name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Email meta */}
        <div className="px-6 pt-4 space-y-2">
          <div className="flex items-center gap-2 text-sm">
            <User size={13} className="text-gray-500" />
            <span className="text-gray-500 w-12">To:</span>
            <span className="text-indigo-400">{draft.to || "—"}</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Building2 size={13} className="text-gray-500" />
            <span className="text-gray-500 w-12">Subj:</span>
            <span className="text-white font-medium">{draft.subject}</span>
          </div>
        </div>

        {/* Divider */}
        <div className="mx-6 my-3 border-t border-white/5" />

        {/* Body */}
        <div className="px-6 pb-4">
          <pre className="text-sm text-gray-300 whitespace-pre-wrap font-sans leading-relaxed max-h-72 overflow-y-auto">
            {draft.body}
          </pre>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-white/5">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
          >
            Close
          </button>
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-sm font-medium hover:bg-indigo-500/20 transition-colors">
            <Send size={14} />
            Copy Draft
          </button>
        </div>
      </div>
    </div>
  );
}
