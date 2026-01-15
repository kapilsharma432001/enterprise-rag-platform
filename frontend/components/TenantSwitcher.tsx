"use client";

import { useTenant } from "@/context/TenantContext";

export default function TenantSwitcher() {
    // we grab the global state and the setter function
    const { tenantId, setTenantId } = useTenant();

    return (
        <div className="p-4 bg-white borde-b border-gray-200 flex flex-col md:flex-row justify-between items-center shadow-sm sticky top-0 z-10">
            <h1 className="text-xl font-bold text-indigo-600 mb-2 md:mb-0">
                Enterprise RAG 🤖
            </h1>
            <div className="flex items-center gap-3">
                <label className="text-sm font-medium text-gray-600">
                    Current Tenant ID:
                </label>
                <input 
                type="text" 
                value={tenantId}
                onChange={(e) => setTenantId(e.target.value)}
                className="border border-gray-300 rounded px-3 py-1.5 text-sm w-80 font-mono bg-gray-50 focus:ring-2 focus:ring-indigo-500 outline-none"
                placeholder="Paste UUID here..."
                />
            </div>
        </div>
    )
};