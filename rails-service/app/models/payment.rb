class Payment < ApplicationRecord
  enum :currency, { idr: 0, eur: 1, cad: 2, aud: 3, usd: 4 }
  enum :payment_method, { cash: 0, bca_transfer: 1, bni_transfer: 2 }
end
