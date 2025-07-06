"use client"

import { useState } from "react"
import { Slider } from "@/components/ui/slider"
import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Star } from "lucide-react"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import type { ProductBrand } from "@/types/product"
import type { ProductCategory } from "@/types/computer-component-category"
import { cn } from "@/lib/utils"

interface ProductFiltersProps {
    allCategories: ProductCategory[]
    allBrands: ProductBrand[]
    defaultMinPrice: number
    defaultMaxPrice: number
    selectedCategories: string[]
    setSelectedCategories: (categories: string[]) => void
    selectedBrands: string[]
    setSelectedBrands: (brands: string[]) => void
    selectedPriceRange: [number, number]
    setSelectedPriceRange: (range: [number, number]) => void
    minRating: number
    setMinRating: (rating: number) => void
    applyFilters: () => void
}

export function ProductFilters({
    allCategories,
    allBrands,
    defaultMinPrice,
    defaultMaxPrice,
    selectedCategories,
    setSelectedCategories,
    selectedBrands,
    setSelectedBrands,
    selectedPriceRange,
    setSelectedPriceRange,
    minRating,
    setMinRating,
    applyFilters,
}: ProductFiltersProps) {
    const [priceInputMin, setPriceInputMin] = useState(selectedPriceRange[0].toString())
    const [priceInputMax, setPriceInputMax] = useState(selectedPriceRange[1].toString())

    const handleCategoryChange = (category: string) => {
        setSelectedCategories(
            selectedCategories.includes(category)
                ? selectedCategories.filter((c) => c !== category)
                : [...selectedCategories, category],
        )
    }

    const handleBrandChange = (brand: string) => {
        setSelectedBrands(
            selectedBrands.includes(brand) ? selectedBrands.filter((b) => b !== brand) : [...selectedBrands, brand],
        )
    }

    const handlePriceRangeChange = (value: number[]) => {
        setSelectedPriceRange([value[0], value[1]])
        setPriceInputMin(value[0].toString())
        setPriceInputMax(value[1].toString())
    }

    const handlePriceInputChange = (min: string, max: string) => {
        const minValue = Number(min)
        const maxValue = Number(max)

        if (!isNaN(minValue) && !isNaN(maxValue) && minValue <= maxValue) {
            setSelectedPriceRange([minValue, maxValue])
        }
    }

    const handleRatingChange = (rating: number) => {
        setMinRating(rating === minRating ? 0 : rating)
    }

    const resetFilters = () => {
        setSelectedCategories([])
        setSelectedBrands([])
        setSelectedPriceRange([defaultMinPrice, defaultMaxPrice])
        setPriceInputMin(defaultMinPrice.toString())
        setPriceInputMax(defaultMaxPrice.toString())
        setMinRating(0)
        applyFilters()
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-lg font-semibold">Filters</h2>
                <Button variant="ghost" size="sm" onClick={resetFilters}>
                    Reset
                </Button>
            </div>
            <Accordion type="multiple" defaultValue={["categories", "price", "brands", "rating"]}>
                {/* Categories */}
                <AccordionItem value="categories">
                    <AccordionTrigger>Categories</AccordionTrigger>
                    <AccordionContent>
                        <div className="space-y-2">
                            {
                                allCategories.map((category) => (
                                    <div key={category.id} className="flex items-center space-x-2">
                                        <Checkbox 
                                            id={`category-${category.id}`}
                                            checked={selectedCategories.includes(category.name)}
                                            onCheckedChange={() => handleCategoryChange(category.name)}
                                        />
                                        <label
                                            htmlFor={`category-${category.id}`} className="text-sm cursor-pointer flex-1"
                                        >
                                            {category.name}
                                            <span className="text-xs text-gray-500 ml-1 italic">
                                                Available
                                            </span>
                                        </label>
                                    </div>
                                ))
                            }
                        </div>
                    </AccordionContent>
                </AccordionItem>

                {/* Price Range */}
                <AccordionItem value="price">
                    <AccordionTrigger>Price Range</AccordionTrigger>
                    <AccordionContent>
                        <div className="space-y-4">
                            <Slider 
                                defaultValue={[defaultMinPrice, defaultMaxPrice]}
                                value={[selectedPriceRange[0], selectedPriceRange[1]]}
                                min={defaultMinPrice}
                                max={defaultMaxPrice}
                                step={1}
                                onValueChange={handlePriceRangeChange}
                                className="my-6"
                            />
                        </div>

                        <div className="flex items-center space-x-2">
                            <Input 
                                type="number"
                                value={priceInputMin}
                                onChange={(e) => {
                                    setPriceInputMin(e.target.value)
                                    handlePriceInputChange(e.target.value, priceInputMax)
                                }}
                                className="h-8"
                                min={defaultMinPrice}
                                max={defaultMaxPrice}
                            />
                            <span>to</span>
                            <Input 
                                type="number"
                                value={priceInputMax}
                                onChange={(e) => {
                                    setPriceInputMax(e.target.value)
                                    handlePriceInputChange(priceInputMin, e.target.value)
                                }}
                                className="h-8"
                                min={defaultMinPrice}
                                max={defaultMaxPrice}
                            />
                        </div>
                    </AccordionContent>
                </AccordionItem>

                {/* Brands */}
                <AccordionItem value="brands">
                    <AccordionTrigger>Brands</AccordionTrigger>
                    <AccordionContent>
                        <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
                            {
                                allBrands.map((brand) => (
                                    <div key={brand.id} className="flex items-center space-x-2">
                                        <Checkbox 
                                            id={`brand-${brand.name}`}
                                            checked={selectedBrands.includes(brand.name)}
                                            onCheckedChange={() => handleBrandChange(brand.name)}
                                        />
                                        <label htmlFor={`brand-${brand.name}`} className="text-sm cursor-pointer">
                                            {brand.name}
                                        </label>
                                    </div>
                                ))
                            }
                        </div>
                    </AccordionContent>
                </AccordionItem>

                {/* Ratings */}
                <AccordionItem value="rating">
                    <AccordionTrigger>Ratings</AccordionTrigger>
                    <AccordionContent>
                        <div className="space-y-2">
                            {[5, 4, 3, 2, 1].map((rating) => (
                                <div
                                    key={rating}
                                    className="flex items-center space-x-2 cursor-pointer"
                                    onClick={() => handleRatingChange(rating)}
                                >
                                    <div className={cn(
                                        "w-4 h-4 rounded-sm border flex items-center justify-center",
                                        minRating === rating ? "bg-primary border-primary" :
                                        "border-input",
                                    )}>
                                        {minRating === rating && <div className="h-2 w-2 bg-white rounded-sm" />}
                                    </div>
                                    <div className="flex items-center">
                                        {
                                            Array.from({ length: 5 }).map((_, i) => (
                                                <Star 
                                                    key={i}
                                                    className={cn("h-3 w-3", i < rating ? "text-yellow-400 fill-yellow-400" : "text-gray-300")}
                                                />
                                            ))
                                        }
                                        <span className="text-xs ml-1">& Up</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </AccordionContent>
                </AccordionItem>
            </Accordion>

            <Button onClick={applyFilters} className="w-full">
                Apply Filters
            </Button>
        </div>
    )
}
