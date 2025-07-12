"use client"

import { ChevronLeft, ChevronRight, Loader2 } from "lucide-react"
import type { ReportData } from "@/types/report"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"

interface ParamsProps {
    reportData: ReportData
    isLoading: boolean
    currentPage: number
    onPageChange: (page: number) => void
}

export function ReportTable({ reportData, isLoading, currentPage, onPageChange }: ParamsProps) {
    if (isLoading) {
        return (
            <div className="flex justify-center items-center h-64">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        )
    }

    if (!reportData) {
        return (
            <div className="text-center py-12 border rounded-md">
                <p className="text-muted-foreground">No report data available</p>
            </div>
        )
    }

    const { report_headers, report_body, paging } = reportData

    return (
        <div className="space-y-4">
            <div className="rounded-md border overflow-auto">
                <Table>
                    <TableHeader>
                        <TableRow>
                            {report_headers.map((header, index) => (
                                <TableHead key={index} className="whitespace-nowrap">
                                    {header.text}
                                </TableHead>
                            ))}
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {report_body.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={report_headers.length} className="text-center h-24">
                                    No data found
                                </TableCell>
                            </TableRow>
                        ) : (
                            report_body.map((row, rowIndex) => (
                                <TableRow key={rowIndex}>
                                    {
                                        row.map((cell, cellIndex) => (
                                            <TableCell key={cellIndex} className="whitespace-nowrap">
                                                {
                                                    cell.cell_type == "text" ?
                                                    cell.text :
                                                    (
                                                        cell.cell_type == "money" ?
                                                        Number(cell.text).toLocaleString('id-ID', {
                                                            style: 'currency',
                                                            currency: 'IDR',
                                                            minimumFractionDigits: 0, // Typically no decimals for IDR
                                                            maximumFractionDigits: 0, // Typically no decimals for IDR
                                                        }) :
                                                        (
                                                            cell.cell_type == "quantity" ?
                                                            Number(cell.text).toFixed(2) :
                                                            cell.text
                                                        )
                                                    )
                                                }
                                            </TableCell>
                                        ))
                                    }
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between">
                <div className="text-sm text-muted-foreground">
                    Showing page {paging.page} of {Math.ceil(paging.total_item / 10)}
                </div>
                <div className="flex items-center space-x-2">
                    <Button 
                        variant="outline"
                        size="sm"
                        onClick={() => onPageChange(currentPage - 1)}
                        disabled={!paging.pagination.prev_page_url}
                    >
                        <ChevronLeft className="h-4 w-4" />
                        <span className="sr-only">Previous Page</span>
                    </Button>
                    <div className="text-sm">
                        Page {paging.page} of {Math.ceil(paging.total_item / 10)}
                    </div>
                    <Button 
                        variant="outline"
                        size="sm"
                        onClick={() => onPageChange(currentPage + 1)}
                        disabled={!paging.pagination.next_page_url}
                    >
                        <ChevronRight className="h-4 w-4" />
                        <span className="sr-only">Next Page</span>
                    </Button>
                </div>
            </div>
        </div>
    )
}