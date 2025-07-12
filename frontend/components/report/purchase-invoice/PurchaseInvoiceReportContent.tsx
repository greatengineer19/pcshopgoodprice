"use client"

import { useReportPurchaseInvoice } from "@/hooks/use-report-purchase-invoice"
import { FiltersReportPurchaseInvoice } from "./FiltersReportPurchaseInvoice"
import { ReportTable } from "./ReportTable"

export default function PurchaseInvoiceReportContent() {
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
                    View purchase invoices details and its deliveries status
                </p>
            </div>

            <FiltersReportPurchaseInvoice 
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