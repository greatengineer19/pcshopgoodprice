"use client"

import { useState, useCallback, useEffect } from "react"
import type { InboundDelivery, InboundDeliveryFormData, InboundDeliveryLineFormData } from "@/types/inbound-delivery"
import type { DeliverablePurchaseInvoice } from "@/types/purchase-invoice"
import { useToastError } from "./use-toast-error"
import { handleApiError } from "@/utils/api/error-handlers"

export function useInboundDeliveryForm() {
    const [deliverablePurchaseInvoices, setDeliverablePurchaseInvoices] = useState<DeliverablePurchaseInvoice[]>([])
    const [isLoadingInvoices, setIsLoadingInvoices] = useState(false)
    const [selectedInvoice, setSelectedInvoice] = useState<DeliverablePurchaseInvoice | null>(null)
    const { showErrorToast } = useToastError()

    const [formData, setFormData] = useState<InboundDeliveryFormData>({
        purchase_invoice_id: null,
        purchase_invoice_no: "",
        inbound_delivery_date: new Date().toISOString().split("T")[0],
        inbound_delivery_reference: "",
        received_by: "",
        notes: "",
        inbound_delivery_lines_attributes: [],
        inbound_delivery_attachments_attributes: []
    });

    useEffect(() => {
        const loadDeliverableInvoices = async () => {
            setIsLoadingInvoices(true)

            try {
                const response = await fetch('http://localhost:8000/api/inbound-deliveries/deliverable-purchase-invoices')

                if (!response.ok) {
                    await handleApiError(response, showErrorToast);
                    return
                }

                const responseData = await response.json();
                const data: DeliverablePurchaseInvoice[] = responseData.purchase_invoices;
                setDeliverablePurchaseInvoices(data)
            } catch (error) {
                showErrorToast("Unable to load purchase invoices")
            } finally {
                setIsLoadingInvoices(false)
            }
        };

        loadDeliverableInvoices()
    }, []);

    const handleInvoiceSelect = (invoiceId: number) => {
        const invoice = deliverablePurchaseInvoices.find((invoice) => invoice.id === invoiceId)

        if (!invoice) {
            showErrorToast("Invoice not found")
            return
        }

        setSelectedInvoice(invoice)

        const inboundLines: InboundDeliveryLineFormData[] = invoice.deliverable_invoice_lines.map((invoiceLine) => ({
            purchase_invoice_line_id: invoiceLine.id,
            component_id: invoiceLine.component_id,
            component_name: invoiceLine.component_name,
            component_category_id: invoiceLine.component_category_id,
            component_category_name: invoiceLine.component_category_name,
            expected_quantity: invoiceLine.deliverable_quantity || 0,
            received_quantity: invoiceLine.deliverable_quantity || 0,
            damaged_quantity: 0,
            notes: "",
            price_per_unit: invoiceLine.price_per_unit
        }))

        setFormData({
            ...formData,
            purchase_invoice_id: invoiceId,
            inbound_delivery_lines_attributes: inboundLines
        })
    }

    const handleChange = (field: keyof InboundDeliveryFormData, value: string) => {
        setFormData({
            ...formData,
            [field]: value
        })
    }

    const handleLineChange = (index: number, field: keyof InboundDeliveryLineFormData, value: number | string) => {
        const updatedLines = [...formData.inbound_delivery_lines_attributes]
        updatedLines[index] = {
            ...updatedLines[index],
            [field]: value
        }

        setFormData({
            ...formData,
            inbound_delivery_lines_attributes: updatedLines
        })
    }

    const handleAttachmentChange = (files: FileList | null) => {
        if (!files) return

        const fileArray = Array.from(files)
        setFormData(prev => ({
            ...prev,
            inbound_delivery_attachments_attributes: [
                ...(prev.inbound_delivery_attachments_attributes || []),
                ...fileArray
            ]
        }))
    }

    const handleRemoveAttachment = (index: number) => {
        const updatedAttachments = [...formData.inbound_delivery_attachments_attributes]
        updatedAttachments.splice(index, 1)

        setFormData({
            ...formData,
            inbound_delivery_attachments_attributes: updatedAttachments
        })
    }

    const validateForm = (): boolean => {
        if (!formData.purchase_invoice_id) {
            showErrorToast("Please select an invoice")
            return false
        }

        if (!formData.inbound_delivery_date) {
            showErrorToast("Please enter a delivery date")
            return false
        }

        if (!formData.inbound_delivery_reference) {
            showErrorToast("Please enter a delivery reference")
            return false
        }

        if (!formData.received_by) {
            showErrorToast("Please enter who received the delivery")
            return false
        }

        const invalidLine = formData.inbound_delivery_lines_attributes.find(
            (inboundLine) => inboundLine.received_quantity + inboundLine.damaged_quantity > inboundLine.expected_quantity
        )

        if (invalidLine) {
            showErrorToast("Received quantity plus damaged quantity cannot exceed expected quantity")
            return false
        }

        return true
    }

    const resetForm = () => {
        setSelectedInvoice(null)
        setFormData({
            purchase_invoice_id: null,
            purchase_invoice_no: "",
            inbound_delivery_date: new Date().toISOString().split("T")[0],
            inbound_delivery_reference: "",
            received_by: "",
            notes: "",
            inbound_delivery_lines_attributes: [],
            inbound_delivery_attachments_attributes: []
        })
    }

    return {
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
    }
}
