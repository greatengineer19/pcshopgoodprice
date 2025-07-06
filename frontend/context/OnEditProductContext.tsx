import { createContext, useContext, useState, ReactNode } from 'react';
import type { ProductInFrontend, ProductParams } from '@/types/product'; // adjust path

type OnEditProductContextType = {
  onEditProduct: ProductParams;
  setOnEditProduct: (product: ProductParams) => void;
  selectedProduct: ProductInFrontend | null;
  handleEditProductChange: (field: string, value: any) => void;
  handleEditProductChangeInt: (field: string, value: number) => void;
  defaultPrice: string,
  setDefaultPrice: React.Dispatch<React.SetStateAction<string>>;
};

interface OnEditProductProviderProps {
  children: ReactNode;
  selectedProduct: ProductInFrontend | null;
}

const OnEditProductContext = createContext<OnEditProductContextType | undefined>(undefined);

export const OnEditProductProvider = ({ children, selectedProduct }: OnEditProductProviderProps) => {
  const [onEditProduct, setOnEditProduct] = useState<ProductParams>({
    id: selectedProduct != undefined ? selectedProduct?.id : 0,
    name: selectedProduct?.name || "",
    component_category_name: selectedProduct?.component_category_name || "",
    description: selectedProduct?.description || "",
    image: "/placeholder.svg?height=300&width=300",
    component_category_id: selectedProduct?.component_category_id ? selectedProduct.component_category_id : null,
    status: selectedProduct?.status,
    product_code: selectedProduct?.product_code || "",
    computer_component_sell_price_settings_attributes: selectedProduct?.computer_component_sell_price_settings || []
  });
    
  const [defaultPrice, setDefaultPrice] = useState("")
  const defaultPriceSetting = onEditProduct.computer_component_sell_price_settings_attributes.find(sell_price => sell_price.day_type === 'default')

  if (defaultPriceSetting) {
    setDefaultPrice(String(defaultPriceSetting.price_per_unit))
  }

  const handleEditProductChange = (field: string, value: any) => {
    setOnEditProduct({
      ...onEditProduct,
      [field]: value
    });
  };

  const handleEditProductChangeInt = (field: string, value: number) => {
    setOnEditProduct({
      ...onEditProduct,
      [field]: value
    });
  };

  return (
    <OnEditProductContext.Provider value={{
      onEditProduct,
      setOnEditProduct,
      selectedProduct,
      handleEditProductChange,
      handleEditProductChangeInt,
      defaultPrice,
      setDefaultPrice
    }}>
      {children}
    </OnEditProductContext.Provider>
  );
};

export const useOnEditProduct = () => {
  const context = useContext(OnEditProductContext);
  if (context === undefined) {
    throw new Error('useOnEditProduct must be used within an OnEditProductProvider');
  }
  return context;
};
