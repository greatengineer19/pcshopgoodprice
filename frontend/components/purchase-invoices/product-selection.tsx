"use client"

import { useState } from "react"
import Image from "next/image"
import { Search, Plus } from "lucide-react"
import type { MappedProduct } from "@/types/purchase-invoice"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface ParamsProps {
    products: MappedProduct[]
    onAddProduct: (product: MappedProduct) => void
}

export function ProductSelection({ products, onAddProduct }: ParamsProps) {
    const [searchTerm, setSearchTerm] = useState("")

    const filteredProducts = products.filter(
        (product) =>
            product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            product.component_category_name.toLowerCase().includes(searchTerm.toLowerCase()),
    )

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">Select Products</h3>
                <div className="relative w-full max-w-[300px]">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input 
                        placeholder="Search products..."
                        className="pl-8"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            <div className="rounded-md border max-h-[300px] overflow-y-auto">
                <Table>
                    <TableHeader className="stticky top-0 bg-background z-10">
                        <TableRow>
                            <TableHead>Product</TableHead>
                            <TableHead>Category</TableHead>
                            <TableHead className="text-right">Price</TableHead>
                            <TableHead className="w-[100px] text-center">Action</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {filteredProducts.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={6} className="text-center py-4 text-muted-foreground">
                                    No products found
                                </TableCell>
                            </TableRow>
                        ) : (
                            filteredProducts.map((product) => (
                                <TableRow key={product.id}>
                                    <TableCell className="font-medium">
                                        {product.name}
                                    </TableCell>
                                    <TableCell>
                                        {product.component_category_name}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        Rp {product.buyPrice}
                                    </TableCell>
                                    <TableCell className="text-center">
                                        <Button 
                                            variant="outline"
                                            size="sm"
                                            onClick={() => onAddProduct(product)}
                                            className="h-8 w-8 p-0"
                                        >
                                            <Plus className="h-4 w-4" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>
        </div>
    )
}