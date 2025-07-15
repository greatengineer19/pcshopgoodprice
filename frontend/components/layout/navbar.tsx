"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { ChevronDown, Globe, SwitchCamera, ShoppingBasket, FileText } from "lucide-react"
// import { userContext } from "@/context/user-context"
import { fetchUser } from "@/lib/user-service"
import { fetchCart } from "@/lib/cart-service"
import {
    NavigationMenu,
    NavigationMenuContent,
    NavigationMenuItem,
    NavigationMenuLink,
    NavigationMenuList,
    NavigationMenuTrigger
} from "@/components/ui/navigation-menu"
import { Button } from "@/components/ui/button"
import { CartLine } from "@/types/cart"
import { GetUserResponseAPI, User, UserRole } from "@/types/user"
import { useUser } from "@/hooks/use-user"
import { redirect } from 'next/navigation'

export function Navbar() {
    const SECRET_KEY_NAME = 'secret_key';
    const REFRESH_KEY_NAME = 'refresh_key';
    const [language, setLanguage] = useState<"English" | "Indonesia">("English")
    const {
        user, role, setRole, setUser
    } = useUser()
    const [cartItemCount, setCartItemCount] = useState(0)

    // Load cart item count
    useEffect(() => {
        const loadCartCount = async () => {
            if (user && role === "buyer") {
                try {
                    const cartLines: CartLine[] = await fetchCart()
                    setCartItemCount(cartLines.length)
                } catch (error) {
                    console.error("Failed to load cart count:", error)
                }
            }
        }

        loadCartCount()
    }, [role])

    const toggleRole = async () => {
        let requestRole = role === "seller" ? "buyer" : "seller"

        const response: GetUserResponseAPI = await fetchUser(requestRole)
        const responseUser = response.user;

        localStorage.setItem(SECRET_KEY_NAME, response.access_token);
        localStorage.setItem(REFRESH_KEY_NAME, response.refresh_token);

        const userRole: UserRole = responseUser.role.toLowerCase() as UserRole;
        setUser(responseUser)
        setRole(userRole)

        if (userRole == "buyer") {
            redirect('/shop')
        } else {
            redirect('/computer_components')
        }
    }
    
    return (
        <div className="border-b">
            <div className="container mx-auto flex h-16 items-center justify-between px-4">
                {/* Logo */}
                <Link href="/computer_components" className="flex items-center">
                    <span className="text-xl font-normal" style={{ fontFamily: "'Tinos', serif", fontWeight: 400 }}>
                        PCSHOP GOOD PRICE
                    </span>
                </Link>

                {/* Navigation - Different based on role */}
                {
                    role === "seller" ? (
                        <NavigationMenu>
                            <NavigationMenuList>
                                {/* Computer Components */}
                                <NavigationMenuItem>
                                    <NavigationMenuTrigger>
                                        Computer Components
                                    </NavigationMenuTrigger>
                                    <NavigationMenuContent>
                                        <ul className="grid w-[200px] gap-3 p-4">
                                            <li>
                                                <NavigationMenuLink asChild>
                                                    <Link 
                                                        href="/computer_components"
                                                        className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                                                    >
                                                        <div className="text-sm font-medium">Computer Components</div>
                                                        <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                                                            View and manage components
                                                        </p>
                                                    </Link>
                                                </NavigationMenuLink>
                                            </li>
                                            <li>
                                                <NavigationMenuLink asChild>
                                                    <Link 
                                                        href="/test_api"
                                                        className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                                                    >
                                                        <div className="text-sm font-medium">*Demo Data Seeding</div>
                                                        <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                                                            Seeds demo data for first time use
                                                        </p>
                                                    </Link>
                                                </NavigationMenuLink>
                                            </li>
                                        </ul>
                                    </NavigationMenuContent>
                                </NavigationMenuItem>

                                {/* Purchase Invoice */}
                                <NavigationMenuItem>
                                    <NavigationMenuTrigger>Procurement</NavigationMenuTrigger>
                                    <NavigationMenuContent>
                                        <ul className="grid w-[200px] gap-3 p-4">
                                            <li>
                                                <NavigationMenuLink asChild>
                                                    <Link 
                                                        href="/purchase_invoices"
                                                        className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hovers:bg-accent hover:text-accent-foreground focus:bg-accent focus:textt-accent-foreground"
                                                    >
                                                        <div className="text-sm font-medium">Purchase Invoice</div>
                                                        <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                                                            Manage purchase invoices
                                                        </p>
                                                    </Link>
                                                </NavigationMenuLink>
                                            </li>
                                            <li>
                                                <NavigationMenuLink asChild>
                                                    <Link 
                                                        href="/inbound_deliveries"
                                                        className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hovers:bg-accent hover:text-accent-foreground focus:bg-accent focus:textt-accent-foreground"
                                                    >
                                                        <div className="text-sm font-medium">Inbound Delivery</div>
                                                        <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                                                            Manage inbound deliveries
                                                        </p>
                                                    </Link>
                                                </NavigationMenuLink>
                                            </li>
                                        </ul>
                                    </NavigationMenuContent>
                                </NavigationMenuItem>

                                {/* Report */}
                                <NavigationMenuItem>
                                    <NavigationMenuTrigger>Report</NavigationMenuTrigger>
                                    <NavigationMenuContent>
                                        <ul className="grid w-[220px] gap-3 p-4">
                                            <li>
                                                <NavigationMenuLink asChild>
                                                    <Link 
                                                        href="/report/purchase_invoices"
                                                        className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hovers:bg-accent hover:text-accent-foreground focus:bg-accent focus:textt-accent-foreground"
                                                    >
                                                        <div className="text-sm font-medium">Report Purchase Invoice</div>
                                                        <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                                                            View purchase invoice reports
                                                        </p>
                                                    </Link>
                                                </NavigationMenuLink>
                                            </li>
                                            <li>
                                                <NavigationMenuLink asChild>
                                                    <Link 
                                                        href="/report/inventories"
                                                        className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hovers:bg-accent hover:text-accent-foreground focus:bg-accent focus:textt-accent-foreground"
                                                    >
                                                        <div className="text-sm font-medium">Report Inventory Movement</div>
                                                        <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                                                            View inventory movement reports
                                                        </p>
                                                    </Link>
                                                </NavigationMenuLink>
                                            </li>
                                        </ul>
                                    </NavigationMenuContent>
                                </NavigationMenuItem>
                            </NavigationMenuList>
                        </NavigationMenu>
                    ) : (
                        <NavigationMenu>
                            <NavigationMenuList>
                                {/* Computer Components - Buyer View */}
                                <NavigationMenuItem>
                                    <NavigationMenuLink asChild>
                                        <Link 
                                            href="/shop"
                                            className="flex h-10 w-full items-center justify-between px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                                        >
                                            Shop Products
                                        </Link>
                                    </NavigationMenuLink>
                                </NavigationMenuItem>
                            </NavigationMenuList>
                        </NavigationMenu>
                    )
                }

                {/* Right side items */}
                <div className="flex items-center space-x-4">
                    {/* Language Selector */}
                    <div className="relative">
                        <button 
                            className="flex items-center space-x-1 text-sm"
                            onClick={() => setLanguage(language === "English" ? "Indonesia" : "English")}
                            disabled={true}
                        >
                            <Globe className="h-4 w-4"/>
                            <span>{language}</span>
                            <ChevronDown className="h-3 w-3" />
                        </button>
                    </div>

                    {/* User Greeting */}
                    <button onClick={toggleRole} className="text-sm hover:underline cursor-pointer">
                        Switch to { role === "buyer" ? "Seller" : "Buyer" }
                    </button>

                    {/* Buyer-specific icons */}
                    {
                        role === "buyer" && (
                            <>
                                {/* Shopping Basket */}
                                <Link href="/cart">
                                    <Button variant="ghost" size="icon" className="relative">
                                        <ShoppingBasket className="h-5 w-5" />
                                        {
                                            cartItemCount > 0 && (
                                                <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] text-white">
                                                    {cartItemCount}
                                                </span>
                                            )
                                        }
                                    </Button>
                                </Link>

                                {/* Orders/Invoices */}
                                <Link href="/orders">
                                        <Button variant="ghost" size="icon">
                                            <FileText className="h-5 w-5" />
                                        </Button>
                                </Link>
                            </>
                        )
                    }
                </div>
            </div>
        </div>
    )
}