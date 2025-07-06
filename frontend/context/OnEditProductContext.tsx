import { createContext, useContext, useState, ReactNode } from 'react';
import type { ProductInFrontend } from '@/types/product'; // adjust path

type OnEditProductContextType = {
  onEditProduct: ProductInFrontend;
  setOnEditProduct: (product: ProductInFrontend) => void;
  selectedProduct: ProductInFrontend | null;
  handleEditProductChange: (field: string, value: any) => void;
  handleEditProductChangeInt: (field: string, value: number) => void;
};

interface OnEditProductProviderProps {
  children: ReactNode;
  selectedProduct: ProductInFrontend | null;
}

const OnEditProductContext = createContext<OnEditProductContextType | undefined>(undefined);

export const OnEditProductProvider = ({ children, selectedProduct }: OnEditProductProviderProps) => {
  const [onEditProduct, setOnEditProduct] = useState<ProductInFrontend>({
    id: selectedProduct?.id,
    name: selectedProduct?.name || "",
    component_category_name: selectedProduct?.component_category_name || "",
    price: (selectedProduct?.price || 0).toString(),
    description: selectedProduct?.description || "",
    stock: (selectedProduct?.stock || 0).toString(),
    image: "/placeholder.svg?height=300&width=300",
    component_category_id: selectedProduct?.component_category_id,
    product_code: selectedProduct?.product_code,
    status: selectedProduct?.status,
  });

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
      handleEditProductChangeInt
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
