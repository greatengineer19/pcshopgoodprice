"use client"

import { Trash2, AlertTriangle } from "lucide-react"
import type { ProductInFrontend } from "@/types/product"

import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
    DialogDescription
} from "@/components/ui/dialog"

import { Button } from "@/components/ui/button"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { useToastError } from "@/hooks/use-toast-error"
import { useToastSuccess } from "@/hooks/use-toast-success"
import { handleApiError } from "@/utils/api/error-handlers"

interface DeleteConfirmationModalProps {
    selectedProduct: ProductInFrontend | null,
    isDeleteDialogOpen: boolean,
    isLoading: boolean,
    setIsLoading: React.Dispatch<React.SetStateAction<boolean>>,
    setIsDialogOpen: React.Dispatch<React.SetStateAction<boolean>>,
    setCloseDeleteDialog: () => void
  }

export function DeleteConfirmationModal({
    selectedProduct,
    isDeleteDialogOpen,
    isLoading,
    setIsLoading,
    setIsDialogOpen,
    setCloseDeleteDialog
}: DeleteConfirmationModalProps) {
    if (!selectedProduct) return null

    const { showErrorToast } = useToastError()
    const { showSuccessToast } = useToastSuccess()

    const handleDeleteProduct = async () => {
        if (!selectedProduct) return;
    
        setIsLoading(true);
    
        try {
            const response = await fetch(
                "http://localhost:8080/api/computer-components/" + selectedProduct.id,
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

            showSuccessToast("Product deleted successfully");

            // Close dialogs first
            setCloseDeleteDialog();
            setIsDialogOpen(false);

            // Use setTimeout to ensure dialogs are closed before reload
            setTimeout(() => {
                window.location.reload();
            }, 100);
        } catch (error) {
            showErrorToast("Failed to connect to the server. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };    

    return (
        <Dialog open={isDeleteDialogOpen} onOpenChange={setCloseDeleteDialog}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle className="text-xl font-bold">
                        Confirm Deletion
                    </DialogTitle>
                    <DialogDescription>
                        Are you sure you want to delete this product? This action cannot be undone.
                    </DialogDescription>
                </DialogHeader>

                {selectedProduct && (
                    <Alert variant="destructive" className="my-4">
                        <AlertTriangle className="h-4 w-4" />
                        <AlertTitle>Warning</AlertTitle>
                        <AlertDescription>You are about to delete "{selectedProduct.name}".</AlertDescription>
                    </Alert>
                )}

                <DialogFooter className="flex justify-end gap-2 mt-4">
                    <Button type="button" variant="outline" onClick={setCloseDeleteDialog} disabled={isLoading}>
                        Cancel
                    </Button>
                    <Button
                        type="button"
                        variant="destructive"
                        onClick={handleDeleteProduct}
                        className="flex items-center gap-1"
                        disabled={isLoading}
                    >
                        <Trash2 className="h-4 w-4" /> { isLoading ? "Deleting" : "Delete Product" }
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}