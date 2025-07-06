"use client"

import { useReportInventoryMovement } from "@/hooks/use-report-inventory-movement"
import { ReportInventoryMovementFilters } from "./report-filters"
import { ReportTable } from "./report-table"

export default function InventoryMovementReport() {
    const {
        reportData,
        isLoading,
        currentPage,
        filters,
        updateFilters,
        changePage,
        loadReportData
    } = useReportInventoryMovement()

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold">Inventory Movement Report</h1>
                <p className="text-muted-foreground mt-2">
                    View detailed report of inventory movement and their delivery status
                </p>
            </div>

            <ReportInventoryMovementFilters 
                filters={filters}
                onFilterChange={updateFilters}
                onApplyFilters={loadReportData}
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