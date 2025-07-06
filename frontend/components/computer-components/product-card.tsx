import Image from "next/image"
import type { ProductInFrontend } from "@/types/product"

interface ProductCardProps {
    product: ProductInFrontend
    onClick: (product: ProductInFrontend) => void
}

export function ProductCard({ product, onClick }:
    ProductCardProps
) {
    return (
        <div
            key={product.id}
            onClick={() => onClick(product)}
            className="group border rounded-lg overflow-hidden hover:shadow-md transition-shadow"
        >
            <div className="aspect-square relative">
                    <Image src={product.image || "/placeholder.svg"} alt={product.name} fill className="object-cover" />
            </div>
            <div className="p-4">
                <h3 className="font-medium text-lg">{product.name}</h3>
                <p className="text-muted-foreground text-sm mb-2">{product.component_category_name}</p>
                <p className="font-bold">${Number(product.price).toFixed(2)}</p>
            </div>
        </div>
    )
}