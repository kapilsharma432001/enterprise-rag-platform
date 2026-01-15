"use client";

import { createContext, useContext, useState, ReactNode } from "react";

// 1. Define the shape of our global object
interface TenantContextType {
    tenantId: string;
    setTenantId: (id: string) => void;
}

// 2. Create the context (the empty box)
const TenantContext = createContext<TenantContextType | undefined> (undefined);


// 3. Create the Provider (the wrapper component that fills the box)
// Any component wrapped inside TenantProvider can access the tenantId and setTenantId
export const TenantProvider = ({ children }: { children: ReactNode }) => {
    const [tenantId, setTenantId] = useState<string>("");

    return (
        <TenantContext.Provider value={{ tenantId, setTenantId }}>
            {children}
        </TenantContext.Provider>
    );
}

// 4. Custom hook, helper function to use context easily in any component
export function useTenant() {
    const context = useContext(TenantContext);
    if (!context) {
        throw new Error("useTenant must be used within a TenantProvider");
    }
    return context;
}