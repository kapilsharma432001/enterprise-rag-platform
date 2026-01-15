"use client";

import TenantSwitcher from "../components/TenantSwitcher";
import { useTenant } from "../context/TenantContext";

export default function Home() {
  const { tenantId } = useTenant();

  return (
    <main className="flex flex-col h-screen">
      {/* 1. The Header with the Switcher */}
      <TenantSwitcher />
      
      {/* 2. The Main Content Area */}
      <div className="flex-1 flex flex-col items-center justify-center p-10 space-y-4">
        
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-800">
            Welcome to the Multi-Tenant Knowledge Base
          </h2>
          <p className="text-gray-500 mt-2">
            Upload documents and chat with your isolated data.
          </p>
        </div>

        {/* Visual feedback to show it works */}
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 mt-6 max-w-lg">
          <p className="text-sm text-blue-800">
            <strong>System Status:</strong> <br/>
            {tenantId ? (
              <>✅ Authenticated as Tenant: <span className="font-mono">{tenantId}</span></>
            ) : (
              <>⚠️ No Tenant ID set. Please enter a UUID above.</>
            )}
          </p>
        </div>

      </div>
    </main>
  );
}