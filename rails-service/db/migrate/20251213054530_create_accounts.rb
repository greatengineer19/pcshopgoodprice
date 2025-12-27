class CreateAccounts < ActiveRecord::Migration[8.1]
  def change
    create_table :tax_codes, if_not_exists: true do |t|
      t.string :name, null: false
      t.decimal :rate, precision: 20, scale: 6, default: "0.0", null: false

      t.timestamps
    end

    create_table :accounts, if_not_exists: true do |t|
      t.integer :account_code, null: false
      t.string :account_name, null: false
      t.integer :account_type, null: false
      t.integer :subtype, null: false
      t.references :parent, foreign_key: { to_table: :accounts }
      t.integer :normal_balance, null: false
      t.boolean :is_active
      t.references :tax_codes

      t.timestamps
    end

    add_index :accounts, :account_code, unique: true, if_not_exists: true
  end
end
