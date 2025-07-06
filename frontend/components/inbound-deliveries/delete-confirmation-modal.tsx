"use client"

import { useCallback } from "react"
import { AlertTriangle, Trash2 } from "lucide-react"
import type { InboundDelivery } from "@/types/inbound-delivery"

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { useToastError } from "@/hooks/use-toast-error"
import { handleApiError } from "@/utils/api/error-handlers"
import { useToastSuccess } from "@/hooks/use-toast-success"

interface ParamsProps {
    inboundDelivery: InboundDelivery | null
    isDialogOpen: boolean
    isLoading: boolean
    onClose: () => void
    handleSetLoading: React.Dispatch<React.SetStateAction<boolean>>
}

export function DeleteConfirmationModal({
    inboundDelivery,
    isDialogOpen,
    isLoading,
    onClose,
    handleSetLoading
}: ParamsProps) {
    const { showErrorToast } = useToastError()
    const { showSuccessToast } = useToastSuccess()

    if (!inboundDelivery) return null

    const performDeleteInboundDelivery = useCallback(async () => {
        handleSetLoading(true)

        try {
            const response = await fetch(
                "http://localhost:8080/api/inbound-deliveries/" + inboundDelivery.id,
                {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

            if (!response.ok) {
                await handleApiError(response, showErrorToast);
                return;
            }
    
            showSuccessToast("Inbound Delivery deleted successfully");
            window.location.reload();
        } catch (error) {
            showErrorToast("Failed to connect to the server. Please try again.");
        } finally {
            handleSetLoading(false);
        }
    }, []);

    return (
        <Dialog open={isDialogOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w[425px] w-fit">
                <DialogHeader>
                    <DialogTitle className="text-xl font-bold">Confirm Deletion</DialogTitle>
                    <DialogDescription>
                        Are you sure you want to delete this inbound delivery? This action cannot be undone.
                    </DialogDescription>
                </DialogHeader>

                <Alert variant="destructive" className="my-4">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertTitle>Warning</AlertTitle>
                    <AlertDescription>
                        You are about to delete purchase inbound "{inboundDelivery.inbound_delivery_no}" for invoice {inboundDelivery.purchase_invoice_no}.
                    </AlertDescription>
                </Alert>

                <DialogFooter className="flex justify-end gap-2 mt-4">
                    <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
                        Cancel
                    </Button>
                    <Button 
                        type="button"
                        variant="destructive"
                        onClick={performDeleteInboundDelivery}
                        className="flex items-center gap-1"
                        disabled={isLoading}
                    >
                        <Trash2 className="h-4 w-4" />
                        Delete Inbound
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}