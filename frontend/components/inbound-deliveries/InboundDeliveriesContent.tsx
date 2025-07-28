"use client"

import type { SetStateAction } from "react"
import { useState, useCallback } from "react"
import { Plus, ShowerHead } from "lucide-react"
import type { InboundDelivery } from "@/types/inbound-delivery"

import { Button } from "@/components/ui/button"
import { InboundDeliveriesList } from "./InboundDeliveriesList"
import { InboundDeliveryForm } from "./InboundDeliveryForm"
import { InboundViewModal } from "./InboundViewModal"
import { DeleteConfirmationModal } from "./DeleteConfirmationModal"

import { useToastError } from "@/hooks/use-toast-error"

export default function InboundDeliveriesContent() {
    const { showErrorToast } = useToastError()
    const [selectedInboundDelivery, setSelectedInboundDelivery] = useState<InboundDelivery | null>(null)

    const [isLoading, setIsLoading] = useState(false)
    const [isFormVisible, setIsFormVisible] = useState(false)
    const [isViewModalOpen, setIsViewModalOpen] = useState(false)
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)

    const handleView = useCallback(async (inboundDelivery: InboundDelivery) => {
        try {
            const response = await fetch(`http://localhost:80/api/inbound-deliveries/${inboundDelivery.id}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch invoice detail');
            }
            
            const data = await response.json();

            setSelectedInboundDelivery(data);
            setIsViewModalOpen(true);
        } catch (error) {
            showErrorToast("Unable to fetch delivery detail");
        }
    }, [showErrorToast]);

    const handleDelete = useCallback(async (inboundDelivery: InboundDelivery) => {
        const response = await fetch(`http://localhost:80/api/inbound-deliveries/${inboundDelivery.id}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch delivery detail');
        }

        const data = await response.json();

        setSelectedInboundDelivery(data);
        setIsDeleteDialogOpen(true)
    }, [])

    const handleNewInbound = useCallback(() => {
        setIsFormVisible(true)
    }, [])

    const handleSetLoading = useCallback((value: SetStateAction<boolean>) => {
        setIsLoading(value);
    }, []);

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold">Inbound Deliveries</h1>
                <Button onClick={handleNewInbound} className="flex items-center gap-2 bg-[#D84040] hover:bg-[#383838] dark:hover:bg-[#E85050] text-white" disabled={isFormVisible}>
                    <Plus className="mr-2 h-4 w-4" /> New Inbound Delivery
                </Button>
            </div>

            {
                isFormVisible ? (
                    <div className="mb-8">
                        <h2 className="text-xl font-bold mb-4">Create New Inbound Delivery</h2>
                        <InboundDeliveryForm
                            isLoading={isLoading}
                            handleSetLoading={handleSetLoading}
                            hideForm={() => setIsFormVisible(false)}
                        />
                    </div>
                ) : (
                    <InboundDeliveriesList 
                        handleView={handleView}
                        handleDelete={handleDelete}
                    />
                )
            }

            <InboundViewModal
                inboundDelivery={selectedInboundDelivery}
                isOpen={isViewModalOpen}
                onClose={() => setIsViewModalOpen(false)}
            />

            <DeleteConfirmationModal
                inboundDelivery={selectedInboundDelivery}
                isDialogOpen={isDeleteDialogOpen}
                isLoading={isLoading}
                onClose={() => setIsDeleteDialogOpen(false)}
                handleSetLoading={handleSetLoading}
            />
        </div>
    )
}