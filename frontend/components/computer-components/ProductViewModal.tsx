"use client"

import { useState, useRef } from "react"
import Image from "next/image"
import { X, Edit, Save, Upload, Trash2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogClose } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

import type React from "react"
import type { ProductInFrontend, DailyProductPrice } from "@/types/product"

import { useProductForm } from "@/hooks/use-product-form"
import { handleApiError } from "@/utils/api/error-handlers"
import { categories } from "@/utils/computer-component/categories"
import { useToastSuccess } from "@/hooks/use-toast-success"
import { useToastError } from "@/hooks/use-toast-error"

import { useOnEditProduct } from "@/context/OnEditProductContext"
import { UploadedImageResponse } from "@/types/image"
import type { ProductParams } from "@/types/product"
import { fetchProductCategories } from "@/lib/product-service" 
import { Switch } from "@/components/ui/switch"

interface ProductViewModalProps {
    product: ProductInFrontend | null,
    setSelectedProduct: (product: ProductInFrontend | null) => void,
    setIsDeleteDialogOpen: () => void,
    setFalseLoading: () => void,
    setTrueLoading: () => void,
    isEditMode: boolean,
    setIsEditMode: React.Dispatch<React.SetStateAction<boolean>>,
    setIsAddDialogOpen: React.Dispatch<React.SetStateAction<boolean>>,
    isDialogOpen: boolean,
    setIsDialogOpen: React.Dispatch<React.SetStateAction<boolean>>,
    isLoading: boolean,
    handleFileSelect: (event: React.ChangeEvent<HTMLInputElement>) => void,
    uploadedImage: UploadedImageResponse | null,
}

