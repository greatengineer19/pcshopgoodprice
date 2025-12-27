class Account < ApplicationRecord
  enum :normal_balance, { debit: 0, credit: 1}
  enum :account_type, { asset: 0, liability: 1, equity: 2, revenue: 3, expense: 4 }
end
