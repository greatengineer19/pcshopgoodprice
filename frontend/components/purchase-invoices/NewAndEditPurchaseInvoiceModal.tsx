"use client"

import { useCallback } from "react"
import { Check } from "lucide-react"
import type {
    PurchaseInvoice,
    PurchaseForm,
    OnEditPurchaseInvoiceLine,
    MappedProduct,
    PurchaseInvoiceToBackend,
    PurchaseInvoiceLine } from "@/types/purchase-invoice"
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
    DialogDescription,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { SelectProducts } from "./SelectProducts"
import { PurchaseSummary } from "./PurchaseSummary"
import { usePurchaseInvoiceForm } from "@/hooks/use-purchase-invoice-form"
import { useProducts } from "@/hooks/use-products"
import { useToastError } from "@/hooks/use-toast-error"
import { useToastSuccess } from "@/hooks/use-toast-success"
import { handleApiError } from "@/utils/api/error-handlers"

interface ParamsProps {
    isNewModalOpen: boolean
    isLoading: boolean
    isEditMode: boolean
    initialInvoice: PurchaseInvoice | null
    closeModal: () => void
    handleSetLoading: React.Dispatch<React.SetStateAction<boolean>>
}

export function NewAndEditPurchaseInvoiceModal({
    isNewModalOpen,
    isLoading,
    isEditMode,
    initialInvoice,
    closeModal,
    handleSetLoading
}: ParamsProps) {
    const { products } = useProducts()
    const mappedProducts: MappedProduct[] = products ? products.map(
            (product) => ({
                id: Number(product.id),
                name: product.name,
                quantity: product.quantity,
                buyPrice: Number(product.computer_component_sell_price_settings.find(p => p.day_type === "default")?.price_per_unit || 0).toLocaleString(),
                numberBuyPrice: Number(product.computer_component_sell_price_settings.find(p => p.day_type === "default")?.price_per_unit || 0),
                component_category_id: product.component_category_id,
                component_category_name: product.component_category_name
            })
        ) : []

    const initialData = isEditMode && initialInvoice ? {
        supplierName: initialInvoice.supplier_name,
        expectedDeliveryDate: initialInvoice.expected_delivery_date,
        notes: initialInvoice.notes,
        purchase_invoice_lines: initialInvoice.purchase_invoice_lines
    } : undefined

    const {
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
        validateForm
    } = usePurchaseInvoiceForm(initialData)

    const { showErrorToast } = useToastError()
    const { showSuccessToast } = useToastSuccess()

    const createNewInvoice = async (purchaseForm: PurchaseForm) => {
        handleSetLoading(true)

        try {
            const payload: PurchaseInvoiceToBackend = {
                id: null,
                supplier_name: purchaseForm.supplierName,
                expected_delivery_date: purchaseForm.expectedDeliveryDate,
                notes: purchaseForm.notes,
                invoice_date: (new Date()).toISOString(),
                purchase_invoice_lines_attributes: purchaseForm.selectedInvoiceLines.map(
                    (invoiceLine) => ({
                        id: null,
                        component_id: Number(invoiceLine.component_id),
                        component_name: invoiceLine.component_name,
                        component_category_id: invoiceLine.component_category_id,
                        component_category_name: invoiceLine.component_category_name,
                        quantity: invoiceLine.quantity,
                        price_per_unit: invoiceLine.price
                    })
                )
            }

            const response = await fetch("http://localhost:8000/api/purchase-invoices", {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
              });

            if (!response.ok) {
                await handleApiError(response, showErrorToast);
                return;
            }
        
            const data = await response.json();
            showSuccessToast(data.message || "Purchase Invoice created successfully!")

            resetForm()
            closeModal
            window.location.reload();
        } catch (error) {
            showErrorToast("Unable to create invoice")
        } finally {
            handleSetLoading(false)
        }
    }

    const updatePurchaseInvoice = async (id: number, purchaseForm: PurchaseForm) => {
        handleSetLoading(true)

        try {
            const payload: PurchaseInvoiceToBackend = {
                id: id,
                supplier_name: purchaseForm.supplierName,
                expected_delivery_date: purchaseForm.expectedDeliveryDate,
                notes: purchaseForm.notes,
                invoice_date: (new Date()).toISOString(),
                purchase_invoice_lines_attributes: [
                ...purchaseForm.selectedInvoiceLines.map((invoiceLine) => ({
                    id: invoiceLine.id,
                    component_id: Number(invoiceLine.component_id),
                    component_name: invoiceLine.component_name,
                    component_category_id: invoiceLine.component_category_id,
                    component_category_name: invoiceLine.component_category_name,
                    quantity: invoiceLine.quantity,
                    price_per_unit: invoiceLine.price,
                })),
                ...destroyableInvoiceLines.map((invoiceLine) => ({
                    id: invoiceLine.id,
                    component_id: Number(invoiceLine.component_id),
                    component_name: invoiceLine.component_name,
                    component_category_id: invoiceLine.component_category_id,
                    component_category_name: invoiceLine.component_category_name,
                    quantity: invoiceLine.quantity,
                    price_per_unit: invoiceLine.price,
                    _destroy: true,
                })),
                ]
            }

            const response = await fetch("http://localhost:8000/api/purchase-invoices/" + id, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                await handleApiError(response, showErrorToast);
                return;
            }
    
            const data = await response.json();
            showSuccessToast(data.message || "Purchase Invoice updated successfully");

            resetForm()
            closeModal
            window.location.reload();
        } catch (error) {
            showErrorToast("Unable to update invoice")
        } finally {
            handleSetLoading(false)
        }
    }

    const handleSubmit = () => {
        if (!validateForm()) return;

        const formData = getFormData();

        if (isEditMode && initialInvoice) {
            updatePurchaseInvoice(Number(initialInvoice.id), formData);
        } else {
            createNewInvoice(formData);
        }
    };


    return (
        <Dialog open={isNewModalOpen} onOpenChange={closeModal}>
            <DialogContent className="max-w-[95vw] w-[1400px]">
                <DialogHeader>
                    <DialogTitle className="text-xl font-bold">
                        {isEditMode ? `Edit Purchase Invoice: ${initialInvoice?.purchase_invoice_no}` : "New Procurement"}
                    </DialogTitle>
                    <DialogDescription>
                        {
                            isEditMode ?
                            "Update the details of this purchase invoice" :
                            "Select products and enter details for the new procurement"
                        }
                    </DialogDescription>
                </DialogHeader>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-4">
                    {/* Product Selection */}
                    <div className="lg:col-span-2">
                        <SelectProducts products={mappedProducts} onAddProduct={addProductToProcurement} />
                    </div>

                    {/* Procurement Summary */}
                    <div>
                        <PurchaseSummary 
                            selectedInvoiceLines={selectedInvoiceLines}
                            supplierName={supplierName}
                            setSupplierName={setSupplierName}
                            expectedDeliveryDate={expectedDeliveryDate}
                            setExpectedDeliveryDate={setExpectedDeliveryDate}
                            procurementNote={procurementNote}
                            setProcurementNote={setProcurementNote}
                            onUpdateQuantity={updateProductQuantity}
                            onRemoveProduct={removeProductFromProcurement}
                            total={calculateTotal()}
                        />
                    </div>
                </div>

                <DialogFooter className="flex justify-end gap-2 mt-6">
                    <Button type="button" variant="outline" onClick={closeModal} disabled={isLoading}>
                        Cancel
                    </Button>
                    <Button
                        type="button"
                        onClick={handleSubmit}
                        className="flex items-center gap-1 bg-green-600 hover:bg-green-700"
                        disabled={isLoading || selectedInvoiceLines.length === 0 || !supplierName}
                    >
                        {
                            isLoading ? (
                                "Processing"
                            ) : (
                                <>
                                    <Check className="h-4 w-4" />
                                    {isEditMode ? "Update" : "Create"} Procurement
                                </>
                            )
                        }
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}