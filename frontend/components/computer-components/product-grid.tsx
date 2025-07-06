"use client"

import { ProductCard } from "@/components/computer-components/product-card"
import { useProducts } from "@/hooks/use-products"
import { useOnEditProduct } from "@/context/OnEditProductContext"

import type { ProductInFrontend, ProductResponseWithPriceSettings, ProductParams } from "@/types/product"

interface ProductGridProps {
	setIsDialogOpen: (value: boolean) => void,
	setIsEditMode: (value: boolean) => void,
	setSelectedProduct: (product: ProductInFrontend | null) => void
}

export function ProductGrid({ setIsDialogOpen, setIsEditMode, setSelectedProduct }: ProductGridProps) {
    const { products } = useProducts()
	const { setOnEditProduct } = useOnEditProduct()

    const handleProductClick = async (product: ProductInFrontend) => {
		const response = await fetch("http://localhost:8080/api/computer-components/" + product.id);
		const productResponse: ProductInFrontend = await response.json();

		setOnEditProduct({
			id: productResponse.id,
			name: productResponse.name || "",
			component_category_id: productResponse.component_category_id,
			product_code: productResponse.product_code,
			status: productResponse.status,
			component_category_name: productResponse.component_category_name || "",
			description: productResponse.description || "",
			image: product.image || "/placeholder.svg?height=300&width=300",
			computer_component_sell_price_settings_attributes: productResponse.computer_component_sell_price_settings
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