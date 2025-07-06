"use client"

import { useState } from "react"
import Image from "next/image"
import { Calendar, User, Package, FileText, ChevronLeft, ChevronRight, X } from "lucide-react"
import type { InboundDelivery } from "@/types/inbound-delivery"

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
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface ParamsProps {
    inboundDelivery: InboundDelivery | null
    isOpen: boolean
    onClose: () => void
}

export function InboundViewModal({ inboundDelivery, isOpen, onClose }: ParamsProps) {
    const [activeTab, setActiveTab] = useState("details")
    const [currentImageIndex, setCurrentImageIndex] = useState(0)
    const [isGalleryOpen, setIsGalleryOpen] = useState(false)

    if (!inboundDelivery) return null

    const imageAttachments = inboundDelivery.inbound_delivery_attachments || []

    const nextImage = () => {
        setCurrentImageIndex((prev) => (prev + 1) % imageAttachments.length)
    }

    const prevImage = () => {
        setCurrentImageIndex((prev) => (prev - 1 + imageAttachments.length) % imageAttachments.length)
    }

    const openGallery = (index: number) => {
        setCurrentImageIndex(index)
        setIsGalleryOpen(true)
    }

    return (
        <>
            <Dialog open={isOpen} onOpenChange={onClose}>
                <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle className="text-xl font-bold">Inbound Delivery Detail</DialogTitle>
                        <DialogDescription>Inbound #{inboundDelivery.inbound_delivery_no}</DialogDescription>
                    </DialogHeader>

                    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                        <TabsList className="grid w-full grid-cols-2 mb-4">
                            <TabsTrigger value="details" className="w-full">Details</TabsTrigger>
                            <TabsTrigger value="attachments" className="w-full">Attachments ({imageAttachments.length})</TabsTrigger>
                        </TabsList>

                        <TabsContent value="details" className="space-y-6">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <h4 className="text-sm font-medium text-muted-foreground mb-1">Invoice</h4>
                                    <p className="flex items-center">
                                        <FileText className="h-4 w-4 mr-2 text-mutted-foreground" />
                                        {inboundDelivery.purchase_invoice_no}
                                    </p>
                                </div>
                                <div>
                                    <h4 className="text-sm font-medium text-muted-foreground mb-1">Status</h4>
                                    <Badge className="bg-green-500 text-white">{inboundDelivery.status}</Badge>
                                </div>
                                <div>
                                    <h4 className="text-sm font-medium textt-muted-foreground mb-1">Inbound Date</h4>
                                    <p className="flex items-center">
                                        <Calendar className="h-4 w-4 mr-2 text-muted-foreground" />
                                        { new Date(inboundDelivery.inbound_delivery_date).toLocaleDateString() }
                                    </p>
                                </div>
                                <div>
                                    <h4 className="text-sm font-medium text-muted-foreground mb-1">Reference</h4>
                                    <p>{inboundDelivery.inbound_delivery_reference}</p>
                                </div>
                                <div>
                                    <h4 className="text-sm font-medium text-muted-foreground mb-1">Received By</h4>
                                    <p className="flex items-center">
                                        <User className="h-4 w-4 mr-2 text-muted-foreground" />
                                        {inboundDelivery.received_by}
                                    </p>
                                </div>
                                <div>
                                    <h4 className="text-sm font-medium text-muted-foreground mb-1">Created</h4>
                                    <p>{new Date(new Date(inboundDelivery.created_at).getTime() + (7 * 60 * 60 * 1000)).toLocaleString()}</p>
                                </div>

                                {
                                    inboundDelivery.notes && (
                                        <div>
                                            <h4 className="text-sm font-medium text-mutted-foreground mb-1">Notes</h4>
                                            <p className="text-sm bg-muted p-2 rounded">{inboundDelivery.notes}</p> 
                                        </div>
                                    )
                                }
                            </div>

                            <Separator className="my-6" />

                            <div>
                                <div>
                                    <h4 className="font-medium mb-2">Delivered Items</h4>
                                    <div className="rounded-md border">
                                        <Table>
                                            <TableHeader>
                                                <TableRow>
                                                    <TableHead>Product</TableHead>
                                                    <TableHead className="text-center">Expected</TableHead>
                                                    <TableHead className="text-center">Received</TableHead>
                                                    <TableHead className="text-center">Damaged</TableHead>
                                                    <TableHead className="text-right">Unit Price</TableHead>
                                                    <TableHead className="text-right">Total</TableHead>
                                                </TableRow>
                                            </TableHeader>
                                            <TableBody>
                                                {inboundDelivery.inbound_delivery_lines.map((inbound_line) => (
                                                    <TableRow key={inbound_line.id}>
                                                        <TableCell className="font-medium">{inbound_line.component_name}</TableCell>
                                                        <TableCell className="text-center">{inbound_line.expected_quantity}</TableCell>
                                                        <TableCell className="text-center">{inbound_line.received_quantity}</TableCell>
                                                        <TableCell className="text-center">{inbound_line.damaged_quantity}</TableCell>
                                                        <TableCell className="text-right">${Number(inbound_line.price_per_unit).toFixed(2)}</TableCell>
                                                        <TableCell className="text-right">${Number(inbound_line.total_line_amount).toFixed(2)}</TableCell>
                                                    </TableRow>
                                                ))}
                                            </TableBody>
                                        </Table>
                                    </div>
                                </div>

                                <div className="flex justify-between font-medium text-lg mt-4 mb-6">
                                    <span>Total Amount:</span>
                                    <span>
                                        ${inboundDelivery.inbound_delivery_lines.reduce((total, product) => {
                                            return total + Number(product.price_per_unit) * (product.received_quantity || 0 )
                                        }, 0)}
                                    </span>
                                </div>
                            </div>
                        </TabsContent>

                        <TabsContent value="attachments">
                            {imageAttachments.length === 0 ? (
                                <div className="text-center py-8 text-muted-foreground border border-dashed rounded-md">
                                    No attachments available
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {imageAttachments.length > 0 && (
                                        <div>
                                            <h4 className="font-medium mb-2">Images</h4>
                                            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                                                {imageAttachments.map((attachment, index) => (
                                                    <div
                                                        key={attachment.id}
                                                        className="relative aspect-square border rounded-md overflow-hidden cursor-pointer hover:opacity-90 transition-opacity"
                                                        onClick={() => openGallery(index)}
                                                    >
                                                        <Image 
                                                            src={attachment.file_link || "/placeholder.svg"}
                                                            alt={attachment.file_link}
                                                            fill
                                                            className="object-cover"
                                                        />
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    <div>
                                        <h4 className="font-medium mb-2">All Attachments</h4>
                                        <div className="space-y-2">
                                            {imageAttachments.map((attachment, index) => (
                                                <Card key={attachment.id}>
                                                    <CardContent className="p-4 flex justify-between items-center">
                                                        <div className="flex items-center gap-2">
                                                            <Package className="h-5 w-5 text-muted-foreground" />
                                                            <div>
                                                                <p className="font-medium">Image {index + 1}</p>
                                                                <p className="text-sx text-muted-foreground">
                                                                    Uploaded by {attachment.uploaded_by} on {" "}
                                                                    {new Date(new Date(attachment.created_at).getTime() + (7 * 60 * 60 * 1000)).toLocaleString()}
                                                                </p>
                                                            </div>
                                                        </div>
                                                        <Button variant="outline" size="sm">
                                                            Download
                                                        </Button>
                                                    </CardContent>
                                                </Card>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </TabsContent>
                    </Tabs>

                    <DialogFooter>
                        <Button type="button" onClick={onClose}>
                            Close
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {isGalleryOpen && imageAttachments.length > 0 && (
                <Dialog open={isGalleryOpen} onOpenChange={setIsGalleryOpen}>
                    <DialogContent className="sm:max-w-[90vw] max-h-[90vh] p-0 overflow-hidden">
                        <div className="relative h-[80vh] bg-black flex items-center justify-center">
                            <Button
                                variant="ghost"
                                size="icon"
                                className="absolute top-2 right-2 text-white bg-black/50 hover:bg-black/70 z-10"
                                onClick={() => setIsGalleryOpen(false)}
                            >
                                <X className="h-4 w-4" />
                            </Button>

                            <Button
                                variant="ghost"
                                size="icon"
                                className="absolute left-2 top-1/2 -translate-y-1/2 text-white bg-black/50 hover:bg-black/70 z-10"
                                onClick={prevImage}
                            >
                                <ChevronLeft className="h-6 w-6" />
                            </Button>

                            <div className="relative w-full h-full">
                                <Image 
                                    src={imageAttachments[currentImageIndex].file_link || "/placeholder.svg"}
                                    alt={imageAttachments[currentImageIndex].file_link}
                                    fill
                                    className="object-contain"
                                />
                            </div>

                            <Button
                                variant="ghost"
                                size="icon"
                                className="absolutte right-2 top-1/2 -translate-y-1/2 text-whitte bg-black/50 hover:bg-black/70 z-10"
                                onClick={nextImage}
                            >
                                <ChevronRight 
                                    className="h-6 w-6"
                                />
                            </Button>

                            <div className="absolute bottom-4 left-0 rightt-0 text-center text-white bg-black/50 py-2">
                                {imageAttachments[currentImageIndex].file_link} ({currentImageIndex + 1}/{imageAttachments.length})
                            </div>
                        </div>
                    </DialogContent>
                </Dialog>
            )}
        </>
    )
}