export function ProductViewModal(
    {
        product,
        setSelectedProduct,
        setIsDeleteDialogOpen,
        setFalseLoading,
        setTrueLoading,
        isEditMode,
        setIsEditMode,
        setIsAddDialogOpen,
        isDialogOpen,
        setIsDialogOpen,
        isLoading,
        handleFileSelect,
        uploadedImage
    }: ProductViewModalProps) {
    if (!product) return null
    
    const { showSuccessToast } = useToastSuccess()
    const { showErrorToast } = useToastError()

    const [sellPricesAttributes, setSellPricesAttributes] = useState<DailyProductPrice[]>([]);
    const { onEditProduct, handleEditProductChange, handleEditProductChangeInt, defaultPrice, setDefaultPrice } = useOnEditProduct()
    const { resetForm } = useProductForm(product || undefined)
    const fileInputRef = useRef<HTMLInputElement>(null);
    const handleUploadClick = () => {
        fileInputRef.current?.click();
    };

    const [dayPricing, setDayPricing] = useState<DailyProductPrice[]>(
        onEditProduct.computer_component_sell_price_settings_attributes.filter(
            attr => attr.day_type.toLowerCase() !== "default"
        )
    );

    const handlePriceChange = (index: number, price: string) => {
        const updated = [...dayPricing]
        updated[index].price_per_unit = parseInt(price)
        setDayPricing(updated)
    }

    const handleActiveToggle = (index: number, active: boolean) => {
        const updated = [...dayPricing]
        updated[index].active = active
        setDayPricing(updated)
    }

    const handleDeleteClick = () => {
		setIsDeleteDialogOpen()
	};

    const toggleEditMode = () => {
        if (isEditMode) {
            resetForm()
        }
        setIsEditMode(!isEditMode)
    }

    const handleUpdateProduct = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
   
        if (!onEditProduct.name || !onEditProduct.component_category_name) {
            showErrorToast("Please fill in all required fields");
            return;
        } else if (!onEditProduct.id) {
            showErrorToast("No id found! Please contact dev of hassle free comps");
            return;
        }
    
        setTrueLoading();
    
        try {
            const imageUrl = uploadedImage?.s3_key;

            const productCategories = await fetchProductCategories();
            const category = productCategories.find(category => category.name === onEditProduct.component_category_name);

            if (!category) {
                throw new Error('Failed to fetch category');
            }

            let tempSellPrices: DailyProductPrice[] = [];

            const defaultPriceSetting = onEditProduct.computer_component_sell_price_settings_attributes.find(sell_price => sell_price.day_type === 'default')
            if (defaultPriceSetting) {
                const defaultPriceSettingParams = {
                    id: defaultPriceSetting?.id,
                    day_type: defaultPriceSetting?.day_type,
                    price_per_unit: Number(defaultPrice),
                    active: true
                };
                tempSellPrices.push(defaultPriceSettingParams);
            }
            

            // 2. Create the daily price settings
            const dailyPriceSettingsParams = onEditProduct.computer_component_sell_price_settings_attributes
                .map(priceSetting => {
                    const foundDayPricing = dayPricing.find(sellPrice => sellPrice.day_type === priceSetting.day_type)
                    return {
                        id: priceSetting.id, // Include ID if exists for update
                        day_type: priceSetting.day_type.toLowerCase(),
                        price_per_unit: Number(foundDayPricing?.price_per_unit || priceSetting.price_per_unit),
                        active: foundDayPricing?.active || priceSetting.active
                    };
                });
            tempSellPrices.push(...dailyPriceSettingsParams);
            setSellPricesAttributes(tempSellPrices);

            const payload: ProductParams = {
                ...onEditProduct,
                id: onEditProduct.id,
                category_id: category.id,
                images: imageUrl ? [imageUrl] : [],
                computer_component_sell_price_settings_attributes: tempSellPrices
            };
    
            const response = await fetch("http://localhost:8000/api/computer-components/" + onEditProduct.id, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
    
            if (!response.ok) {
                await handleApiError(response, showErrorToast);
                return;
            }
    
            const data = await response.json();
            showSuccessToast(data.message || "Product updated successfully");
    
            setIsEditMode(false);
            setIsAddDialogOpen(false);
            window.location.reload();
        } catch (error) {
            showErrorToast("Failed to update product. Please try again.");
        } finally {
            setFalseLoading();
        }
    };

    const handleClose = () => {
        setIsEditMode(false)
        resetForm()
        setIsDialogOpen(false)
    };

    function capitalizeFirstLetter(string: string) {
        if (!string) return '';
        return string.charAt(0).toUpperCase() + string.slice(1);
    }

    return (
        <Dialog open={isDialogOpen} onOpenChange={handleClose}>
            <DialogContent className="sm:max-w-[900px] p-0 overflow-hidden">
                <DialogClose className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
                        <X className="h-4 w-4" />
                        <span className="sr-only">Close</span>
                </DialogClose>

                {
                    (
                        <div className="grid md:grid-cols-2 gap-0">
                            <div className="relative h-full min-h-[300px] md:min-h-[500px] bg-muted">
                                <Image 
                                    src={ product?.image || "/placeholder.svg" }
                                    alt={ product.name }
                                    fill
                                    className="object-cover"
                                />
                            </div>

                            { /* Right side - Product Form */ }
                            <div className="p-6">
                                <DialogHeader className="flex flex-row items-center justify-between">
                                    <DialogTitle className="text-x1 font-bold">Product Details</DialogTitle>
                                    <div className="flex items-center gap-2">
                                        {
                                            !isEditMode && (
                                                <>
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        onClick={handleDeleteClick}
                                                        className="flex items-center gap-1 text-destructive hover:text-destructive"
                                                        disabled={isLoading}>
                                                        <Trash2 className="h-4 w-4" />
                                                    </Button>
                                                    <Button variant="outline" size="sm" onClick={toggleEditMode}
                                                    className="flex items-center gap-1"
                                                    disabled={isLoading}>
                                                        <Edit className="h-4 w-4"/>
                                                        Edit
                                                    </Button>
                                                </>
                                            )
                                        }
                                    </div>
                                </DialogHeader>

                                <form onSubmit={isEditMode ? handleUpdateProduct : undefined} className="grid gap-4 py-4 mt-2">
                                    <Tabs defaultValue="info" className="w-full">
                                        <TabsList className="grid w-full grid-cols-2">
                                            <TabsTrigger value="info">Product Info</TabsTrigger>
                                            <TabsTrigger value="pricing">Pricing</TabsTrigger>
                                        </TabsList>

                                        {/* Product Info Tab */}
                                        <TabsContent value="info" className="space-y-4 py-4">
                                            <div className="grid gap-2">
                                            <Label htmlFor="name">Name</Label>
                                            <Input
                                                id="name"
                                                defaultValue={product.name}
                                                disabled={!isEditMode || isLoading}
                                                onChange={(e) => handleEditProductChange("name", e.target.value)}
                                                className={!isEditMode ? "opacity-80" : ""}
                                                required
                                            />
                                        </div>

                                        <div className="grid gap-2">
                                            <Label htmlFor="component_category_name">Category</Label>
                                            <Select 
                                                defaultValue={product.component_category_name}
                                                disabled={!isEditMode || isLoading}
                                                onValueChange={isEditMode ? (value) => handleEditProductChange("component_category_name", value) : undefined}
                                                required
                                            >
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select a category"/>
                                                </SelectTrigger>
                                                <SelectContent>
                                                    {categories.map((category) => (
                                                        <SelectItem key={category} value={category}>
                                                            {category}
                                                        </SelectItem>
                                                    ))}
                                                </SelectContent>
                                            </Select>
                                        </div>

                                        <div className="grid gap-2">
                                            <Label htmlFor="description">Description</Label>
                                            <Textarea 
                                                id="description"
                                                rows={4}
                                                defaultValue={product.description || ""}
                                                disabled={!isEditMode || isLoading}
                                                className={!isEditMode ? "opacity-80" : ""}
                                                onChange={(e) => handleEditProductChange("description", e.target.value)}
                                            />
                                        </div>

                                        {
                                            isEditMode && (
                                                <div className="grid gap-2">
                                                    <Label htmlFor="image">Product Image</Label>
                                                    <div className="flex items-center gap-4">
                                                        <div className="relative h-24 w-24 border-gray-200 border rounded overflow-hidden">
                                                            <Image 
                                                                src={product.image || "/placeholder.svg"}
                                                                alt="Product preview"
                                                                fill
                                                                className="object-cover"
                                                            />
                                                        </div>
                                                        <input 
                                                            type="file"
                                                            ref={fileInputRef}
                                                            onChange={handleFileSelect}
                                                            accept="image/*"
                                                            className="hidden"
                                                        />
                                                        <Button
                                                            type="button"
                                                            variant="outline"
                                                            className="h-10"
                                                            onClick={handleUploadClick}
                                                            disabled={isLoading}>
                                                            <Upload className="h-4 w-4 mr-2" />
                                                            Change Image
                                                        </Button>
                                                    </div>
                                                    <p className="text-sm text-muted-foreground">
                                                        Recommended: 1000x1000px, max 5MB
                                                    </p>
                                                </div>
                                            )
                                        }

                                        {
                                            isEditMode && (
                                                <div className="flex justify-end gap-2 mt-4">
                                                    <Button type="button" variant="outline" onClick={toggleEditMode} disabled={isLoading}>
                                                        Cancel
                                                    </Button>
                                                    <Button type="submit" className="flex items-center gap-1" disabled={isLoading}>
                                                        <Save className="h-4 w-4" />
                                                        Update
                                                    </Button>
                                                </div>
                                            )
                                        }
                                        </TabsContent>

                                        {/* Pricing Tab */}
                                        <TabsContent value="pricing" className="space-y-4 py-4">
                                            <div className="p-3 border rounded-lg">
                                                <div className="grid gap-2">
                                                    <Label htmlFor="default-price" className="required">
                                                        Default Price
                                                    </Label>
                                                    <Input 
                                                        id="default-price"
                                                        type="number"
                                                        placeholder="0.00"
                                                        value={defaultPrice === "0" ? "" : parseFloat(defaultPrice).toFixed(0)}
                                                        onChange={(e) => setDefaultPrice(e.target.value)}
                                                        className="mt-1"
                                                        step="0.01"
                                                        min="0"
                                                        required
                                                        disabled={!isEditMode || isLoading}
                                                    />
                                                </div>
                                            </div>

                                            <div className="space-y-2">
                                                <Label className="text-base font-semibold">Daily Pricing (Optional)</Label>
                                                <div className="space-y-2 max-h-64 overflow-y-auto pr-2">
                                                    {
                                                        dayPricing.map((priceSetting, index) => (
                                                            <div key={priceSetting.day_type} className="flex items-center justify-between p-3 border rounded-lg">
                                                                <div className="flex-1 mr-4">
                                                                    <Label className="font-medium">{capitalizeFirstLetter(priceSetting.day_type)}</Label>
                                                                    <Input
                                                                        type="number"
                                                                        placeholder="0.00"
                                                                        value={priceSetting.price_per_unit === 0 ? "" : Number(priceSetting.price_per_unit).toFixed(0)}
                                                                        onChange={(e) => handlePriceChange(index, e.target.value)}
                                                                        className="mt-1"
                                                                        step="0.01"
                                                                        min="0"
                                                                        disabled={!isEditMode || isLoading}
                                                                    />
                                                                </div>
                                                                <div className="flex items-center space-x-2">
                                                                    <Label className="text-sm">Active</Label>
                                                                    <Switch
                                                                        checked={priceSetting.active}
                                                                        onCheckedChange={(checked) => handleActiveToggle(index, checked)}
                                                                        disabled={!isEditMode || isLoading}
                                                                    />
                                                                </div>
                                                            </div>
                                                        ))
                                                    }
                                                </div>
                                                <p className="text-sm text-muted-foreground mt-2">
                                                    Activate daily pricing for specific days if different from the default.
                                                </p>
                                            </div>
                                        </TabsContent>
                                    </Tabs>
                                </form>
                            </div>
                        </div>
                    )
                }
            </DialogContent>
        </Dialog>
    )
}