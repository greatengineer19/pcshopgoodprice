export interface ReportHeader {
    text: string
}

export interface ReportCell {
    text: string
}

export interface ReportPagination {
    prev_page_url: string | null
    next_page_url: string | null
}

export interface ReportPaging {
    page: number
    total_item: number
    pagination: ReportPagination
}

export interface ReportData {
    report_headers: ReportHeader[]
    report_body: ReportCell[][]
    paging: ReportPaging
}

export interface ReportPurchaseInvoiceFilters {
    keyword: string
    invoiceStatus: string
    startDate: string
    endDate: string
    componentName: string
    componentCategoryId: string
}

export interface ReportInventoryMovementFilters {
    keyword: string
    transactionType: string
    startDate: string
    endDate: string
    componentName: string
    componentCategoryId: string
}