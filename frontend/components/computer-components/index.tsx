"use client"

import { Toaster } from "sonner"
import { useState, useRef, useCallback } from "react"

import { ButtonAddProduct } from "@/components/computer-components/button-add-product"
import { ProductGrid } from "@/components/computer-components/product-grid"
import { ProductViewModal } from "@/components/computer-components/product-view-modal"
import { DeleteConfirmationModal } from "@/components/computer-components/delete-confirmation-modal"
import { NewProductModal } from "@/components/computer-components/new-product-modal"

import { SelectedProductProvider } from '@/context/SelectedProductContext'
import { OnEditProductProvider } from "@/context/OnEditProductContext"
import { useToastError } from "@/hooks/use-toast-error"
import { handleApiError } from "@/utils/api/error-handlers"
import { useProductForm } from "@/hooks/use-product-form"

import type { ProductInFrontend } from "@/types/product"
import type { UploadedImageResponse } from "@/types/image"
import type { SetStateAction } from "react"

export default function ComponentComputerComponentsIndex() {
	const [selectedProduct, setSelectedProduct] = useState<ProductInFrontend | null>(null);
	const [isDialogOpen, setIsDialogOpen] = useState(false);
	const [isLoading, setIsLoading] = useState(false);
	const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
	const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
	const [previewUrl, setPreviewUrl] = useState<string>("/placeholder.svg?height=300&width=300");
	const [isEditMode, setIsEditMode] = useState(false);
	const [uploadedImage, setUploadedImage] = useState<UploadedImageResponse | null>(null);
	const { setFormData } = useProductForm();
	const { showErrorToast } = useToastError();

	const handleFileSelect = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
		const file = event.target.files?.[0];
	
		if (!file) return;
	
		if (file.size > 5 * 1024 * 1024) { // 5MB limit
			showErrorToast("File size must be less than 5MB");
			return;
		}
	
		const reader = new FileReader();
	
		reader.onloadend = async () => {
			const result = reader.result as string;
	
			setPreviewUrl(result);
	
			if (!isEditMode) {
				setFormData(prev => ({
					...prev,
					image: result
				}));
			}
	
			// Upload the image after preview setup
			try {
				const formData = new FormData();
				formData.append('file', file);
	
				const response = await fetch('http://localhost:8080/api/upload_url', {
					method: 'POST',
					body: formData,
				});
	
				if (!response.ok) {
					await handleApiError(response, showErrorToast);
					return;
				}
	
				const uploadData = await response.json();
				setUploadedImage({
					s3_key: uploadData.s3_key,
					status_code: uploadData.status_code
				});
			} catch (error) {
				showErrorToast("Failed to upload image. Please try again.");
			}
		};
	
		reader.readAsDataURL(file);
	}, [isEditMode, setFormData, showErrorToast]);

	const handleOpenDialog = useCallback(() => {
		setIsDialogOpen(true);
	}, []);

	const handleCloseDialog = useCallback(() => {
		setIsDialogOpen(false);
	}, []);

	const handleOpenAddDialog = useCallback(() => {
		setIsAddDialogOpen(true);
	}, []);

	const handleCloseAddDialog = useCallback(() => {
		setIsAddDialogOpen(false);
	}, []);

	const handleOpenDeleteDialog = useCallback(() => {
		setIsDeleteDialogOpen(true);
	}, []);

	const handleCloseDeleteDialog = useCallback(() => {
		setIsDeleteDialogOpen(false);
	}, []);

	const handleSetLoading = useCallback((value: SetStateAction<boolean>) => {
		setIsLoading(value);
	}, []);

	const handleSetSelectedProduct = useCallback((product: ProductInFrontend | null) => {
		setSelectedProduct(product);
	}, []);

	return (
		<SelectedProductProvider>
			<OnEditProductProvider selectedProduct={selectedProduct}>
				<div className="container mx-auto px-4 py-8">
					<div className="flex justify-between items-center mb-8">
						<h1 className="text-3xl font-bold">Computer Components</h1>
						<ButtonAddProduct 
							setIsAddDialogOpen={handleOpenAddDialog}
						/>
					</div>

					<ProductGrid 
						setIsDialogOpen={handleOpenDialog}
						setIsEditMode={setIsEditMode}
						setSelectedProduct={handleSetSelectedProduct}
					/>

					<ProductViewModal 
						product={selectedProduct}
						setSelectedProduct={setSelectedProduct}
						setIsDeleteDialogOpen={handleOpenDeleteDialog}
						setFalseLoading={() => handleSetLoading(false)}
						setTrueLoading={() => handleSetLoading(true)}
						isEditMode={isEditMode}
						setIsEditMode={setIsEditMode}
						setIsAddDialogOpen={handleOpenAddDialog}
						isDialogOpen={isDialogOpen}
						setIsDialogOpen={handleCloseDialog}
						isLoading={isLoading}
						handleFileSelect={handleFileSelect}
						uploadedImage={uploadedImage}
					/>

					<NewProductModal 
						setIsLoading={handleSetLoading}
						isAddDialogOpen={isAddDialogOpen}
						setIsAddDialogOpen={handleCloseAddDialog}
						isLoading={isLoading}
						handleFileSelect={handleFileSelect}
						uploadedImage={uploadedImage}
						setPreviewUrl={setPreviewUrl}
						previewUrl={previewUrl}
					/>

					<DeleteConfirmationModal
						selectedProduct={selectedProduct}
						isDeleteDialogOpen={isDeleteDialogOpen}
						isLoading={isLoading}
						setIsLoading={handleSetLoading}
						setIsDialogOpen={handleCloseDialog}
						setCloseDeleteDialog={handleCloseDeleteDialog}
					/>

					<Toaster richColors />
				</div>
			</OnEditProductProvider>
		</SelectedProductProvider>
	)
}