"use client"

import Image from "next/image"
import { Calendar, User, Edit } from "lucide-react"
import type { PurchaseInvoice } from "@/types/purchase-invoice"
import { getStatusColor } from "@/utils/status-utils"

import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
    DialogDescription,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

interface ParamsProps {
    invoice: PurchaseInvoice | null
    isViewModalOpen: boolean
    closeViewModal: () => void
    onEditModal: (invoice: PurchaseInvoice) => void
}

export function PurchaseViewModal({ invoice, isViewModalOpen, closeViewModal, onEditModal }:
    ParamsProps
) {
    if (!invoice) return null

    return (
        <Dialog open={isViewModalOpen} onOpenChange={closeViewModal}>
            <DialogContent className="max-w-[95vw] w-[1400px]">
                <DialogHeader>
                    <DialogTitle className="text-xl font-bold">Purchase Invoice Detail</DialogTitle>
                    <DialogDescription>Invoice #{invoice.purchase_invoice_no}</DialogDescription>
                </DialogHeader>

                <div className="space-y-6 py-6">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <h4 className="text-sm font-medium text-muted-foreground mb-1">Invoice Date</h4>
                            <p className="flex items-center">
                                <Calendar className="h-4 w-4 mr-2 text-muted-foreground" />
                                {new Date(invoice.invoice_date).toLocaleDateString("en-GB", {
                                    day: "2-digit",
                                    month: "long",
                                    year: "numeric",
                                })}
                            </p>
                        </div>
                        <div>
                            <h4 className="text-sm font-medium text-muted-foreground mb-1">Status</h4>
                            <Badge className={`${getStatusColor(invoice.status)} text-white`}>
                                {invoice.status}
                            </Badge>
                        </div>
                        <div>
                            <h4 className="text-sm font-medium text-muted-foreground mb-1">
                                Supplier
                            </h4>
                            <p className="flex items-center">
                                <User className="h-4 w-4 mr-2 text-muted-foreground" />
                                {invoice.supplier_name}
                            </p>
                        </div>
                        <div>
                            <h4 className="text-sm font-medium text-muted-foreground mb-1">
                                Expected Delivery
                            </h4>
                            <p>{invoice.expected_delivery_date 
                                ? new Date(invoice.expected_delivery_date).toLocaleDateString("en-GB", {
                                    day: "numeric",
                                    month: "long",
                                    year: "numeric",
                                    })
                                : "Not Specified"}
                            </p>
                        </div>
                    </div>

                    {
                        invoice.notes && (
                            <div>
                                <h4 className="text-sm font-medium text-muted-foreground mb-1">Notes</h4>
                                <p className="text-sm bg-muted p-2 rounded">{invoice.notes}</p>
                            </div>
                        )
                    }

                    <Separator />

                    <div>
                        <h4 className="font-medium mb-2">Products</h4>
                        <div className="rounded-md border">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Product</TableHead>
                                        <TableHead className="text-center">Quantity</TableHead>
                                        <TableHead className="text-right">Unit Price</TableHead>
                                        <TableHead className="text-right">Total</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {invoice.purchase_invoice_lines.map((invoice_line) => (
                                        <TableRow key={invoice_line.id}>
                                            <TableCell
                                                className="font-medium flex items-center gap-2"
                                            >
                                                {invoice_line.component_name}
                                            </TableCell>
                                            <TableCell className="text-center">{invoice_line.quantity}</TableCell>
                                            <TableCell className="text-right">{Number(invoice_line.price_per_unit).toLocaleString()}</TableCell>
                                            <TableCell className="text-right">Rp {Number(invoice_line.total_line_amount).toLocaleString()}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </div>
                    </div>

                    <div className="flex justify-end gap-8 font-medium text-lg text-right">
                        <span>Total Amount:</span>
                        <span>Rp {Number(invoice.sum_total_line_amounts).toLocaleString()}</span>
                    </div>
                </div>
                <DialogFooter>
                    <Button type="button" variant="outline" onClick={closeViewModal}>
                        Close
                    </Button>
                    <Button
                        type="button"
                        onClick={() => {
                            closeViewModal()
                            onEditModal(invoice)
                        }}
                    >
                        <Edit className="h-4 w-4 mr-2" />
                        Edit
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}