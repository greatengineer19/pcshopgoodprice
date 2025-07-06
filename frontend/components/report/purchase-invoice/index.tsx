"use client"

import { useReportPurchaseInvoice } from "@/hooks/use-report-purchase-invoice"
import { ReportPurchaseInvoiceFilters } from "./report-filters"
import { ReportTable } from "./report-table"

export default function PurchaseInvoiceReport() {
    const {
        reportData,
        isLoading,
        currentPage,
        filters,
        updateFilters,
        changePage,
        loadReportData
    } = useReportPurchaseInvoice()

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold">Purchase Invoice Report</h1>
                <p className="text-muted-foreground mt-2">
                    View detailed report of purchase invoices and their delivery status
                </p>
            </div>

            <ReportPurchaseInvoiceFilters 
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