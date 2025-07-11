"use client"

import { useState, useCallback, useEffect, useMemo } from "react"
import { toast } from "sonner"
import { useToastSuccess } from "./use-toast-success"
import type { PurchaseInvoice, PurchaseInvoiceLine, OnEditPurchaseInvoiceLine, MappedProduct } from "@/types/purchase-invoice"
import type { ProductInFrontend } from "@/types/product"

interface InitialDataProps {
    supplierName: string
    expectedDeliveryDate: string | null
    notes: string | null
    purchase_invoice_lines: PurchaseInvoiceLine[]
}

export function usePurchaseInvoiceForm(initialData?: InitialDataProps) {
    const [selectedInvoiceLines, setSelectedInvoiceLines] = useState<OnEditPurchaseInvoiceLine[]>([]);
    const [destroyableInvoiceLines, setDestroyableInvoiceLines] = useState<OnEditPurchaseInvoiceLine[]>([]);
    const [supplierName, setSupplierName] = useState("");
    const [expectedDeliveryDate, setExpectedDeliveryDate] = useState("");
    const [procurementNote, setProcurementNote] = useState("");
    const { showSuccessToast } = useToastSuccess();

    useEffect(() => {
        if (initialData) {
            setSupplierName(initialData.supplierName || "");
            const formattedDate = initialData.expectedDeliveryDate
                ? new Date(initialData.expectedDeliveryDate).toISOString().split("T")[0]
                : "";
            setExpectedDeliveryDate(formattedDate);
            setProcurementNote(initialData.notes || "");

            const mappedInvoiceLines: OnEditPurchaseInvoiceLine[] = initialData.purchase_invoice_lines?.map(invoice_line => ({
                id: invoice_line.id,
                component_id: invoice_line.component_id,
                component_name: invoice_line.component_name,
                quantity: invoice_line.quantity,
                price: invoice_line.price_per_unit,
                stock: 10,
                component_category_id: invoice_line.component_category_id,
                component_category_name: invoice_line.component_category_name
            })) || [];

            setSelectedInvoiceLines(mappedInvoiceLines);
        }
    }, [initialData?.supplierName]); 

    const addProductToProcurement = (product: MappedProduct) => {
        const existingProduct = selectedInvoiceLines.find((invoice_line) => invoice_line.component_id === product.id)

        if (existingProduct) {
            setSelectedInvoiceLines(
                selectedInvoiceLines.map(
                    (invoice_line) => invoice_line.component_id === product.id
                        ? { ...invoice_line, quantity: (invoice_line.quantity || 0) + 1 }
                        : invoice_line
                )
            )
        } else {
            setSelectedInvoiceLines([...selectedInvoiceLines, {
                id: null,
                component_id: product.id,
                component_name: product.name,
                quantity: 1,
                price: Number(product.numberBuyPrice),
                component_category_id: product.component_category_id,
                component_category_name: product.component_category_name
            }])
        }
        
        showSuccessToast(`Added ${product.name} to procurement`)
    };

    const removeProductFromProcurement = (productId: number) => {
        const hasIdInvoiceLine = selectedInvoiceLines.find((invoice_line) => invoice_line.id !== null && invoice_line.component_id === productId)
        if (hasIdInvoiceLine) {
            console.log(hasIdInvoiceLine);
            setDestroyableInvoiceLines([
                ...destroyableInvoiceLines,
                hasIdInvoiceLine
            ])
        };
        setSelectedInvoiceLines(selectedInvoiceLines.filter((invoice_line) => invoice_line.component_id !== productId))
        toast.info("Product removed from procurement")
    };

    const updateProductQuantity = (productId: any, newQuantity: number) => {
        if (newQuantity < 1) {
            removeProductFromProcurement(productId)
            return
        }

        setSelectedInvoiceLines(selectedInvoiceLines.map(
            (invoiceLine) => (invoiceLine.component_id === productId ?
            { ...invoiceLine, quantity: newQuantity } :
            invoiceLine)
        ))
    };

    const calculateTotal = () => {
        return selectedInvoiceLines.reduce((total, product) => {
            return total + Number(product.price) * (product.quantity || 0 )
        }, 0)
    };

    const resetForm = () => {
        setSelectedInvoiceLines([])
        setSupplierName("")
        setExpectedDeliveryDate("")
        setProcurementNote("")
    };

    const getFormData = () => {
        return {
            supplierName,
            expectedDeliveryDate,
            notes: procurementNote,
            selectedInvoiceLines: selectedInvoiceLines
        }
    }

    const validateForm = (): boolean => {
        if (selectedInvoiceLines.length === 0) {
            toast.error("Please select at least one product")
            return false
        }

        if (!supplierName) {
            toast.error("Please enter a supplier name")
            return false
        }

        return true
    }

    return {
        selectedInvoiceLines,
        destroyableInvoiceLines,
        supplierName,
        setSupplierName,
        expectedDeliveryDate,
        setExpectedDeliveryDate,
        procurementNote,
        setProcurementNote,
        addProductToProcurement,
        removeProductFromProcurement,
        updateProductQuantity,
        calculateTotal,
        resetForm,
        getFormData,
        validateForm,
    }
}