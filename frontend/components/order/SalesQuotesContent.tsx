"use client"

import Image from "next/image"
import { ChevronDown, ChevronUp } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { toast } from "sonner"
import type { SalesQuote } from "@/types/sales-quote"
import { destroySalesQuote } from "@/lib/sales-quote-service"

interface SalesQuotesProps {
    salesQuotes: SalesQuote[],
    expandedOrderId: number | null,
    handleToggleExpand: (orderId: number) => void,
    isCancelling: number | null,
    setIsCancelling: (id: number | null) => void
}

// actual usage is SalesQuotesContent
export default function SalesQuotesContent(
        {
            salesQuotes,
            expandedOrderId,
            handleToggleExpand,
            isCancelling,
            setIsCancelling
        }: SalesQuotesProps
    ) {

    // Handle order cancellation
    const handleDestroySalesQuote = async (orderId: number) => {
        setIsCancelling(orderId)

        try {
            await destroySalesQuote(orderId)
            toast.success("Sales quote cancelled successfully")
            window.location.reload()
        } catch (error) {
            console.error("Failed to cancel sales quote:", error)
            toast.error("Failed to cancel sales quote")
        }
    }

    return (
        <>
            {
                salesQuotes.map((salesQuote: SalesQuote) => (
                    <Card key={salesQuote.id} className="overflow-hidden">
                        <CardHeader className="bg-muted/50">
                            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                                <div>
                                    <CardTitle className="text-lg">Sales Quote #{salesQuote.sales_quote_no}</CardTitle>
                                    <CardDescription>Placed on {new Date(salesQuote.created_at).toLocaleDateString()}</CardDescription>
                                </div>
                                <div className="flex items-center gap-3">
                                    <Badge className="bg-yellow-500 text-white">
                                        PENDING
                                    </Badge>
                                    <Button variant="outline" size="sm" onClick={() => handleToggleExpand(salesQuote.id)}>
                                        {
                                            expandedOrderId === salesQuote.id ? (
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
                            {/* Sales Quotes Summary (Always Visible) */}
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
                                            <p className="text-sm text-muted-foreground">Total: Rp {salesQuote.sum_total_line_amounts.toLocaleString()}</p>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-3">
                                        {
                                            (
                                                <Button 
                                                    variant="destructive"
                                                    size="sm"
                                                    onClick={() => handleDestroySalesQuote(salesQuote.id)}
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
                                expandedOrderId === salesQuote.id && (
                                    <div className="p-6">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                            {/* Left Column - Quoted Items */}
                                            <div>
                                                <h3 className="font-semibold text-lg mb-4">Requested Items</h3>
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
                                                                            Rp {item.price_per_unit.toLocaleString()} x {item.quantity}
                                                                        </p>
                                                                        <p className="font-medium mt-1">Rp {item.total_line_amount.toLocaleString()}</p>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        ))
                                                    }
                                                </div>

                                                <Separator className="my-6" />

                                                {/* Sales Quote Summary */}
                                                <div className="space-y-2">
                                                    <div className="flex justify-between">
                                                        <span className="text-muted-foreground">Subtotal</span>
                                                        <span>Rp {salesQuote.sum_total_line_amounts.toLocaleString()}</span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span className="text-muted-foreground">Tax</span>
                                                        <span>Rp 0</span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span className="text-muted-foreground">Shipping</span>
                                                        <span>Rp 0</span>
                                                    </div>
                                                    {(
                                                        <div className="flex justify-between text-green-600">
                                                            <span>Discount</span>
                                                            <span>Rp -0</span>
                                                        </div>
                                                    )}
                                                    <Separator className="my-2" />

                                                    <div className="flex justify-between font-bold">
                                                        <span>Total</span>
                                                        <span>Rp {salesQuote.total_payable_amount.toLocaleString()}</span>
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
                                                                Available soon
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
        </>
    )
}