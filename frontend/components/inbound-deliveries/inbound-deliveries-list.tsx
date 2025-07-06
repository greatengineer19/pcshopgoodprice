"use client"

import { useState } from "react"
import { Search, Eye, Trash2, Package } from "lucide-react"

import type { InboundDelivery } from "@/types/inbound-delivery"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useInboundDeliveries } from "@/hooks/use-inbound-deliveries"

interface ParamsProps {
    handleView: (inboundDelivery: InboundDelivery) => void
    handleDelete: (inboundDelivery: InboundDelivery) => void
}

export function InboundDeliveriesList({ handleView, handleDelete }: ParamsProps) {
    const {
        inboundDeliveries,
        setInboundDeliveries
    } = useInboundDeliveries()

    const [searchTerm, setSearchTerm] = useState("")

    const filteredDeliveries = inboundDeliveries.filter(
        (inboundDelivery: InboundDelivery) =>
            inboundDelivery.inbound_delivery_no.toLowerCase().includes(searchTerm.toLowerCase()) ||
            inboundDelivery.purchase_invoice_no.toLowerCase().includes(searchTerm.toLowerCase()) ||
            inboundDelivery.inbound_delivery_reference.toLowerCase().includes(searchTerm.toLowerCase()) ||
            inboundDelivery.received_by.toLowerCase().includes(searchTerm.toLowerCase())
    )

    return (
        <Card>
            <CardHeader>
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div>
                        <CardTitle>Inbound Deliveries History</CardTitle>
                        <CardDescription>View and manage all Inbound Deliveries</CardDescription>
                    </div>
                    <div className="w-full sm:w-auto">
                        <div className="relative">
                            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                            <Input 
                                placeholder="Search inbound deliveries..."
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
                            <TableRow>
                                <TableHead>Ib. Delivery No #</TableHead>
                                <TableHead>Invoice No #</TableHead>
                                <TableHead>Ib. Delivery Date</TableHead>
                                <TableHead>Ib. Delivery Reference</TableHead>
                                <TableHead>Received By</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead className="text-center">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {filteredDeliveries.length === 0 ? (
                                <TableRow key="no_keys">
                                    <TableCell colSpan={7} className="text-center py-4 text-muted-foreground">
                                        No inbound deliveries found
                                    </TableCell>
                                </TableRow>
                            ): (
                                filteredDeliveries.map((inboundDelivery) => (
                                    <TableRow key={inboundDelivery.id}>
                                        <TableCell className="font-medium">{inboundDelivery.inbound_delivery_no}</TableCell>
                                        <TableCell>{inboundDelivery.purchase_invoice_no}</TableCell>
                                        <TableCell>{new Date(inboundDelivery.inbound_delivery_date).toLocaleDateString()}</TableCell>
                                        <TableCell>{inboundDelivery.inbound_delivery_reference}</TableCell>
                                        <TableCell>{inboundDelivery.received_by}</TableCell>
                                        <TableCell>
                                            <Badge className="bg-green-500 text-white">{inboundDelivery.status}</Badge>
                                        </TableCell>
                                        <TableCell>
                                            <div className="flex justify-center">
                                                <DropdownMenu>
                                                    <DropdownMenuTrigger asChild>
                                                        <Button variant="ghost" className="h-8 w-8 p-0">
                                                            <span className="sr-only">Open menu</span>
                                                            <Package className="h-4 w-4" />
                                                        </Button>
                                                    </DropdownMenuTrigger>
                                                    <DropdownMenuContent align="end">
                                                        <DropdownMenuLabel>Actions</DropdownMenuLabel>
                                                        <DropdownMenuSeparator />
                                                        <DropdownMenuItem onClick={() => handleView(inboundDelivery)}>
                                                            <Eye className="mr-2 h-4 w-4" />
                                                            View Details
                                                        </DropdownMenuItem>
                                                        <DropdownMenuItem
                                                            onClick={() => handleDelete(inboundDelivery)}
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