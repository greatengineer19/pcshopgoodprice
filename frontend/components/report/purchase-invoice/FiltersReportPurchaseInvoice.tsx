"use client"

import type React from "react"

import { useState } from "react"
import { Search, Filter, Calendar } from "lucide-react"
import type { ReportPurchaseInvoiceFilters } from "@/types/report"
import { useComponentCategories } from "@/hooks/use-component-categories"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Card, CardContent } from "@/components/ui/card"

interface ParamsProps {
    filters: ReportPurchaseInvoiceFilters
    onFilterChange: (filters: Partial<ReportPurchaseInvoiceFilters>) => void
    onApplyFilters: () => void
    isLoading: boolean
}

export function FiltersReportPurchaseInvoice({ filters, onFilterChange, onApplyFilters, isLoading}: ParamsProps) {
    const [isFilterOpen, setIsFilterOpen] = useState(false)
    const invoiceStatuses = ["Pending", "Processing", "Completed", "Cancelled"]
    const { componentCategories } = useComponentCategories()

    const handleSearch = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            onApplyFilters()
        }
    }

    return (
        <Card className="mb-6">
            <CardContent className="pt-6">
                <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
                    {/* Keyword Search */}
                    <div className="relative flex-1">
                        <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input 
                            placeholder="Search by invoice number..."
                            className="pl-8"
                            value={filters.keyword}
                            onChange={(e) => onFilterChange({ keyword: e.target.value })}
                            onKeyDown={handleSearch}
                        />
                    </div>

                    {/* Advanced Filters Button */}
                    <Popover open={isFilterOpen} onOpenChange={setIsFilterOpen}>
                        <PopoverTrigger asChild>
                            <Button variant="outline" className="flex items-center gap-2">
                                <Filter className="h-4 w-4" />
                                <span>Filters</span>
                            </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-80 md:w-96">
                            <div className="grid gap-4">
                                <h4 className="font-medium">Filter Options</h4>

                                {/* Invoice Status */}
                                <div className="grid w-full gap-2">
                                    <Label htmlFor="status">Invoice Status</Label>
                                    <Select
                                        value={filters.invoiceStatus}
                                        onValueChange={(value) => onFilterChange({ invoiceStatus: value})}
                                    >
                                        <SelectTrigger id="status" className="w-full">
                                            <SelectValue placeholder="Select status" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {
                                                invoiceStatuses.map((status, index) => {
                                                    // const value = index === 0 ? '' : String(index - 1);
                                                    return (
                                                        <SelectItem key={status} value={String(index)}>
                                                        {status}
                                                        </SelectItem>
                                                    );
                                                })
                                            }
                                        </SelectContent>
                                    </Select>
                                </div>

                                {/* Date Range */}
                                <div className="grid grid-cols-2 gap-2">
                                    <div className="grid gap-2">
                                        <Label htmlFor="start-date">Start Date</Label>
                                        <div className="relative">
                                        <Calendar className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                                        <Input
                                            id="start-date"
                                            type="date"
                                            className="pl-8"
                                            value={filters.startDate}
                                            onChange={(e) => onFilterChange({ startDate: e.target.value })}
                                        />
                                        </div>
                                    </div>
                                    <div className="grid gap-2">
                                        <Label htmlFor="end-date">End Date</Label>
                                        <div className="relative">
                                            <Calendar className='absolute left-2 top-2.5 h-4 w-4 text-muted-foreground' />
                                            <Input 
                                                id="end-date"
                                                type='date'
                                                className="pl-8"
                                                value={filters.endDate}
                                                onChange={(e) => onFilterChange({ endDate: e.target.value })}
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Component Name */}
                                <div className="grid gap-2">
                                    <Label htmlFor="component-name">Component Name</Label>
                                    <Input 
                                        id="component-name"
                                        placeholder="Enter component name"
                                        value={filters.componentName}
                                        onChange={(e) => onFilterChange({ componentName: e.target.value })}
                                    />
                                </div>

                                {/* Component Category */}
                                <div className="grid gap-2">
                                    <Label htmlFor="component-category">Component Category</Label>
                                    <Select 
                                        value={filters.componentCategoryId}
                                        onValueChange={(value) => onFilterChange({ componentCategoryId: value })}
                                    >
                                        <SelectTrigger id="component-category" className="w-full">
                                            <SelectValue placeholder="Select category" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {componentCategories.map((category) => (
                                                <SelectItem key={category.name} value={String(category.id)}>
                                                    {category.name}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>

                                {/* Apply Filters Button */}
                                <Button 
                                    onClick={() => {
                                        onApplyFilters()
                                        setIsFilterOpen(false)
                                    }}
                                    disabled={isLoading}
                                >
                                    Apply Filters
                                </Button>
                            </div>
                        </PopoverContent>
                    </Popover>

                    {/* Apply Button (for mobile) */}
                    <Button onClick={onApplyFilters} disabled={isLoading} className="md:hidden w-full">
                        Apply
                    </Button>
                </div>

                {/* Active Filters Display */}
                <div className="flex flex-wrap gap-2 mt-4">
                    {filters.keyword && (
                        <div className="bg-secondary text-secondary-fogreground px-3 py-1 rounded-full text-xs flex items-center">
                            Search: {filters.keyword}
                            <button className='ml-2 hover:text-primary' onClick={() => onFilterChange({ keyword: "" })}>
                                x
                            </button>
                        </div>
                    )}
                    {filters.invoiceStatus !== "All" && (
                        <div className="bg-secondary text-secondary-foreground px-3 py-1 rounded-full text-xs flex items-center">
                            Status: {filters.invoiceStatus}
                            <button className="ml-2 hover:text-primary" onClick={() => onFilterChange({ invoiceStatus: 'All '})}>
                                x
                            </button>
                        </div>
                    )}
                    {filters.startDate && (
                        <div className='bg-secondary text-secondary-foreground px-3 py-1 rounded-full text-xs flex items-center'>
                            From: {filters.startDate}
                            <button className="ml-2 hover:text-primary" onClick={() => onFilterChange({ startDate: "" })}>
                                x
                            </button>
                        </div>
                    )}
                    {filters.endDate && (
                        <div className="bg-secondary text-secondary-foreground px-3 py-1 rounded-full text-xs flex items-center">
                            To: {filters.endDate}
                            <button className="ml-2 hover:text-primary" onClick={() => onFilterChange({ endDate: "" })}>
                                x
                            </button>
                        </div>
                    )}
                    {filters.componentName && (
                        <div className="bg-secondary text-secondary-foreground px-3 py-1 rounded-full text-xs flex items-center">
                            Component: {filters.componentName}
                            <button className="ml-2 hover:text-primary" onClick={() => onFilterChange({ componentName: "" })}>
                                x
                            </button>
                        </div>
                    )}
                    {filters.componentCategoryId !== '' && (() => {
                        const selectedCategory = componentCategories.find(
                            (category) => category.id === Number(filters.componentCategoryId)
                        );

                        return (
                            <div className="bg-secondary text-secondary-foreground px-3 py-1 rounded-full text-xs flex items-center">
                            Category: {selectedCategory?.name}
                            <button className="ml-2 hover:text-primary" onClick={() => onFilterChange({ componentCategoryId: ""})}>
                                x
                            </button>
                        </div>
                        )
                    })()}
                </div>
            </CardContent>
        </Card>
    )
}