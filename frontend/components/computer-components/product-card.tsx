import Image from "next/image"
import type { ProductInFrontend } from "@/types/product"

interface ProductCardProps {
    product: ProductInFrontend
    onClick: (product: ProductInFrontend) => void
}

export function ProductCard({ product, onClick }:
    ProductCardProps
) {
    const defaultPrice = product.computer_component_sell_price_settings.find((p) => p.day_type === "default")
    const formattedPrice = new Intl.NumberFormat("id-ID", {
        style: "currency",
        currency: "IDR",
        minimumFractionDigits: 0,
    }).format(defaultPrice?.price_per_unit || 0);

    return (
        <div
            key={product.id}
            onClick={() => onClick(product)}
            className="group border rounded-lg overflow-hidden hover:shadow-md transition-shadow"
        >
            <div className="aspect-square relative">
                    <Image src={product.image || "/placeholder.svg"} alt={product.name} fill sizes="(max-width: 768px) 100vw,
                        (max-width: 1200px) 50vw,
                        33vw" className="object-cover" />
            </div>
            <div className="p-4">
                <h3 className="font-medium text-lg">{product.name}</h3>
                <p className="text-muted-foreground text-sm mb-2">{product.component_category_name}</p>
                <p className="font-bold">{formattedPrice}</p>
            </div>
        </div>
    )
}