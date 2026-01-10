class AddAccountToPayment < ActiveRecord::Migration[8.1]
  def change
    add_reference :payments, :debit_account, foreign_key: { to_table: :accounts }, if_not_exists: true
  end
end
