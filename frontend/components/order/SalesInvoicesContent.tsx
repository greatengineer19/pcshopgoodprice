"use client"

import Image from "next/image"
import { ChevronDown, ChevronUp } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { toast } from "sonner"
import type { SalesInvoice } from "@/types/sales-invoice"
import { voidSalesInvoice } from "@/lib/sales-invoice-service"

interface SalesInvoiceProps {
    salesInvoices: SalesInvoice[],
    expandedOrderId: number | null,
    expandedResourceType: string | null,
    handleToggleExpand: (orderId: number, resourceType: string) => void
}

// actual usage is SalesInvoicesContent
export default function SalesInvoicesContent(
        {
            salesInvoices,
            expandedOrderId,
            expandedResourceType,
            handleToggleExpand
        }: SalesInvoiceProps
    ) {

    const getStatusColor = (status: string) => {
        switch (status) {
            case "COMPLETED":
                return "bg-blue-500"
            case "PENDING":
                return "bg-yellow-500"
            case "VOID":
                return "bg-red-500"
            default:
                return "bg-gray-500"
        }
    }

    return (
        <>
            {
                salesInvoices.map((salesInvoice: SalesInvoice) => (
                    <Card key={salesInvoice.id} className="overflow-hidden">
                        <CardHeader className="bg-muted/50">
                            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                                <div>
                                    <CardTitle className="text-lg">Sales Invoice #{salesInvoice.sales_invoice_no}</CardTitle>
                                    <CardDescription>Placed on {new Date(salesInvoice.created_at).toLocaleDateString("en-GB", {
                                        day: "numeric",
                                        month: "short", // "Jul" format
                                        year: "numeric",
                                        })}</CardDescription>
                                </div>
                                <div className="flex items-center gap-3">
                                    <Badge className={`${getStatusColor(salesInvoice.status)} text-white`}>
                                        {salesInvoice.status}
                                    </Badge>
                                    <Button variant="outline" size="sm" onClick={() => handleToggleExpand(salesInvoice.id, "SalesInvoice")}>
                                        {
                                            (expandedOrderId === salesInvoice.id && expandedResourceType == "SalesInvoice") ? (
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
                            {/* Sales Invoices Summary (Always Visible) */}
                            <div className="p-6 border-b">
                                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                                    <div className="flex items-center gap-3">
                                        <div className="flex -space-x-4">
                                            {
                                                salesInvoice.sales_invoice_lines.slice(0, 3).map((item, index) => (
                                                    <div
                                                        key={item.id}
                                                        className="relative h-12 w-12 rounded-full border-2 border-background overflow-hidden bg-white"
                                                        style={{ zIndex: 3 - index }}
                                                    >
                                                        <Image 
                                                            src={item.images ? item.images[0] : "/placeholder.svg?height=300&width=300"}
                                                            alt={item.component_name}
                                                            fill
                                                            sizes="(max-width: 768px) 100vw,
                                                                (max-width: 1200px) 50vw,
                                                                33vw"
                                                            className="object-contain p-1"
                                                        />
                                                    </div>
                                                ))
                                            }
                                            {
                                                salesInvoice.sales_invoice_lines.length > 3 && (
                                                    <div className="relative h-12 w-12 rounded-full border-2 border-background bg-muted flex items-center justify-center text-xs font-medium">
                                                        +{salesInvoice.sales_invoice_lines.length - 3}
                                                    </div>
                                                )
                                            }
                                        </div>
                                        <div>
                                            <p className="font-medium">
                                                {salesInvoice.sales_invoice_lines.length} {salesInvoice.sales_invoice_lines.length === 1 ? "item" : "items"}
                                            </p>
                                            <p className="text-sm text-muted-foreground">Total: Rp {Number(salesInvoice.sum_total_line_amounts).toLocaleString()}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Expanded Order Details */}
                            {
                                (expandedOrderId === salesInvoice.id && expandedResourceType == "SalesInvoice") && (
                                    <div className="p-6">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                            {/* Left Column - Quoted Items */}
                                            <div>
                                                <h3 className="font-semibold text-lg mb-4">Requested Items</h3>
                                                <div className="space-y-4">
                                                    {
                                                        salesInvoice.sales_invoice_lines.map((item) => (
                                                            <div key={item.id} className="flex gap-4">
                                                                <div className="relative h-16 w-16 border rounded-md overflow-hidden flex-shrink-0">
                                                                    <Image 
                                                                        src={item.images ? item.images[0] : "/placeholder.svg?height=300&width=300"}
                                                                        alt={item.component_name}
                                                                        fill
                                                                        sizes="(max-width: 768px) 100vw,
                                                                            (max-width: 1200px) 50vw,
                                                                            33vw"
                                                                        className="object-contain p-1"
                                                                    />
                                                                </div>
                                                                <div>
                                                                    <div className="flex-1 min-w-0">
                                                                        <h4 className="font-medium text-sm line-clamp-1">{item.component_name}</h4>
                                                                        <p className="text-sm text-muted-foreground">
                                                                            Rp {Number(item.price_per_unit).toLocaleString()} x {item.quantity}
                                                                        </p>
                                                                        <p className="font-medium mt-1">Rp {Number(item.total_line_amount).toLocaleString()}</p>
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
                                                        <span>Rp {Number(salesInvoice.sum_total_line_amounts).toLocaleString()}</span>
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
                                                        <span>Rp {Number(salesInvoice.total_payable_amount).toLocaleString()}</span>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Right Column - Shipping & Tracking */}
                                            <div>
                                                {/* Shipping Information */}
                                                <h3 className="font-semibold text-lg mb-4">Shipping Information</h3>
                                                <div className="bg-muted/50 p-4 rounded-md mb-6">
                                                    <p className="font-medium">{salesInvoice.customer_name}</p>
                                                    <p>{salesInvoice.shipping_address}</p>
                                                </div>

                                                {/* Payment Information */}
                                                <h3 className="font-semibold text-lg mb-4">Payment Information</h3>
                                                <div className="bg-muted/50 p-4 rounded-md mb-6">
                                                    <div className="flex justify-between mb-2">
                                                        <span>Payment Method</span>
                                                        <span className="font-medium">
                                                            {
                                                                salesInvoice.payment_method_name
                                                            }
                                                        </span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span>Invoice Status</span>
                                                        <Badge className={`${getStatusColor(salesInvoice.status)} text-white`}>
                                                            {salesInvoice.status}
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