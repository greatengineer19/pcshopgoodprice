"use client"

import { useReportInventoryMovement } from "@/hooks/use-report-inventory-movement"
import { FilterReportInventoryMovement } from "./FilterReportInventoryMovement"
import { ReportTable } from "./ReportTable"

export default function ReportInventoryMovementContent() {
    const {
        reportData,
        isLoading,
        currentPage,
        filters,
        updateFilters,
        changePage,
        onFilterChangePromise,
        loadPageWithFilters
    } = useReportInventoryMovement()

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold">Report Inventory Movement</h1>
            </div>

            <FilterReportInventoryMovement 
                filters={filters}
                onFilterChange={updateFilters}
                onFilterChangePromise={onFilterChangePromise}
                onApplyFilters={loadPageWithFilters}
                isLoading={isLoading}
            />

            <ReportTable
                reportData={reportData}
                isLoading={isLoading}
                currentPage={currentPage}
                onPageChange={changePage}
            />
        </div>
    )
}