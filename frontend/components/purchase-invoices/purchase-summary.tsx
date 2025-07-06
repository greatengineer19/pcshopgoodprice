"use client"

import Image from "next/image"
import { Plus, Minus, Trash2 } from "lucide-react"
import type { OnEditPurchaseInvoiceLine } from "@/types/purchase-invoice"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Separator } from "@/components/ui/separator"

interface ParamsProps {
    selectedInvoiceLines: OnEditPurchaseInvoiceLine[]
    supplierName: string
    setSupplierName: (value: string) => void
    expectedDeliveryDate: string
    setExpectedDeliveryDate: (value: string) => void
    procurementNote: string
    setProcurementNote: (value: string) => void
    onUpdateQuantity: (productId: number, quantity: number) => void
    onRemoveProduct: (productId: number) => void
    total: number
}

export function PurchaseSummary({
    selectedInvoiceLines,
    supplierName,
    setSupplierName,
    expectedDeliveryDate,
    setExpectedDeliveryDate,
    procurementNote,
    setProcurementNote,
    onUpdateQuantity,
    onRemoveProduct,
    total,
}: ParamsProps) {
    return (
        <div className="space-4-y">
            <h3 className="text-lg font-medium">Purchase Summary</h3>

            <div className="space-y-4">
                <div className="grid grid-cols-1 gap-4">
                    <div className="space-y-2">
                        <Label htmlFor="supplier-name" className="required">
                            Supplier Name
                        </Label>
                        <Input 
                            id="supplier-name"
                            placeholder="Enter supplier name"
                            value={supplierName}
                            onChange={(e) => setSupplierName(e.target.value)}
                            required
                        />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="delivery-date">Expected Delivery Date</Label>
                        <Input 
                            id="delivery-date"
                            type="date"
                            value={expectedDeliveryDate}
                            onChange={(e) => setExpectedDeliveryDate(e.target.value)}
                        />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="procurement-note">Procurement Note</Label>
                        <Textarea 
                            id="procurement-note"
                            placeholder="Add notes about this procurement..."
                            value={procurementNote}
                            onChange={(e) => setProcurementNote(e.target.value)}
                            rows={3}
                        />
                    </div>

                    <Separator />
        
                    <div>
                        <h4 className="font-medium mb-2">Selected Products</h4>
                        {selectedInvoiceLines.length === 0 ? (
                            <div className="text-center py-4 text-muted-foreground border rounded-md">
                                No products selected yet
                            </div>
                        ) : (
                            <div className="space-y-2 max-h-[200px] overflow-y-auto border rounded-md p-2">
                                {selectedInvoiceLines.map((invoiceLine) => (
                                    <div key={invoiceLine.component_id} className="flex items-center justify-between border-b pb-2">
                                        <div className="flex items-center space-x-2">
                                            <div className="relative h-8 w-8 rounded overfloww-hidden">
                                                <Image
                                                    src={"/placeholder.svg"}
                                                    alt={invoiceLine.component_name}
                                                    fill
                                                    className="object-cover"
                                                />
                                            </div>
                                            <span className="text-sm font-medium">
                                                {invoiceLine.component_name}
                                            </span>
                                        </div>
                                        <div className="flex items-center space-x-1">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => onUpdateQuantity(Number(invoiceLine.component_id), (invoiceLine.quantity || 1) - 1)}
                                                className="h-6 w-6 p-0"
                                            >
                                                <Minus className="h-3 w-3" />
                                            </Button>
                                            <span className="w-6 text-center text-sm">{invoiceLine.quantity}</span>
                                            <Button 
                                                variant="outline"
                                                size="sm"
                                                onClick={() => onUpdateQuantity(Number(invoiceLine.component_id), (invoiceLine.quantity || 1) + 1)}
                                                className="h-6 w-6 p-0"
                                            >
                                                <Plus className="h-3 w-3" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => onRemoveProduct(Number(invoiceLine.component_id))}
                                                className="h-6 w-6 p-0 text-destructive"
                                            >
                                                <Trash2 className="h-3 w-3" />
                                            </Button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="flex justify-between font-medium text-lg">
                        <span>Total:</span>
                        <span>${total.toFixed(2)}</span>
                    </div>
                </div>
            </div>
        </div>
    )
}