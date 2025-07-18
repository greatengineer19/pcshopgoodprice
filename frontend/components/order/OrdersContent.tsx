"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { FileText } from "lucide-react"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"
import { fetchSalesQuotes } from "@/lib/sales-quote-service"
import { fetchSalesInvoices } from "@/lib/sales-invoice-service"
import { fetchSalesDeliveries } from "@/lib/sales-delivery-service"
import type { SalesQuote } from "@/types/sales-quote"
import { SalesDelivery } from "@/types/sales-delivery"
import { SalesInvoice } from "@/types/sales-invoice"
import SalesQuotesContent from "./SalesQuotesContent"
import SalesDeliveriesContent from "./SalesDeliveriesContent"
import SalesInvoicesContent from "./SalesInvoicesContent"

// actual usage is SalesQuotesContent, SalesInvoicesContent, SalesDeliveriesContent
export default function OrdersContent() {
    const [salesQuotes, setSalesQuotes] = useState<SalesQuote[]>([])
    const [salesInvoices, setSalesInvoices] = useState<SalesInvoice[]>([])
    const [salesDeliveries, setSalesDeliveries] = useState<SalesDelivery[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [expandedOrderId, setExpandedOrderId] = useState<number | null>(null)
    const [isCancelling, setIsCancelling] = useState<number | null>(null)

    // Load Sales Quotes
    useEffect(() => {
        const loadSalesQuotes = async () => {
            setIsLoading(true)
            try {
                const salesQuotesData = await fetchSalesQuotes()

                setSalesQuotes(salesQuotesData)
            } catch (error) {
                console.error("Failed to Sales Quotes:", error)
                toast.error("Failed to load your Sales Quotes")
            }
        }

        const loadSalesInvoices = async () => {
            setIsLoading(true)

            try {
                const salesInvoicesData = await fetchSalesInvoices()

                setSalesInvoices(salesInvoicesData)
            } catch (error) {
                console.error("Failed to Sales Invoices:", error)
                toast.error("Failed to load your Sales Invoices")
            }
        }

        const loadSalesDeliveries = async () => {
            setIsLoading(true)

            try {
                const salesInvoicesData = await fetchSalesDeliveries()

                setSalesDeliveries(salesInvoicesData)
            } catch (error) {
                console.error("Failed to Sales Deliveries:", error)
                toast.error("Failed to load your Sales Deliveries")
            }
        }

        loadSalesQuotes()
        loadSalesInvoices()
        loadSalesDeliveries()
        setIsLoading(false)
    }, [])

    // Load shipping updates when an order is expanded
    const handleToggleExpand = (orderId: number) => {
        if (expandedOrderId === orderId) {
            setExpandedOrderId(null)
            return
        }

        setExpandedOrderId(orderId)
    }

    // Empty orders view
    if (!isLoading && salesQuotes.length === 0) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
                    <FileText className="h-16 w-16 text-muted-foreground mb-4" />
                    <h1 className="text-3xl font-bold mb-4">Your Orders</h1>
                    <p className="text-muted-foreground mb-8 max-w-md">
                        View and track all your orders in one place. You don't have any orders yet.
                    </p>
                    <Link href="/shop">
                        <Button className="flex items-center gap-2">Start Shopping</Button>
                    </Link>
                </div>
            </div>
        )
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-8">Your Orders</h1>

            {
                isLoading ? (
                    <div className="flex justify-center items-center h-64">
                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
                    </div>
                ) : (
                    <div className="space-y-6">
                        <SalesDeliveriesContent 
                            salesDeliveries={salesDeliveries}
                            expandedOrderId={expandedOrderId}
                            handleToggleExpand={handleToggleExpand}
                            isCancelling={isCancelling}
                            setIsCancelling={setIsCancelling}
                        />
                        <SalesInvoicesContent 
                            salesInvoices={salesInvoices}
                            expandedOrderId={expandedOrderId}
                            handleToggleExpand={handleToggleExpand}
                            isCancelling={isCancelling}
                            setIsCancelling={setIsCancelling}
                        />
                        <SalesQuotesContent 
                            salesQuotes={salesQuotes}
                            expandedOrderId={expandedOrderId}
                            handleToggleExpand={handleToggleExpand}
                            isCancelling={isCancelling}
                            setIsCancelling={setIsCancelling}
                        />
                    </div>
                )
            }
        </div>
    )
}