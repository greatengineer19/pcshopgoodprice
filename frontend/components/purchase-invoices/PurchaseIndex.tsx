"use client"

import { useState, useCallback } from "react"
import type { PurchaseInvoice } from "@/types/purchase-invoice"
import type { SetStateAction } from "react"

import { ButtonAddPurchaseInvoice } from "@/components/purchase-invoices/button-add-purchase-invoice"
import { PurchaseInvoiceList } from "./PurchaseInvoiceList"
import { PurchaseViewModal } from "./PurchaseViewModal"
import { DeleteConfirmationModal } from "./delete-confirmation-modal"
import { NewAndEditPurchaseInvoiceModal } from "./NewAndEditPurchaseInvoiceModal"
import { useToastError } from "@/hooks/use-toast-error"

export default function PurchaseIndex() {
    const [isPurchaseModalOpen, setIsPurchaseInvoiceModalOpen] = useState(false)
    const [isViewModalOpen, setIsViewModalOpen] = useState(false)
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
    const [selectedInvoice, setSelectedPurchaseInvoice] = useState<PurchaseInvoice | null>(null)
    const [isEditMode, setIsEditMode] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const { showErrorToast } = useToastError()

    const handleNewPurchaseModal = useCallback(() => {
        setSelectedPurchaseInvoice(null)
        setIsEditMode(false)
        setIsPurchaseInvoiceModalOpen(true)
    }, []);

    const openEditPurchaseModal = useCallback(async (invoice:
        PurchaseInvoice) => {
            const response = await fetch(`http://localhost:8000/api/purchase-invoices/${invoice.id}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch invoice detail');
            }

            const data = await response.json();
            setSelectedPurchaseInvoice(data)
            setIsEditMode(true)
            setIsPurchaseInvoiceModalOpen(true)
    }, []);

    const openPurchaseViewModal = useCallback(async (invoice: PurchaseInvoice) => {
        try {
            const response = await fetch(`http://localhost:8000/api/purchase-invoices/${invoice.id}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch invoice detail');
            }
            
            const data = await response.json();
            setSelectedPurchaseInvoice(data);
            setIsViewModalOpen(true);
        } catch (error) {
            showErrorToast("Unable to fetch invoice detail");
        }
    }, [showErrorToast]);

    const handleSetLoading = useCallback((value: SetStateAction<boolean>) => {
        setIsLoading(value);
    }, []);

    const openDeleteDialog = useCallback(async (invoice: PurchaseInvoice) => {
        const response = await fetch(`http://localhost:8000/api/purchase-invoices/${invoice.id}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch invoice detail');
        }

        const data = await response.json();
        setSelectedPurchaseInvoice(data);
        setIsDeleteDialogOpen(true);
    }, []);

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold">Purchase Invoices</h1>
                <ButtonAddPurchaseInvoice 
                    handleOnClick={handleNewPurchaseModal}
                />
            </div>

            <PurchaseInvoiceList 
                onViewModal={openPurchaseViewModal}
                onEditModal={openEditPurchaseModal}
                onDeleteInvoice={openDeleteDialog}
            />

            <PurchaseViewModal 
                invoice={selectedInvoice}
                isViewModalOpen={isViewModalOpen}
                closeViewModal={() => setIsViewModalOpen(false)}
                onEditModal={openEditPurchaseModal}
            />

            <NewAndEditPurchaseInvoiceModal 
                isNewModalOpen={isPurchaseModalOpen}
                isLoading={isLoading}
                isEditMode={isEditMode}
                initialInvoice={selectedInvoice}
                closeModal={() => setIsPurchaseInvoiceModalOpen(false)}
                handleSetLoading={handleSetLoading}
            />

            <DeleteConfirmationModal 
                invoice={selectedInvoice}
                isOpen={isDeleteDialogOpen}
                isLoading={isLoading}
                onClose={() => setIsDeleteDialogOpen(false)}
                handleSetLoading={handleSetLoading}
            />
        </div>
    )
}