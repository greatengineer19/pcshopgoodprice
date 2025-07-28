"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { Package, Upload, X, AlertTriangle } from "lucide-react"
import Image from "next/image"
import type { InboundDeliveryFormData, InboundDeliveryLineFormData } from "@/types/inbound-delivery"
import type { UploadedImageResponse } from "@/types/image"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { useInboundDeliveryForm } from "@/hooks/use-inbound-delivery-form"

import { handleApiError } from "@/utils/api/error-handlers"
import { useToastSuccess } from "@/hooks/use-toast-success"
import { useToastError } from "@/hooks/use-toast-error"

interface ParamsProps {
    isLoading: boolean
    handleSetLoading: React.Dispatch<React.SetStateAction<boolean>>
    hideForm: () => void
}

export function InboundDeliveryForm({
    isLoading,
    handleSetLoading,
    hideForm
}: ParamsProps) {
    const [fileInputKey, setFileInputKey] = useState(Date.now())

    const { showSuccessToast } = useToastSuccess()
    const { showErrorToast } = useToastError()

    const {
        formData,
        deliverablePurchaseInvoices,
        isLoadingInvoices,
        selectedInvoice,
        handleInvoiceSelect,
        handleChange,
        handleLineChange,
        handleAttachmentChange,
        handleRemoveAttachment,
        validateForm,
        resetForm
    } = useInboundDeliveryForm()

    const newIsLoading = isLoading || isLoadingInvoices

    const handleFormCancel = useCallback(() => {
        hideForm()
        resetForm()
    }, []);

    const handleSubmit = useCallback((e: React.FormEvent) => {
        e.preventDefault()

        if (!validateForm()) return
        createNewInboundDelivery(formData)
    }, [formData, validateForm]);

    const createNewInboundDelivery = async (formData: InboundDeliveryFormData) => {
        handleSetLoading(true)

        try {
            const payload: InboundDeliveryFormData = {
                purchase_invoice_id: formData.purchase_invoice_id,
                purchase_invoice_no: formData.purchase_invoice_no,
                inbound_delivery_date: formData.inbound_delivery_date,
                inbound_delivery_reference: formData.inbound_delivery_reference,
                received_by: formData.received_by,
                notes: formData.notes,
                inbound_delivery_lines_attributes: formData.inbound_delivery_lines_attributes,
                inbound_delivery_attachments_attributes: []
            }

            if (Array.isArray(formData.inbound_delivery_attachments_attributes) && formData.inbound_delivery_attachments_attributes.length > 0) {
                const imageFormData = new FormData();
                formData.inbound_delivery_attachments_attributes.forEach((file) => {
                    imageFormData.append('files', file);
                });
                
                const response_upload_images = await fetch('http://localhost:80/api/multi_upload_url', {
                    method: 'POST',
                    body: imageFormData,
                });

                if (!response_upload_images.ok) {
                    await handleApiError(response_upload_images, showErrorToast);
                    return;
                }
                
                const uploadData = await response_upload_images.json();
                
                payload.inbound_delivery_attachments_attributes = uploadData.image_list.map((uploaded_image: UploadedImageResponse) => ({
                    file_s3_key: uploaded_image.s3_key,
                    uploaded_by: formData.received_by,
                    _destroy: false
                }));
            }

            const response = await fetch("http://localhost:80/api/inbound-deliveries", {
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
            showSuccessToast(data.message || "Inbound Delivery created successfully!")

            resetForm()
            window.location.reload();
        } catch (error) {
            showErrorToast("Unable to create delivery")
        } finally {
            handleSetLoading(false)
        }
    }

    return (
        <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid gap-4">
                <div className="grid gap-2">
                    <Label htmlFor="invoice-select" className="required">
                        Purchase Invoice
                    </Label>
                    <Select value={formData.purchase_invoice_id?.toString() ?? undefined} onValueChange={(invoiceId) => {
                            const selectedInvoice = deliverablePurchaseInvoices.find(
                                (inv) => String(inv.id) === invoiceId
                            );
                    
                            if (selectedInvoice) {
                                handleInvoiceSelect(selectedInvoice.id); // Pass the invoice.id here
                            }
                        }} disabled={newIsLoading}>
                        <SelectTrigger id="invoice-select">
                            <SelectValue placeholder="Select an invoice" />
                        </SelectTrigger>
                        <SelectContent>
                            {deliverablePurchaseInvoices.length === 0 ? (
                                <SelectItem value="none" disabled>
                                    No pending invoices available
                                </SelectItem>
                            ) : (
                                deliverablePurchaseInvoices.map((invoice) => (
                                    <SelectItem key={invoice.id} value={String(invoice.id)}>
                                        {invoice.purchase_invoice_no} - {invoice.supplier_name}
                                    </SelectItem>
                                ))
                            )}
                        </SelectContent>
                    </Select>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="grid gap-2">
                        <Label htmlFor="delivery-date" className="required">
                            Delivery Date
                        </Label>
                        <Input 
                            id="delivery-date"
                            type="date"
                            value={formData.inbound_delivery_date}
                            onChange={(e) => handleChange("inbound_delivery_date", e.target.value)}
                            required
                            disabled={newIsLoading}
                        />
                    </div>
                    <div className="grid gap-2">
                        <Label htmlFor="delivery-reference" className="required">
                            Delivery Reference
                        </Label>
                        <Input 
                            id="delivery-reference"
                            placeholder="e.g., EK-OBD-12345"
                            value={formData.inbound_delivery_reference}
                            onChange={(e) => handleChange("inbound_delivery_reference", e.target.value)}
                            required
                            disabled={newIsLoading}
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="grid gap-2">
                        <Label htmlFor="received-by" className="required">
                            Received By
                        </Label>
                        <Input 
                            id="received-by"
                            placeholder="Name of receiver"
                            value={formData.received_by}
                            onChange={(e) => handleChange("received_by", e.target.value)}
                            required
                            disabled={newIsLoading}
                        />
                    </div>
                    <div className="grid gap-2">
                        <Label htmlFor="notes">Notes</Label>
                        <Textarea 
                            id="notes"
                            placeholder="Any additional notes about this delivery"
                            value={formData.notes}
                            onChange={(e) => handleChange("notes", e.target.value)}
                            disabled={newIsLoading}
                            rows={1}
                        />
                    </div>
                </div>
            </div>

            {selectedInvoice && (
                <Card>
                    <CardContent className="pt-6">
                        <h3 className="text-lg font-medium mb-4">Delivery Items</h3>
                        <div className="rounded-md border overflow-hidden">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Component name</TableHead>
                                        <TableHead className="text-center">Quantity invoice</TableHead>
                                        <TableHead className="text-center">Received</TableHead>
                                        <TableHead className="text-center">Damaged</TableHead>
                                        <TableHead>Notes</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {formData.inbound_delivery_lines_attributes.map((deliveryLine, index) => {
                                        const invoiceLine = selectedInvoice.deliverable_invoice_lines.find((invoiceLine) => invoiceLine.component_id === deliveryLine.component_id)
                                        if (!invoiceLine) return null

                                        const isQuantityError = deliveryLine.received_quantity + deliveryLine.damaged_quantity > deliveryLine.expected_quantity

                                        return (
                                            <TableRow key={index}>
                                                <TableCell className="font-medium max-w-[200px] break-words whitespace-normal">
                                                    <div className="flex items-center gap-2">
                                                        <span className="font-medium">{invoiceLine.component_name}</span>
                                                    </div>
                                                </TableCell>
                                                <TableCell className="text-center">{deliveryLine.expected_quantity}</TableCell>
                                                <TableCell>
                                                    <Input 
                                                        type="number"
                                                        min="0"
                                                        max={deliveryLine.expected_quantity}
                                                        value={deliveryLine.received_quantity}
                                                        onChange={(e) =>
                                                            handleLineChange(index, "received_quantity", Number.parseInt(e.target.value) || 0)
                                                        }
                                                        className={`w-20 mx-auto text-center ${isQuantityError ? "border-red-500" : ""}`}
                                                        disabled={newIsLoading}
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    <Input 
                                                        type="number"
                                                        min="0"
                                                        max={deliveryLine.expected_quantity}
                                                        value={deliveryLine.damaged_quantity}
                                                        onChange={(e) =>
                                                            handleLineChange(index, "damaged_quantity", Number.parseInt(e.target.value) || 0)
                                                        }
                                                        className={`w-20 mx-auto text-center ${isQuantityError ? "border-red-500" : ""}`}
                                                        disabled={newIsLoading}
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    <Input 
                                                        placeholder="Item notes"
                                                        value={deliveryLine.notes}
                                                        onChange={(e) => handleLineChange(index, "notes", e.target.value)}
                                                        disabled={newIsLoading}
                                                    />
                                                </TableCell>
                                            </TableRow>
                                        )
                                    })}
                                </TableBody>
                            </Table>
                        </div>

                        {formData.inbound_delivery_lines_attributes.some((deliveryLine) => deliveryLine.received_quantity + deliveryLine.damaged_quantity > deliveryLine.expected_quantity) && (
                            <Alert variant="destructive" className="mt-4">
                                <AlertTriangle className="h-4 w-4" />
                                <AlertDescription>
                                    Received quantity plus damaged quantity cannot exceed quantity invoice
                                </AlertDescription>
                            </Alert>
                        )}
                    </CardContent>
                </Card>
            )}

            <Card>
                <CardContent className="pt-6">
                    <div className="flex flex-col gap-4">
                        <div className="flex justify-between items-center">
                            <h3 className="text-lg font-medium">Attachments</h3>
                            <div>
                                <input
                                    type="file"
                                    id="file-upload"
                                    key={fileInputKey}
                                    className="hidden"
                                    multiple
                                    onChange={(e) => {
                                        handleAttachmentChange(e.target.files)
                                        setFileInputKey(Date.now())
                                    }}
                                    disabled={newIsLoading}
                                />
                                <label htmlFor="file-upload">
                                    <Button type="button" variant="outline" className="cursor-pointer" disabled={newIsLoading} asChild>
                                        <span>
                                            <Upload className="h-4 w-4 mr-2" />
                                            Upload Files
                                        </span>
                                    </Button>
                                </label>
                            </div>
                        </div>

                        {formData.inbound_delivery_attachments_attributes.length > 0 ? (
                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mt-2">
                                {formData.inbound_delivery_attachments_attributes.map((file, index) => (
                                    <div key={index} className="flex items-center justify-between border rounded-md p-2">
                                        <div className="flex items-center gap-2 overflow-hidden">
                                            <Package className="h-5 w-5 flex-shrink-0 text-muted-foreground" />
                                            <span className="text-sm truncate">{file.name}</span>
                                        </div>
                                        <Button 
                                            type="button"
                                            variant="ghost"
                                            size="sm"
                                            className="h-8 w-8 p-0 text-muted-foreground"
                                            onClick={() => handleRemoveAttachment(index)}
                                            disabled={newIsLoading}
                                        >
                                            <X className="h-4 w-4" />
                                        </Button>
                                    </div> 
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-muted-foreground border border-dashed rounded-md">
                                No attachments added yet
                            </div>
                        )}
                    </div>
                </CardContent>
            </Card>

            <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={handleFormCancel} disabled={newIsLoading}>
                    Cancel
                </Button>
                <Button
                    type="submit"
                    disabled={
                        newIsLoading ||
                        !formData.purchase_invoice_id ||
                        !formData.inbound_delivery_date ||
                        !formData.inbound_delivery_reference ||
                        !formData.received_by ||
                        formData.inbound_delivery_lines_attributes.some((deliveryLine) => deliveryLine.received_quantity + deliveryLine.damaged_quantity > deliveryLine.expected_quantity)
                    }
                >
                    {newIsLoading ? "Processing..." : "Create Inbound"}
                </Button>
            </div>
        </form>
    )
}