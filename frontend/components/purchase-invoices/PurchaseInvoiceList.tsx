"use client"

import { useState } from "react"
import { usePurchaseInvoices } from "@/hooks/use-purchase-invoices"

import { Search, FileText, Eye, Edit, Trash2 } from "lucide-react"
import type { PurchaseInvoice } from "@/types/purchase-invoice"
import { getStatusColor } from "@/utils/status-utils"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"


interface ParamsProps {
    onViewModal: (invoice: PurchaseInvoice) => void,
    onEditModal: (invoice: PurchaseInvoice) => void,
    onDeleteInvoice: (invoice: PurchaseInvoice) => void
}

export function PurchaseInvoiceList({
        onViewModal,
        onEditModal,
        onDeleteInvoice
    }: ParamsProps) {
    
    const { purchase_invoices } = usePurchaseInvoices()
    
    const [searchTerm, setSearchTerm] = useState("")
    const filteredInvoices = purchase_invoices.filter(
        (invoice: PurchaseInvoice) =>
            invoice.purchase_invoice_no.toLowerCase().includes(searchTerm.toLowerCase()) ||
                invoice.supplier_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                invoice.status.toLowerCase().includes(searchTerm.toLowerCase()),
    )

    return (
        <Card>
            <CardHeader>
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div>
                        <CardTitle>View and manage all purchase invoices</CardTitle>
                    </div>
                    <div className="w-full sm:w-auto">
                        <div className="relative">
                            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                            <Input 
                                placeholder="Search invoices..."
                                className="pl-8 w-full sm:w-[250px]"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="rounded-md border">
                    <Table>
                        <TableHeader>
                            <TableRow key="header-row">
                                <TableHead>Invoice #</TableHead>
                                <TableHead>Date</TableHead>
                                <TableHead>Supplier</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead className="text-right">Total</TableHead>
                                <TableHead className="text-center">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {filteredInvoices.length === 0 ? (
                                <TableRow key="no-invoices">
                                    <TableCell colSpan={6} className="text-center py-4 text-muted-foreground">
                                        No invoices found
                                    </TableCell>
                                </TableRow>
                            ) : (
                                filteredInvoices.map((invoice: PurchaseInvoice) => (
                                    <TableRow key={invoice.id}>
                                        <TableCell className="font-medium">{invoice.purchase_invoice_no}</TableCell>
                                        <TableCell>{new Date(invoice.invoice_date).toLocaleDateString("en-GB", {
                                            day: "2-digit",
                                            month: "long",
                                            year: "numeric",
                                        })}
                                        </TableCell>
                                        <TableCell>{invoice.supplier_name}</TableCell>
                                        <TableCell>
                                            {(() => {
                                                const badgeColor = getStatusColor(invoice.status);
                                                return (
                                                    <Badge 
                                                        variant="outline"
                                                        className={`${badgeColor} text-white px-2 py-1 min-w-[80px] text-center border-none`}
                                                    >
                                                        {invoice.status.toUpperCase()}
                                                    </Badge>
                                                );
                                            })()}
                                        </TableCell>
                                        <TableCell className="text-right">
                                            Rp {Number(invoice.sum_total_line_amounts).toLocaleString()}
                                        </TableCell>
                                        <TableCell>
                                            <div className="flex justify-center">
                                                <DropdownMenu>
                                                    <DropdownMenuTrigger asChild>
                                                        <Button variant="ghost" className="h-8 w-8 p-0">
                                                            <span className="sr-only">
                                                                Open menu
                                                            </span>
                                                            <FileText className="h-4 w-4" />
                                                        </Button>
                                                    </DropdownMenuTrigger>
                                                    <DropdownMenuContent align="end">
                                                        <DropdownMenuLabel>Actions</DropdownMenuLabel>
                                                        <DropdownMenuSeparator />
                                                        <DropdownMenuItem 
                                                            onClick={() => onViewModal(invoice)}
                                                        >
                                                            <Eye className="mr-2 h-4 w-4" />
                                                            View Details   
                                                        </DropdownMenuItem>
                                                        <DropdownMenuItem
                                                            onClick={() => onEditModal(invoice)}
                                                        >
                                                            <Edit className="mr-2 h-4 w-4"/>
                                                            Edit
                                                        </DropdownMenuItem>
                                                        <DropdownMenuItem
                                                            onClick={() => onDeleteInvoice(invoice)}
                                                            className="text-destructive focus:text-destructive"
                                                        >
                                                            <Trash2 className="mr-2 h-4 w-4" />
                                                            Delete
                                                        </DropdownMenuItem>
                                                    </DropdownMenuContent>
                                                </DropdownMenu>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </div>
            </CardContent>
        </Card>
    )
}