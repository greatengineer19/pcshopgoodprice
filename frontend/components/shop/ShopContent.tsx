"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import { fetchProducts, fetchProductCategories, fetchProductBrands } from "@/lib/product-service"
import { ShopContentProductCard } from "@/components/shop/ShopContentProductCard"
import { ProductFilters } from "@/components/shop/ProductFilters"
import { Loader2 } from "lucide-react"
import { ShopContentListWrapper, ShopContentDictionary, ProductBrand } from "@/types/product"
import type { ProductCategory } from "@/types/computer-component-category"

export default function ShopContent() {
    const [totalItem, setTotalItem] = useState(0)
    const [groupedProducts, setGroupedProducts] = useState<ShopContentDictionary>({})

    const [allCategories, setAllCategories] = useState<ProductCategory[]>([])
    const [selectedCategories, setSelectedCategories] = useState<ProductCategory[]>([])

    const [brands, setBrands] = useState<ProductBrand[]>([])
    const [selectedBrands, setSelectedBrands] = useState<string[]>([])

    const defaultMinPrice = 0
    const defaultMaxPrice = 100000000
    const [selectedPriceRange, setSelectedPriceRange] = useState<[number, number]>([0, 150000000])

    const [isLoading, setIsLoading] = useState(true)
    const [minRating, setMinRating] = useState(0)
    const item_per_page = 25

    function transformResponseProducts(products: ShopContentListWrapper) {
        setTotalItem(products.total_item)
        setGroupedProducts(products.sellable_products)
    }

    useEffect(() => {
        const loadInitialData = async () => {
            setIsLoading(true)

            try {
                const [categoriesData] = await Promise.all([
                    fetchProductCategories(),
                    // fetchProductBrands()
                ])

                setAllCategories(categoriesData)
                // setBrands(brandsData)

                const fetchedProducts = await fetchProducts()
                const productsData = fetchedProducts.result
                transformResponseProducts(productsData)
            } catch (error) {
                console.error("Failed to load initial data:", error)
            } finally {
                setIsLoading(false)
            }
        }

        loadInitialData()
    }, [])

    const applyFilters = async () => {
        setIsLoading(true)

        try {
            const filters = {
                categories: selectedCategories,
                priceRange: selectedPriceRange,
                ratings: minRating
            }

            const fetchedProducts = await fetchProducts(filters)
            const productsData = fetchedProducts.result
            transformResponseProducts(productsData)
        } catch (error) {
            console.error("Failed to apply filters:", error)
        } finally {
            setIsLoading(true)
        }
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-8">Hi shoppers, shop with us today.</h1>
            <div className="flex flex-col md:flex-row gap-8">
                <div className="w-full md:w-1/4 lg:w-1/5">
                    <ProductFilters 
                        allCategories={allCategories}
                        allBrands={brands}
                        defaultMinPrice={defaultMinPrice}
                        defaultMaxPrice={defaultMaxPrice}
                        selectedCategories={selectedCategories}
                        setSelectedCategories={setSelectedCategories}
                        selectedBrands={selectedBrands}
                        setSelectedBrands={setSelectedBrands}
                        selectedPriceRange={selectedPriceRange}
                        setSelectedPriceRange={setSelectedPriceRange}
                        minRating={minRating}
                        setMinRating={setMinRating}
                        applyFilters={applyFilters}
                    />
                </div>

                {/* Product Listings */}
                <div className="w-full md:w-3/4 lg:w-4/5">
                    {isLoading && totalItem === 0 ? (
                        <div className="flex justify-center items-center h-64">
                            <Loader2 className="h-8 w-8 animate-spin text-primary"></Loader2>
                        </div>
                    ) : totalItem === 0 ? (
                        <div className="text-center py-12 border rounded-md">
                            <p className="text-muted-foreground">No products found matching your filters.</p>
                        </div>
                    ) : (
                        Object.entries(groupedProducts).map(([_, categoryProducts]) => (
                            <div key={categoryProducts.name} className="mb-12">
                                <h2 className="text-2xl font-semibold mb-6">{categoryProducts.name}</h2>
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {
                                        categoryProducts.components.map((product, index) => {
                                            if (categoryProducts.components.length === index + 1) {
                                                return (
                                                    <div key={product.id}>
                                                        <ShopContentProductCard product={product} />
                                                    </div>
                                                )
                                            } else {
                                                return <ShopContentProductCard key={product.id} product={product} />
                                            }
                                        })
                                    }
                                </div>
                            </div>
                        ))
                    )}

                    {
                        isLoading && totalItem > 0 && (
                            <div className="flex justify-center items-center py-8">
                                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                            </div>
                        )
                    }
                </div>
            </div>
        </div>
    )
}