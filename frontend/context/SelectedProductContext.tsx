import { createContext, useContext, useState, ReactNode } from 'react';
import type { ProductInFrontend } from '@/types/product'; // adjust path

type SelectedProductContextType = {
  selectedProduct: ProductInFrontend | null;
  setSelectedProduct: (product: ProductInFrontend | null) => void;
};

const SelectedProductContext = createContext<SelectedProductContextType | undefined>(undefined);

export const SelectedProductProvider = ({ children }: { children: ReactNode }) => {
  const [selectedProduct, setSelectedProduct] = useState<ProductInFrontend | null>(null);

  return (
    <SelectedProductContext.Provider value={{ selectedProduct, setSelectedProduct }}>
      {children}
    </SelectedProductContext.Provider>
  );
};

export const useSelectedProduct = () => {
  const context = useContext(SelectedProductContext);
  if (context === undefined) {
    throw new Error('useSelectedProduct must be used within a SelectedProductProvider');
  }
  return context;
};
