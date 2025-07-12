export interface ReportHeader {
    text: string
}

export interface ReportCell {
    text: string
    cell_type?: string
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
    wordingInvoiceStatus: string
    startDate: string
    wordingStartDate: string
    endDate: string
    wordingEndDate: string
    componentName: string
    componentCategoryId: string
}

export interface ReportInventoryMovementFilters {
    keyword: string
    transactionType: string
    startDate: string
    wordingStartDate: string
    endDate: string
    wordingEndDate: string
    componentName: string
    componentCategoryId: string
}