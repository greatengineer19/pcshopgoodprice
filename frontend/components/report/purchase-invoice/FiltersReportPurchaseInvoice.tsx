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
    onFilterChangePromise: (filters: Partial<ReportPurchaseInvoiceFilters>) => void
    onApplyFilters: () => void
    isLoading: boolean
}

interface InvoiceStatusMap {
    [key: number]: string; // This is the index signature
    0: "Pending";
    1: "Processing";
    2: "Completed";
    3: "Cancelled";
}

export function FiltersReportPurchaseInvoice({ filters, onFilterChange, onFilterChangePromise, onApplyFilters, isLoading}: ParamsProps) {
    const [isFilterApplied, setIsFilterApplied] = useState(false)
    const onResetFilters = async () => {
        await onFilterChangePromise(
            {
                keyword: "",
                invoiceStatus: "",
                wordingInvoiceStatus: "",
                startDate: "",
                wordingStartDate: "",
                endDate: "",
                wordingEndDate: "",
                componentName: "",
                componentCategoryId: ""
            }
        )
        setIsFilterApplied(false)
        onApplyFilters()
    }
    const [isFilterOpen, setIsFilterOpen] = useState(false)
    const invoiceStatuses = ["Pending", "Processing", "Completed", "Cancelled"]
    const invoiceStatusMap: InvoiceStatusMap = {
        0: "Pending",
        1: "Processing",
        2: "Completed",
        3: "Cancelled"
    };
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
                                        onValueChange={(value: string) => onFilterChange({ invoiceStatus: value, wordingInvoiceStatus: invoiceStatusMap[Number(value)]})}
                                    >
                                        <SelectTrigger id="status" className="w-full">
                                            <SelectValue placeholder="Select status" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {
                                                invoiceStatuses.map((status, index) => {
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
                                            onChange={(e) => onFilterChange({ startDate: e.target.value,
                                                wordingStartDate: new Date(e.target.value).toLocaleDateString("en-GB", {
                                                day: "2-digit",
                                                month: "long",
                                                year: "numeric",
                                            }) })}
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
                                                onChange={(e) => onFilterChange({ endDate: e.target.value,
                                                    wordingEndDate: new Date(e.target.value).toLocaleDateString("en-GB", {
                                                    day: "2-digit",
                                                    month: "long",
                                                    year: "numeric",
                                                }) })}
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
                                        setIsFilterApplied(true)
                                    }}
                                    disabled={isLoading}
                                >
                                    Apply Filters
                                </Button>
                            </div>
                        </PopoverContent>
                    </Popover>

                    {/* Apply Button (for mobile) */}
                    <Button onClick={() => {
                                        onApplyFilters()
                                        setIsFilterOpen(false)
                                        setIsFilterApplied(true)
                                    }} disabled={isLoading} className="md:hidden w-full">
                        Apply
                    </Button>
                </div>

                {/* Active Filters Display */}
                <div className="flex flex-wrap gap-2 mt-4">
                    {
                        <button className="bg-secondary text-secondary-fogreground px-3 py-1 rounded-full text-xs flex items-center"
                                onClick={() => onResetFilters()}>
                            Reset Filter
                        </button>
                    }
                    {isFilterApplied && filters.keyword && (
                        <div className="bg-secondary text-secondary-fogreground px-3 py-1 rounded-full text-xs flex items-center">
                            Search: {filters.keyword}
                        </div>
                    )}
                    {isFilterApplied && filters.invoiceStatus !== "" && (
                        <div className="bg-secondary text-secondary-foreground px-3 py-1 rounded-full text-xs flex items-center">
                            Status: {filters.wordingInvoiceStatus}
                        </div>
                    )}
                    {isFilterApplied && filters.startDate && (
                        <div className='bg-secondary text-secondary-foreground px-3 py-1 rounded-full text-xs flex items-center'>
                            From: {filters.wordingStartDate}
                        </div>
                    )}
                    {isFilterApplied && filters.endDate && (
                        <div className="bg-secondary text-secondary-foreground px-3 py-1 rounded-full text-xs flex items-center">
                            To: {filters.wordingEndDate}
                        </div>
                    )}
                    {isFilterApplied && filters.componentName && (
                        <div className="bg-secondary text-secondary-foreground px-3 py-1 rounded-full text-xs flex items-center">
                            Component: {filters.componentName}
                        </div>
                    )}
                    {isFilterApplied && filters.componentCategoryId !== '' && (() => {
                        const selectedCategory = componentCategories.find(
                            (category) => category.id === Number(filters.componentCategoryId)
                        );

                        return (
                            <div className="bg-secondary text-secondary-foreground px-3 py-1 rounded-full text-xs flex items-center">
                            Category: {selectedCategory?.name}
                        </div>
                        )
                    })()}
                </div>
            </CardContent>
        </Card>
    )
}