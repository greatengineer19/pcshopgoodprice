"use client"

// Custom hook for procurement data management
import { useState, useEffect, useCallback } from "react"
import { toast } from "sonner"
import type { PurchaseInvoice } from "@/types/purchase-invoice"
import { useToastError } from "@/hooks/use-toast-error"
import { handleApiError } from "@/utils/api/error-handlers"

export function usePurchaseInvoices() {
    const [purchase_invoices, setPurchaseInvoices] = useState<PurchaseInvoice[]>([])
    const { showErrorToast } = useToastError()

    useEffect(() => {
        const loadInvoices = async () => {
            try {
                const response = await fetch('http://localhost:8080/api/purchase-invoices')

                if (!response.ok) {
                    await handleApiError(response, showErrorToast);
                    return;
                }

                const responseData = await response.json();
                const data: PurchaseInvoice[] = responseData.purchase_invoices;
                setPurchaseInvoices(data);
            } catch (error) {
                showErrorToast("Unable to load invoice")
            };
        };

        loadInvoices()
    }, []);

    return {
        purchase_invoices,
        setPurchaseInvoices
    }
}