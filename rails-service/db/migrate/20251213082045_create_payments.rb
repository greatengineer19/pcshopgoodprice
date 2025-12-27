class CreatePayments < ActiveRecord::Migration[8.1]
  def change
    create_table :payments, if_not_exists: true do |t|
      t.references :user, null: false
      t.references :account, null: false
      t.decimal :amount, precision: 20, scale: 6, default: "0.0", null: false
      t.integer :currency, null: false
      t.integer :payment_method, null: false
      t.timestamps
    end
  end
end
