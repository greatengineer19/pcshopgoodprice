"use client"

import { useState } from "react"
import Image from "next/image"
import Link from "next/link"
import { Star, ShoppingCart } from "lucide-react"
import type { ShopContentProduct } from "@/types/product"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface ProductCardProps {
    product: ShopContentProduct
}

export function ShopContentProductCard({ product }: ProductCardProps) {
    const [isHovered, setIsHovered] = useState(false)

    function toSnakeCase(str: string): string {
        return str
            .replace(/\s+/g, '_')
            .replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
            .replace(/__+/g, '_')
            .replace(/^_+|_+$/g, '')
            .toLowerCase();
    }

    const product_slug = toSnakeCase(product.name)

    return (
        <Link href={`/shop/product/${product_slug}`}>
            <div 
                className="group border rounded-lg overflow-hidden transition-all duration-300 hover:shadow-md"
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
            >
                {/* Discount badge */}
                {
                    <div className="absolute top-2 left-2 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-md z-10">
                        33% OFF
                    </div>
                }

                {/* Product image */}
                <div className="relative aspect-square bg-gray-100">
                    <Image 
                        src={product.images ? product.images[0] : "/placeholder.svg?height=300&width=300"}
                        alt={product.name}
                        fill
                        className="object-contain p-4 transition-transform duration-300 group-hover:scale-105"
                    />

                    {/* Quick add to cart button (appears on hover) */}
                    <div 
                        className={cn(
                            "absolute bottom-0 left-0 right-0 bg-black/70 text-white py-2 px-4 transition-all duration-300",
                            isHovered ? "translate-y-0 opacity-100" : "translate-y-full opacity-0",
                        )}
                    >
                        <Button 
                            variant="ghost"
                            className="w-full text-white hover:text-white hover:bg-black/50"
                            onClick={(e) => {
                                e.preventDefault()
                            }}
                        >
                            <ShoppingCart className="mr-2 h-4 w-4" />
                            Add to Cart
                        </Button>
                    </div>
                </div>

                {/* Product details */}
                <div className="p-4">
                    <h3 className="font-medium text-sm line-clamp-2 h-10 mb-2">
                        {product.name}
                    </h3>

                    {/* Ratings */}
                    <div className="flex items-center mb-2">
                        <div className="flex">
                            {[1, 2, 3, 4, 5].map((star) => (
                                <Star 
                                    key={star}
                                    className={cn(
                                        "h-3 w-3",
                                        star <= Math.round(product.rating) ? "text-yellow-400 fill-yellow-400" : "text-gray-300"
                                    )}
                                />
                            ))}
                        </div>
                        <span className="text-xs text-gray-500 ml-1">({product.count_review_given})</span>
                    </div>

                    {/* Price */}
                    <div className="flex items-center">
                        <span className="font-bold text-base">IDR {(product.sell_price).toFixed(2)}</span>
                        {
                            product.sell_price && (
                                <span className="text-gray-500 text-sm line-through ml-2">
                                    IDR {product.sell_price.toFixed(2)}
                                </span>
                            )
                        }
                    </div>
                </div>
            </div>
        </Link>
    )
}
