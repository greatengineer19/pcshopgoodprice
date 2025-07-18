"use client"

import Image from "next/image"
import { ChevronDown, ChevronUp } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { toast } from "sonner"
import type { SalesDelivery } from "@/types/sales-delivery"
import { voidSalesDelivery } from "@/lib/sales-delivery-service"

interface SalesDeliveryProps {
    salesDeliveries: SalesDelivery[],
    expandedOrderId: number | null,
    handleToggleExpand: (orderId: number) => void,
    isCancelling: number | null,
    setIsCancelling: (id: number | null) => void
}

// actual usage is SalesDeliveriesContent
export default function SalesDeliveriesContent(
        {
            salesDeliveries,
            expandedOrderId,
            handleToggleExpand,
            isCancelling,
            setIsCancelling
        }: SalesDeliveryProps
    ) {

    // Handle order cancellation
    const handleVoidSalesDelivery = async (orderId: number) => {
        setIsCancelling(orderId)

        try {
            await voidSalesDelivery(orderId)
            toast.success("Sales delivery voided successfully")
            window.location.reload()
        } catch (error) {
            console.error("Failed to cancel sales delivery:", error)
            toast.error("Failed to cancel sales delivery")
        }
    }

    const getStatusColor = (status: string) => {
        switch (status) {
            case "DELIVERED":
                return "bg-blue-500"
            case "PROCESSING":
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
                salesDeliveries.map((salesDelivery) => (
                    <Card key={salesDelivery.id} className="overflow-hidden">
                        <CardHeader className="bg-muted/50">
                            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                                <div>
                                    <CardTitle className="text-lg">Sales Delivery #{salesDelivery.sales_delivery_no}</CardTitle>
                                    <CardDescription>Placed on {new Date(salesDelivery.created_at).toLocaleDateString()}</CardDescription>
                                </div>
                                <div className="flex items-center gap-3">
                                    <Badge className={`${getStatusColor(salesDelivery.status)} text-white`}>
                                        {salesDelivery.status}
                                    </Badge>
                                    <Button variant="outline" size="sm" onClick={() => handleToggleExpand(salesDelivery.id)}>
                                        {
                                            expandedOrderId === salesDelivery.id ? (
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
                            {/* Sales Delivery Summary (Always Visible) */}
                            <div className="p-6 border-b">
                                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                                    <div className="flex items-center gap-3">
                                        <div className="flex -space-x-4">
                                            {
                                                salesDelivery.sales_delivery_lines.slice(0, 3).map((item, index) => (
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
                                                salesDelivery.sales_delivery_lines.length > 3 && (
                                                    <div className="relative h-12 w-12 rounded-full border-2 border-background bg-muted flex items-center justify-center text-xs font-medium">
                                                        +{salesDelivery.sales_delivery_lines.length - 3}
                                                    </div>
                                                )
                                            }
                                        </div>
                                        <div>
                                            <p className="font-medium">
                                                {salesDelivery.sales_delivery_lines.length} {salesDelivery.sales_delivery_lines.length === 1 ? "item" : "items"}
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-3">
                                        {
                                            (
                                                <Button 
                                                    variant="destructive"
                                                    size="sm"
                                                    onClick={() => handleVoidSalesDelivery(salesDelivery.id)}
                                                    disabled={isCancelling === salesDelivery.id}
                                                >
                                                    {
                                                        isCancelling === salesDelivery.id ? "Cancelling..." : "Void Sales Delivery"
                                                    }
                                                </Button>
                                            )
                                        }
                                    </div>
                                </div>
                            </div>

                            {/* Expanded Order Details */}
                            {
                                expandedOrderId === salesDelivery.id && (
                                    <div className="p-6">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                            {/* Left Column - Quoted Items */}
                                            <div>
                                                <h3 className="font-semibold text-lg mb-4">Requested Items</h3>
                                                <div className="space-y-4">
                                                    {
                                                        salesDelivery.sales_delivery_lines.map((item) => (
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
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        ))
                                                    }
                                                </div>
                                            </div>

                                            {/* Right Column - Shipping & Tracking */}
                                            <div>
                                                {/* Shipping Information */}
                                                <h3 className="font-semibold text-lg mb-4">Shipping Information</h3>
                                                <div className="bg-muted/50 p-4 rounded-md mb-6">
                                                    <p className="font-medium">{salesDelivery.customer_name}</p>
                                                    <p>{salesDelivery.shipping_address}</p>
                                                </div>

                                                {/* Payment Information */}
                                                <h3 className="font-semibold text-lg mb-4">Payment Information</h3>
                                                <div className="bg-muted/50 p-4 rounded-md mb-6">
                                                    <div className="flex justify-between">
                                                        <span>Status</span>
                                                        <Badge className={`${getStatusColor(salesDelivery.status)} text-white`}>
                                                            {salesDelivery.status}
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