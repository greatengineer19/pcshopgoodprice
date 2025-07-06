"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { ShoppingCart, Trash2, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Separator } from "@/components/ui/separator"
import { toast } from "sonner"
import { fetchCart, removeFromCart, listPaymentMethods } from "@/lib/cart-service"
import { createSalesQuote } from "@/lib/sales-quote-service"
import type { CartLine, PaymentMethod } from "@/types/cart"
import { useUser } from "@/hooks/use-user"

export default function CartPage() {
    const router = useRouter()
    const [cartLines, setCartLines] = useState<CartLine[] | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [isProcessing, setIsProcessing] = useState(false)
    const [address, setAddress] = useState("")
    const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
    const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<PaymentMethod | undefined>();
    const [itemsToDelete, setItemsToDelete] = useState<number[]>([])
    const [subtotal, setSubtotal] = useState<number>(0)
    const { user } = useUser()

    if (user == undefined) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
                    <ShoppingCart className="h-16 w-16 text-muted-foreground mb-4" />
                    <h1 className="text-3xl font-bold mb-4">Your Shopping Cart</h1>
                    <p className="text-muted-foreground mb-8 max-w-md">
                        Your shopping cart is currently empty. Browse our products to add items to your cart.
                    </p>
                    <Link href="/shop">
                        <Button className="flex items-center gap-2">Continue Shopping</Button>
                    </Link>
                </div>
            </div>
        )
    } 

    // Load cart data
    useEffect(() => {
        const loadCart = async () => {
            setIsLoading(true)
            try {
                const cartData = await fetchCart()
                setCartLines(cartData)

                let subtotalCalculator = 0
                cartLines?.forEach(cartLine => {
                    subtotalCalculator += cartLine.sell_price * cartLine.quantity;
                });
                setSubtotal(subtotalCalculator)
            } catch (error) {
                console.error("Failed to load cart:", error)
                toast.error("Failed to load your cart")
            } finally {
                setIsLoading(false)
            }
        }

        const fetchPaymentMethods = async () => {
            const methods = await listPaymentMethods();
            setPaymentMethods(methods);
            const defaultMethod = methods.find(item => item.name == "Virtual Account");
            setSelectedPaymentMethod(defaultMethod);
        }

        loadCart()
        fetchPaymentMethods()
    }, [])

    // Handle item deletion
    const handleDeleteItem = async (itemId: number) => {
        setItemsToDelete((prevId) => [...prevId, itemId])

        try {
            await removeFromCart(itemId)
            toast.success("Item removed from cart")

            window.location.reload()
        } catch (error) {
            console.error("Failed to remove item:", error)
            toast.error("Failed to remove item from cart")
        } finally {
            setItemsToDelete((prevId) => prevId.filter((id) => id !== itemId))
        }
    }

    const handleCheckout = async () => {
        if (!cartLines || cartLines.length === 0) {
            toast.error("Your cart is empty")
            return
        }

        if (!address.trim()) {
            toast.error("Please enter your shipping address")
            return
        }

        setIsProcessing(true)

        try {
            const paymentInfo = {
                paymentMethodId: selectedPaymentMethod?.id,
                paymentMethodName: selectedPaymentMethod?.name,
                virtualAccountNo: '',
                paylaterAccountReference: '',
                creditCardCustomerName: '',
                creditCardCustomerAddress: '',
                creditCardBankName: ''
            }

            await createSalesQuote(cartLines, address, paymentInfo, user)

            // Show success message
            toast.success("Sales Quote placed successfully!")
            router.push("/sales-quotes")
        } catch (error) {
            console.error("Failed to process order:", error)
            toast.error("Failed to process your order")
        } finally {
            setIsProcessing(false)
        }
    }

    // Empty cart view
    if (!isLoading && (!cartLines || cartLines.length === 0)) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
                    <ShoppingCart className="h-16 w-16 text-muted-foreground mb-4" />
                    <h1 className="text-3xl font-bold mb-4">Your Shopping Cart</h1>
                    <p className="text-muted-foreground mb-8 max-w-md">
                        Your shopping cart is currently empty. Browse our products to add items to your cart.
                    </p>
                    <Link href="/shop">
                        <Button className="flex items-center gap-2">Continue Shopping</Button>
                    </Link>
                </div>
            </div>
        )
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-8">Shopping Cart</h1>

            {
                isLoading ? (
                    <div className="flex justify-center items-center h-64">
                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Left Column - Address and Cart Items */}
                        <div className="lg:col-span-2 space-y-8">
                            {/* Address Section */}
                            <Card>
                                <CardContent className="pt-6">
                                    <h2 className="text-xl font-semibold mb-4">Shipping Address</h2>
                                    <div className="space-y-2">
                                        <Label htmlFor="address">Enter your complete address</Label>
                                        <Textarea 
                                            id="address"
                                            placeholder="Enter your full address including street, city, state, and zip code"
                                            value={address}
                                            onChange={(e) => setAddress(e.target.value)}
                                            rows={4}
                                            className="resize-none"
                                        />
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Draft Orders Section */}
                            <div>
                                <h2 className="text-xl font-semibold mb-4">Draft Orders</h2>
                                <Card>
                                    <CardContent className="pt-6">
                                        {
                                            cartLines?.map((cartLine) => (
                                                <div key={cartLine.id} className="flex items-start space-x-4 py-4 border-b last:border-0">
                                                    {/* Item being deleted indicator */}
                                                    {itemsToDelete.includes(cartLine.id) && (
                                                        <div className="absolute inset-0 bg-black/10 flex items-center justify-center z-10 rounded-md">
                                                            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
                                                        </div>
                                                    )}

                                                    {/* Product Image */}
                                                    <div className="relative h-20 w-20 flex-shrink-0 border rounded-md overflow-hidden">
                                                        <Image 
                                                            src={"/placeholder.svg"}
                                                            alt={cartLine.component_name}
                                                            fill
                                                            className="object-contain p-1"
                                                        />
                                                    </div>

                                                    {/* Product Details */}
                                                    <div className="flex-1 min-w-0">
                                                        <h3 className="font-medium text-sm line-clamp-2">{cartLine.component_name}</h3>
                                                        <p className="text-sm text-muted-foreground mt-1">
                                                            ${cartLine.sell_price.toFixed(2)} x {cartLine.quantity}
                                                        </p>
                                                    </div>

                                                    {/* Price and Delete */}
                                                    <div className="flex flex-col items-end space-y-2">
                                                        <span className="font-semibold">IDR {(cartLine.quantity * cartLine.sell_price).toFixed(2)}</span>
                                                        <Button 
                                                            variant="ghost"
                                                            size="sm"
                                                            className="text-red-500 hover:text-red-700 hover:bg-red-50 p-0 h-auto"
                                                            onClick={() => handleDeleteItem(cartLine.id)}
                                                            disabled={itemsToDelete.includes(cartLine.id)}
                                                        >
                                                            <Trash2 className="h-4 w-4" />
                                                        </Button>
                                                    </div>

                                                    {/* Cart Summary */}
                                                    <div className="mt-4 space-y-2">
                                                        <div className="flex justify-between">
                                                            <span className="text-muted-foreground">Subtotal</span>
                                                            <span>IDR {subtotal.toFixed(2)}</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span className="text-muted-foreground">Tax</span>
                                                            <span>IDR 0</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span className="text-muted-foreground">
                                                                Shipping
                                                            </span>
                                                            <span>IDR 0</span>
                                                        </div>
                                                        {
                                                            1 == 1 && (
                                                                <div className="flex justify-between text-green-600">
                                                                    <span>Discount</span>
                                                                    <span>-IDR 0</span>
                                                                </div>
                                                            )
                                                        }
                                                    </div>
                                                </div>
                                            ))
                                        }
                                    </CardContent>
                                </Card>
                            </div>
                        </div>

                        {/* Right Column - Payment Methods (Sticky) */}
                        <div className="lg:col-span-1">
                            <div className="sticky top-4">
                                <Card>
                                    <CardContent className="pt-6">
                                        <h2 className="text-xl font-semibold mb-4">Payment Method</h2>

                                        <RadioGroup
                                            value={selectedPaymentMethod?.name}
                                            onValueChange={(value) => {
                                                const selected = paymentMethods.find(method => method.name === value);
                                                setSelectedPaymentMethod(selected);
                                            }}
                                            className="space-y-3"
                                        >
                                            {
                                                paymentMethods.map((method) => (
                                                    <div
                                                        key={method.id}
                                                        className="flex items-center space-x-2 border rounded-md p-3"
                                                    >
                                                    <RadioGroupItem
                                                        value={method.name}
                                                        id={String(method.id)}
                                                        disabled={method.name !== "Virtual Account"}
                                                    />
                                                    <Label htmlFor={String(method.id)} className="flex-1 cursor-pointer">
                                                        <div className="font-medium">{method.name}</div>
                                                        <div className="text-sm text-muted-foreground">
                                                        Pay using {method.name}
                                                        </div>
                                                    </Label>
                                                </div>
                                            ))}
                                        </RadioGroup>


                                        <Separator className="my-6" />

                                        {/* Total Amount */}
                                        <div className="flex justify-between items-center mb-6">
                                            <span className="text-lg font-medium">Total Amount</span>
                                            <span className="text-xl font-bold">IDR {subtotal.toFixed(2)}</span>
                                        </div>

                                        {/* Checkout Button */}
                                        <Button 
                                            className="w-full"
                                            size="lg"
                                            onClick={handleCheckout}
                                            disabled={isProcessing || !cartLines || cartLines.length === 0 }
                                        >
                                            {
                                                isProcessing ? "Processing..." : "Pay now"
                                            }
                                        </Button>

                                        {/* Payment Notice */}
                                        <div className="flex items-start mt-4 text-sm text-muted-foreground">
                                            <AlertCircle className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                                            <p>
                                                By clicking "Pay Now", you agree to our terms and conditions. This is a demo application, no real
                                                payment will be processed.
                                            </p>
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>
                        </div>
                    </div>
                )
            }
        </div>
    )
}