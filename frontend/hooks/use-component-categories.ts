"use client"

import { useState, useEffect, useCallback } from "react"
import type { ComputerComponentCategory } from "@/types/computer-component-category"
import { useToastError } from "@/hooks/use-toast-error"
import { handleApiError } from "@/utils/api/error-handlers"

export function useComponentCategories() {
    const [componentCategories, setComponentCategories] = useState<ComputerComponentCategory[]>([])
    const { showErrorToast } = useToastError()

    useEffect(() => {
        const loadComponentCategories = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/computer-component-categories')

                if (!response.ok) {
                    await handleApiError(response, showErrorToast);
                    return;
                }

                const responseData = await response.json();
                // const data: ComputerComponentCategory[] = [
                //     { id: '', name: 'All' },
                //     ...responseData.computer_component_categories
                //   ];  
                const data: ComputerComponentCategory[] = responseData.computer_component_categories;      
                setComponentCategories(data);
            } catch (error) {
                showErrorToast("Unable to load component categories")
            };
        };

        loadComponentCategories()
    }, []);

    return {
        componentCategories
    }
}