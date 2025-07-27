"use client"

import { useState, useEffect } from "react"
import type { ProductInFrontend, ProductFromBackend } from "@/types/product"
import { useToastError } from "@/hooks/use-toast-error"
import { handleApiError } from "@/utils/api/error-handlers"

export function useProducts() {
    const { showErrorToast } = useToastError()

    const [products, setProducts] = useState<ProductInFrontend[]>([]);
    useEffect(() => {
		const fetchProducts = async () => {
			try {
				const response = await fetch('http://localhost:8000/api/computer-components');
				
				if (!response.ok) {
					await handleApiError(response, showErrorToast);
					return;
				}

				const responseData = await response.json();
				const data: ProductFromBackend[] = responseData.computer_components;
				const mutatedData: ProductInFrontend[] = data.map((p) => ({
					...p,
					image: p.images?.[0] ?? undefined,
					component_category_id: p.component_category_id,
					computer_component_sell_price_settings: p.computer_component_sell_price_settings
				  }));

				setProducts(mutatedData);
			} catch (error) {
				showErrorToast("Failed to connect to the server. Please check your connection.");
			}
		};

		fetchProducts();
	}, []);

    return { products }
}