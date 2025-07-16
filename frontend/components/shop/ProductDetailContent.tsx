"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import Link from "next/link"
import { useParams, useRouter } from "next/navigation"
import { fetchProductBySlug } from "@/lib/product-service"
import { addToCart } from "@/lib/cart-service"
import { Star, ShoppingCart, ArrowLeft, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { cn } from "@/lib/utils"
import { toast } from "sonner"
import type { ShopContentProduct, ComputerComponentReview } from "@/types/product"

export default function ProductDetailContent() {
    const { slug } = useParams()
    const router = useRouter()
    const [product, setProduct] = useState<ShopContentProduct | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [isAddingToCart, setIsAddingToCart] = useState(false)
    const [quantity, setQuantity] = useState(1)
    const [selectedImage, setSelectedImage] = useState(0)
    const [notFound, setNotFound] = useState(false)

    useEffect(() => {
        const loadProduct = async () => {
            setIsLoading(true)

            try {
                const productData = await fetchProductBySlug(slug as string)
                setProduct(productData)

                if (productData.images?.length) {
                    setSelectedImage(0)
                }
            } catch (error) {
                setNotFound(true)
                console.error("Failed to load product:", error)
            } finally {
                setIsLoading(false)
            }
        }

        if (slug) {
            loadProduct()
        }
    }, [slug])

    if (notFound) {
        return <div style={{ position: 'relative', width: '100%', height: '800px' }}>
             <Image 
                src={"/data_not_found.png"}
                alt={"not found"}
                fill
                sizes="(max-width: 768px) 100vw,
                            (max-width: 1200px) 50vw,
                            33vw"
                className="object-contain p-6"
            />
        </div>
    }

    const handleQuantityChange = (value: number) => {
        if (value >= 1) {
            setQuantity(value)
        }
    }

    const handleAddToCart = async () => {
        if (!product) return

        setIsAddingToCart(true)

        try {
            await addToCart(product.id, quantity)
            toast.success(`${quantity} ${quantity > 1 ? "items" : "item" }`)
        } catch (error) {
            toast.error("Failed to add to cart")
            console.error("Failed to add to cart:", error)
        } finally {
            setIsAddingToCart(false)
        }
    }

    const handleBuyNow = async () => {
        if (!product) return

        setIsAddingToCart(true)
        try {
            await addToCart(product.id, 1)
            router.push("/cart")
        } catch (error) {
            toast.error("Failed to process your order")
            console.error("Failed to buy now:", error)
        } finally {
            setIsAddingToCart(false)
        }
    }

    if (isLoading) {
        return (
            <div className="container mx-auto px-4 py-8 flex justify-center items-center min-h-[60vh]">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        )
    }

    if (!product) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="text-center py-12 border rounded-md">
                    <p className="text-muted-foreground">Product not found.</p>
                    <Link href="/shop" className="text-primary hover:underline mt-4 inline-block">
                        Back to Shop
                    </Link>
                </div>
            </div>
        )
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <Link href="/shop" className="flex items-center text-sm mb-6 hover:underline">
                <ArrowLeft className="h-4 w-4 mr-1" />
                Back to Shop
            </Link>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
                {/* Product Images */}
                <div className="space-y-4">
                    <div className="relative aspect-square border rounded-lg overflow-hidden bg-gray-100">
                        <div className="absolute top-4 left-4 bg-red-500 text-white text-sm font-bold px-2 py-1 rounded-md z-10">
                            33% OFF
                        </div>
                        <Image 
                            src={product.images ? product.images[selectedImage] : "placeholder.svg?height=500&width=500"}
                            alt={product.name}
                            fill
                            className="object-contain p-6"
                        />
                    </div>

                    {/* Thumbnail Images */}
                    {
                        product.images && product.images.length > 1 && (
                            <div className="flex space-x-2 overflow-x-auto pb-2">
                                {
                                    product.images.map((image, index) => (
                                        <div
                                            key={image}
                                            className={cn(
                                                "relative w-20 h-20 border rounded cursor-pointer overflow-hidden",
                                                selectedImage === index ? "border-primary" : "border-gray-200",
                                            )}
                                            onClick={() => setSelectedImage(index)}
                                        >
                                            <Image src={image || "placeholder.svg"} alt={image} fill className="object-contain p-2" />
                                        </div>
                                    ))
                                }
                            </div>
                        )
                    }
                </div>

                {/* Product Details */}
                <div className="space-y-6">
                    <div>
                        <h1 className="text-2xl font-bold mb-2">{product.name}</h1>
                        <div className="flex items-center mb-4">
                            <div className="flex">
                                {
                                    [1,2,3,4,5].map((star) => (
                                        <Star
                                            key={star}
                                            className={cn(
                                                "h-4 w-4",
                                                star <= Math.round(product.rating) ? "text-yellow-400 fill-yellow-400" : "text-gray-300"
                                            )}
                                        />
                                    ))
                                }
                            </div>
                            <span className="text-sm text-gray-500 ml-2">
                                {product.rating.toFixed(1)} ({product.count_review_given} reviews)
                            </span>
                        </div>

                        <div className="flex items-center mb-4">
                            <span className="text-2xl font-bold">
                                Rp {(product.sell_price).toLocaleString()}
                            </span>
                            <span className="text-gray-500 text-lg line-through ml-3">Rp {(Math.round(( product.sell_price / (1 - 0.33)) / 1000) * 1000).toLocaleString()}</span>
                        </div>

                        <span className="text-sm font-medium mr-4">Description:</span>
                        <p className="text-gray-600 mb-6">{product.description}</p>
                        <div className="flex items-center mb-6">
                            <span className="text-sm font-medium mr-4">Availability:</span>
                            {
                                1 == 1 ? (
                                    <span className="text-green-600">In stock (10 available)</span>
                                ) : (
                                    <span className="text-red-600">Out of stock</span>
                                )
                            }
                        </div>

                        <div className="flex items-center mb-6">
                            <span className="text-sm font-medium mr-4">Brand:</span>
                            <span>Available soon</span>
                        </div>
                    </div>

                    {/* Quantity Selector */}
                    <div className="flex items-center space-x-4">
                        <span className="text-sm font-medium">Quantity:</span>
                        <div className="flex items-center border rounded-md">
                            <button 
                                className="px-3 py-1 border-r"
                                onClick={() => handleQuantityChange(quantity - 1)}
                                disabled={quantity <= 1}
                            >-</button>
                            <input 
                                type="number"
                                value={quantity}
                                onChange={(e) => handleQuantityChange(Number(e.target.value))}
                                className="w-12 text-center py-1 border-none focus:outline-none focus:ring-0"
                                min="1"
                            />
                            <button 
                                className="px-3 py-1 border-l"
                                onClick={() => handleQuantityChange(quantity + 1)}
                            >+</button>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-col sm:flex-row gap-4">
                        <Button
                            className="flex-1"
                            size="lg"
                            onClick={handleAddToCart}
                            disabled={isAddingToCart}
                        >
                            <ShoppingCart className="mr-2 h-5 w-5" />
                            {isAddingToCart ? "Adding..." : "Add to Cart"}
                        </Button>
                        <Button 
                            variant="secondary"
                            className="flex-1"
                            size="lg"
                            onClick={handleBuyNow}
                            disabled={isAddingToCart}
                        >
                            {isAddingToCart ? "Processing..." : "Buy Now"}
                        </Button>
                    </div>
                </div>
            </div>

            {/* Product Tabs */}
            <Tabs defaultValue="sepcifications">
                <TabsList className="w-full justify-start border-b rounded-none">
                    <TabsTrigger value="specifications">Specifications</TabsTrigger>
                    <TabsTrigger value="reviews">Reviews</TabsTrigger>
                </TabsList>
                <TabsContent value="specifications" className="pt-6">
                    {
                        product.description && product.description.length > 10 ? (
                            <p className="text-muted-foreground">{product.description}</p>
                        ) : (
                            <p className="text-muted-foreground">No specifications available yet for this product.</p>
                        )
                    }
                </TabsContent>
                <TabsContent value="reviews" className="pt-6">
                    { product.computer_component_reviews ? (
                        <div className="space-y-6">
                            {product.computer_component_reviews.map((review: ComputerComponentReview) => (
                                <div key={review.id} className="border-b pb-4">
                                    <div className="flex justify-between mb-2">
                                        <div>
                                            <span className="font-medium">{review.user_fullname}</span>
                                            <div className="flex mt-1">
                                                {[1,2,3,4,5].map((star) => (
                                                    <Star 
                                                        key={star}
                                                        className={cn(
                                                            "h-3 w-3",
                                                            star <= review.rating ? "text-yellow-400 fill-yellow-400" : "text-gray-300"
                                                        )}
                                                    />
                                                ))}
                                            </div>
                                        </div>
                                        <span className="text-sm text-gray-500">{new Date(review.created_at).toLocaleDateString()}</span>
                                    </div>
                                    <p className="text-gray-600">{review.comments}</p>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-muted-foreground">No reviews yet for this product.</p>
                    )}
                </TabsContent>
            </Tabs>
        </div>
    )
}