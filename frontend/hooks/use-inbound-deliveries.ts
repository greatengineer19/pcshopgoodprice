"use client"

import { useState, useEffect, useCallback } from "react"
import type { InboundDelivery, InboundDeliveryFormData } from "@/types/inbound-delivery"

import { useToastError } from "./use-toast-error"
import { handleApiError } from "@/utils/api/error-handlers"

export function useInboundDeliveries() {
    const [inboundDeliveries, setInboundDeliveries] = useState<InboundDelivery[]>([])
    const { showErrorToast } = useToastError()

    useEffect(() => {
        const loadInboundDeliveries = async () => {
            try {
                const response = await fetch('http://localhost:8080/api/inbound-deliveries')

                if (!response.ok) {
                    await handleApiError(response, showErrorToast);
                    return
                }

                const responseData = await response.json();
                const data: InboundDelivery[] = responseData.inbound_deliveries;
                setInboundDeliveries(data);
            } catch (error) {
                showErrorToast("Unable to load inbound deliveries")
            }
        };

        loadInboundDeliveries()
    }, []);

    // const uploadInboundAttachment = async (inboundId: string, file: File, uploadedBy: string) => {
    //     setIsLoading(true)
    //     try {
    //         const newAttachment = await uploadInboundAttachment(inboundId, file, uploadedBy)

    //         setPurchaseInbounds((prev) =>
    //             prev.map((inbound) => {
    //                 if (inbound.id === inboundId) {
    //                     return {
    //                         ...inbound,
    //                         attachments: [...(inbound.attachments || []), newAttachment]
    //                     }
    //                 }
    //                 return inbound
    //             })
    //         )

    //         if (selectedInbound && selectedInbound.id == inboundId) {
    //             setSelectedInbound({
    //                 ...selectedInbound,
    //                 attachments: [...(selectedInbound.attachments || []), newAttachment]
    //             })
    //         }

    //         toast.success("Attachment uploaded successfully!")
    //         return true
    //     } catch (error) {
    //         toast.error(`Failed to upload attachment: ${(error as Error).message}`, {
    //             style: { backgroundColor: "#D84040", color: "white" }
    //         })
    //         return false
    //     } finally {
    //         setIsLoading(false)
    //     }
    // }

    return {
        inboundDeliveries,
        setInboundDeliveries
    }
}
