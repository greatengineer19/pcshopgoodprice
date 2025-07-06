"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import Image from "next/image"
import { FileText, Package, Truck, CheckCircle, Clock, AlertTriangle, ChevronDown, ChevronUp } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { toast } from "sonner"
import { fetchSalesQuotes, cancelSalesQuote } from "@/lib/sales-quote-service"
import type { FetchedSalesQuote } from "@/types/sales-quote"

// actual usage is SalesQuoteContent
export default function OrderContent() {
    const [salesQuotes, setSalesQuotes] = useState<FetchedSalesQuote[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [expandedOrder, setExpandedOrder] = useState<number | null>(null)
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
            } finally {
                setIsLoading(false)
            }
        }

        loadSalesQuotes()
    }, [])

    // Load shipping updates when an order is expanded
    const handleToggleExpand = (orderId: number) => {
        if (expandedOrder === orderId) {
            setExpandedOrder(null)
            return
        }

        setExpandedOrder(orderId)
    }

    // Handle order cancellation
    const handleCancelOrder = async (orderId: number) => {
        setIsCancelling(orderId)

        try {
            const updatedOrder = await cancelSalesQuote(orderId)

            // Update the order in the list
            setSalesQuotes((prev) => prev.map((order) => (order.id === orderId ? updatedOrder : order)))

            toast.success("Sales quote cancelled successfully")
        } catch (error) {
            console.error("Failed to cancel order:", error)
            toast.error("Failed to cancel order")
        } finally {
            setIsCancelling(null)
        }
    }

    // Get status color based on order status
    const getStatusColor = (status: string) => {
        switch (status) {
            case "completed":
                return "bg-green-500"
            case "in_progress":
                return "bg-blue-500"
            case "pending":
                return "bg-yellow-500"
            case "cancelled":
                return "bg-red-500"
            default:
                return "bg-gray-500"
        }
    }

    // Format status text
    const formatStatus = (status: string) => {
        return status
            .split("_")
            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
            .join(" ")
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
                        {
                            salesQuotes.map((salesQuote) => (
                                <Card key={salesQuote.id} className="overflow-hidden">
                                    <CardHeader className="bg-muted/50">
                                        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                                            <div>
                                                <CardTitle className="text-lg">Sales Quote #{salesQuote.sales_quote_no}</CardTitle>
                                                <CardDescription>Placed on {new Date(salesQuote.created_at).toLocaleDateString()}</CardDescription>
                                            </div>
                                            <div className="flex items-center gap-3">
                                                <Badge className={`${getStatusColor("pending")} text-white`}>
                                                    {formatStatus("pending")}
                                                </Badge>
                                                <Button variant="outline" size="sm" onClick={() => handleToggleExpand(salesQuote.id)}>
                                                    {
                                                        expandedOrder === salesQuote.id ? (
                                                            <>
                                                                Hide details <ChevronUp className="ml-1 h-4 w-4" />
                                                            </>
                                                        ) : (
                                                            <>
                                                                View Details <ChevronDown className="ml-1 h-4 w-4" />
                                                            </>
                                                        )
                                                    }
                                                </Button>
                                            </div>
                                        </div>
                                    </CardHeader>

                                    <CardContent className="p-0">
                                        {/* Order Summary (Always Visible) */}
                                        <div className="p-6 border-b">
                                            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="flex -space-x-4">
                                                        {
                                                            salesQuote.sales_quote_lines.slice(0, 3).map((item, index) => (
                                                                <div
                                                                    key={item.id}
                                                                    className="relative h-12 w-12 rounded-full border-2 border-background overflow-hidden bg-white"
                                                                    style={{ zIndex: 3 - index }}
                                                                >
                                                                    <Image 
                                                                        src={"/placeholder.svg"}
                                                                        alt={item.component_name}
                                                                        fill
                                                                        className="object-contain p-1"
                                                                    />
                                                                </div>
                                                            ))
                                                        }
                                                        {
                                                            salesQuote.sales_quote_lines.length > 3 && (
                                                                <div className="relative h-12 w-12 rounded-full border-2 border-background bg-muted flex items-center justify-center text-xs font-medium">
                                                                    +{salesQuote.sales_quote_lines.length - 3}
                                                                </div>
                                                            )
                                                        }
                                                    </div>
                                                    <div>
                                                        <p className="font-medium">
                                                            {salesQuote.sales_quote_lines.length} {salesQuote.sales_quote_lines.length === 1 ? "item" : "items"}
                                                        </p>
                                                        <p className="text-sm text-muted-foreground">Total: IDR {salesQuote.sum_total_line_amounts.toFixed(2)}</p>
                                                    </div>
                                                </div>

                                                <div className="flex items-center gap-3">
                                                    {
                                                        (
                                                            <Button 
                                                                variant="destructive"
                                                                size="sm"
                                                                onClick={() => handleCancelOrder(salesQuote.id)}
                                                                disabled={isCancelling === salesQuote.id}
                                                            >
                                                                {
                                                                    isCancelling === salesQuote.id ? "Cancelling..." : "Cancel Order"
                                                                }
                                                            </Button>
                                                        )
                                                    }
                                                </div>
                                            </div>
                                        </div>

                                        {/* Expanded Order Details */}
                                        {
                                            expandedOrder === salesQuote.id && (
                                                <div className="p-6">
                                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                                        {/* Left Column - Quoted Items */}
                                                        <div>
                                                            <h3 className="font-semibold text-lg mb-4">Quoted Items</h3>
                                                            <div className="space-y-4">
                                                                {
                                                                    salesQuote.sales_quote_lines.map((item) => (
                                                                        <div key={item.id} className="flex gap-4">
                                                                            <div className="relative h-16 w-16 border rounded-md overflow-hidden flex-shrink-0">
                                                                                <Image 
                                                                                    src={"/placeholder.svg"}
                                                                                    alt={item.component_name}
                                                                                    fill
                                                                                    className="object-contain p-1"
                                                                                />
                                                                            </div>
                                                                            <div>
                                                                                <div className="flex-1 min-w-0">
                                                                                    <h4 className="font-medium text-sm line-clamp-1">{item.component_name}</h4>
                                                                                    <p className="text-sm text-muted-foreground">
                                                                                        IDR {item.price_per_unit.toFixed(2)} x {item.quantity}
                                                                                    </p>
                                                                                    <p className="font-medium mt-1">IDR {item.total_line_amount.toFixed(2)}</p>
                                                                                </div>
                                                                            </div>
                                                                        </div>
                                                                    ))
                                                                }
                                                            </div>

                                                            <Separator className="my-6" />

                                                            {/* Order Summary */}
                                                            <div className="space-y-2">
                                                                <div className="flex justify-between">
                                                                    <span className="text-muted-foreground">Subtotal</span>
                                                                    <span>IDR {salesQuote.sum_total_line_amounts.toFixed(2)}</span>
                                                                </div>
                                                                <div className="flex justify-between">
                                                                    <span className="text-muted-foreground">Tax</span>
                                                                    <span>IDR 0</span>
                                                                </div>
                                                                <div className="flex justify-between">
                                                                    <span className="text-muted-foreground">Shipping</span>
                                                                    <span>IDR 0</span>
                                                                </div>
                                                                {(
                                                                    <div className="flex justify-between text-green-600">
                                                                        <span>Discount</span>
                                                                        <span>IDR -0</span>
                                                                    </div>
                                                                )}
                                                                <Separator className="my-2" />

                                                                <div className="flex justify-between font-bold">
                                                                    <span>Total</span>
                                                                    <span>${salesQuote.total_payable_amount.toFixed(2)}</span>
                                                                </div>
                                                            </div>
                                                        </div>

                                                        {/* Right Column - Shipping & Tracking */}
                                                        <div>
                                                            {/* Shipping Information */}
                                                            <h3 className="font-semibold text-lg mb-4">Shipping Information</h3>
                                                            <div className="bg-muted/50 p-4 rounded-md mb-6">
                                                                <p className="font-medium">{salesQuote.customer_name}</p>
                                                                <p>{salesQuote.shipping_address}</p>
                                                            </div>

                                                            {/* Payment Information */}
                                                            <h3 className="font-semibold text-lg mb-4">Payment Information</h3>
                                                            <div className="bg-muted/50 p-4 rounded-md mb-6">
                                                                <div className="flex justify-between mb-2">
                                                                    <span>Payment Method</span>
                                                                    <span className="font-medium">
                                                                        {
                                                                            salesQuote.payment_method_name
                                                                        }
                                                                    </span>
                                                                </div>
                                                                <div className="flex justify-between">
                                                                    <span>Payment Status</span>
                                                                    <Badge className={"bg-yellow-500"}>
                                                                        Pending
                                                                    </Badge>
                                                                </div>
                                                            </div>

                                                            {/* Tracking Information */}
                                                            {
                                                                (
                                                                    <>
                                                                        <h3 className="font-semibold text-lg mb-4">Tracking Information</h3>
                                                                        <div className="relative border-l-2 border-muted pl-6 space-y-6 ml-2">
                                                                            TO-DO
                                                                        </div>
                                                                    </>
                                                                )
                                                            }
                                                        </div>
                                                    </div>
                                                </div>
                                            )
                                        }
                                    </CardContent>
                                </Card>
                            ))
                        }
                    </div>
                )
            }
        </div>
    )
}