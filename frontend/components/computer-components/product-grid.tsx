"use client"

import { ProductCard } from "@/components/computer-components/product-card"
import { useProducts } from "@/hooks/use-products"
import { useOnEditProduct } from "@/context/OnEditProductContext"

import type { ProductInFrontend } from "@/types/product"

interface ProductGridProps {
	setIsDialogOpen: (value: boolean) => void,
	setIsEditMode: (value: boolean) => void,
	setSelectedProduct: (product: ProductInFrontend | null) => void
}

export function ProductGrid({ setIsDialogOpen, setIsEditMode, setSelectedProduct }: ProductGridProps) {
    const { products } = useProducts()
	const { setOnEditProduct } = useOnEditProduct()

    const handleProductClick = (product: any) => {
		setOnEditProduct({
			id: product.id,
			name: product.name || "",
			component_category_id: product.component_category_id,
			product_code: product.product_code,
			status: product.status,
			component_category_name: product.component_category_name || "",
			price: product.price || 0,
			description: product.description || "",
			stock: product.stock || 0,
			image: product.image || "/placeholder.svg?height=300&width=300"
		})
		setSelectedProduct(product)
		setIsDialogOpen(true)
		setIsEditMode(false)
	}

    return (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6 w-fit">
			{products.map((product) => 
				<ProductCard key={product.id} product={product} onClick={handleProductClick} />
			)}
        </div>
    )
}