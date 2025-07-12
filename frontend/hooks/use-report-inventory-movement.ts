"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import type { ReportData, ReportInventoryMovementFilters } from "@/types/report"
import { useToastError } from "@/hooks/use-toast-error"
import { handleApiError } from "@/utils/api/error-handlers"

export function useReportInventoryMovement() {
    const [reportData, setReportData] = useState<ReportData>({
        report_headers: [],
        report_body: [],
        paging: {
          page: 1,
          total_item: 0,
          pagination: {
            prev_page_url: null,
            next_page_url: null
          }
        }
    });      
    const [isLoading, setIsLoading] = useState(false)
    const [currentPage, setCurrentPage] = useState(1)
    const [filters, setFilters] = useState<ReportInventoryMovementFilters>({
        keyword: "",
        transactionType: "",
        startDate: "",
        wordingStartDate: "",
        endDate: "",
        wordingEndDate: "",
        componentName: "",
        componentCategoryId: ""
    })
    const filtersRef = useRef(filters)
    const { showErrorToast } = useToastError()

    // Update ref when filters change
    useEffect(() => {
        filtersRef.current = filters
    }, [filters])

    const loadReportData = useCallback(async () => {
        if (isLoading) return; // Prevent concurrent requests
        setIsLoading(true)

        try {
            const query_params = {
                keyword: filtersRef.current.keyword,
                transaction_type: filtersRef.current.transactionType,
                start_date: filtersRef.current.startDate,
                end_date: filtersRef.current.endDate,
                component_name: filtersRef.current.componentName,
                component_category_id: filtersRef.current.componentCategoryId,
                page: String(currentPage)
            }

            const queryString = '?' + new URLSearchParams(query_params).toString();
            const response = await fetch("http://localhost:8080/api/report/inventory-movement" + queryString)

            if (!response.ok) {
                await handleApiError(response, showErrorToast);
                return;
            }

            const responseData = await response.json();
            const data: ReportData = responseData;

            setReportData(data);
        } catch (error) {
            if (error instanceof Error) {
                showErrorToast(error.message);
            } else {
                showErrorToast("Unable to load report data");
            }
            setReportData({
                report_headers: [],
                report_body: [],
                paging: {
                    page: 1,
                    total_item: 0,
                    pagination: {
                        prev_page_url: null,
                        next_page_url: null
                    }
                }
            });
        } finally {
            setIsLoading(false)
        }
    }, [currentPage, showErrorToast, isLoading]); // Removed filters from dependencies

    // Only load data on mount and when currentPage changes
    useEffect(() => {
        loadReportData();
    }, [currentPage]); // Only depend on currentPage

    const updateFilters = useCallback((newFilters: Partial<ReportInventoryMovementFilters>) => {
        setFilters((prev) => ({ ...prev, ...newFilters }))
    }, []);

    const loadPageWithFilters =() => {
        loadReportData();
    }

    const onFilterChangePromise = useCallback((newFilters: Partial<ReportInventoryMovementFilters>) => {
            return new Promise<ReportInventoryMovementFilters>(resolve => { // Explicitly type the resolved value
                setFilters((prev) => {
                    const updatedState = { ...prev, ...newFilters };
                    filtersRef.current = updatedState; // Synchronously update the ref
                    resolve(updatedState); // Resolve the promise with the new state
                    return updatedState; // Return the new state for React
                });
            });
        }, []);

    const changePage = (page: number) => {
        setCurrentPage(page)
    }

    return {
        reportData,
        isLoading,
        currentPage,
        filters,
        updateFilters,
        onFilterChangePromise,
        changePage,
        loadPageWithFilters
    }
}