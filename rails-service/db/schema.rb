# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.1].define(version: 2025_12_21_151543) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_catalog.plpgsql"

  create_table "accounts", id: :serial, force: :cascade do |t|
    t.integer "account_code", null: false
    t.string "account_name", null: false
    t.integer "account_type", null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.boolean "is_active", null: false
    t.integer "normal_balance", null: false
    t.integer "parent_id"
    t.integer "subtype", null: false
    t.integer "tax_code_id"
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
    t.index ["account_code"], name: "index_accounts_on_account_code", unique: true
    t.index ["parent_id"], name: "index_accounts_on_parent_id"
    t.index ["tax_code_id"], name: "index_accounts_on_tax_code_id"
  end

  create_table "cart_lines", id: :serial, force: :cascade do |t|
    t.integer "component_id", null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.integer "customer_id", null: false
    t.decimal "quantity", precision: 20, scale: 6, null: false
    t.integer "status", default: 0, null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
  end

  create_table "computer_component_categories", id: :serial, force: :cascade do |t|
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.string "name", null: false
    t.integer "status", default: 0, null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
    t.index ["id"], name: "ix_computer_component_categories_id"
    t.unique_constraint ["name"], name: "computer_component_categories_name_key"
  end

  create_table "computer_component_reviews", id: :serial, force: :cascade do |t|
    t.string "comments", null: false
    t.integer "component_id", null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.integer "rating", default: 0, null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
    t.string "user_fullname", null: false
    t.integer "user_id", null: false
  end

  create_table "computer_component_sell_price_settings", id: :serial, force: :cascade do |t|
    t.boolean "active", null: false
    t.integer "component_id", null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.integer "day_type", null: false
    t.decimal "price_per_unit", precision: 20, scale: 6, null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
  end

  create_table "computer_components", id: :serial, force: :cascade do |t|
    t.integer "component_category_id", null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.text "description"
    t.string "images", array: true
    t.string "name", null: false
    t.string "product_code", null: false
    t.integer "status", default: 0, null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
    t.index ["id"], name: "ix_computer_components_id"
    t.unique_constraint ["name"], name: "computer_components_name_key"
    t.unique_constraint ["product_code"], name: "computer_components_product_code_key"
  end

  create_table "inbound_deliveries", id: :serial, force: :cascade do |t|
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.boolean "deleted", null: false
    t.date "inbound_delivery_date", null: false
    t.string "inbound_delivery_no", null: false
    t.string "inbound_delivery_reference", null: false
    t.string "notes"
    t.integer "purchase_invoice_id", null: false
    t.string "purchase_invoice_no", null: false
    t.string "received_by"
    t.integer "status", default: 0, null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false

    t.unique_constraint ["inbound_delivery_no"], name: "inbound_deliveries_inbound_delivery_no_key"
  end

  create_table "inbound_delivery_attachments", id: :serial, force: :cascade do |t|
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.string "file_s3_key", null: false
    t.integer "inbound_delivery_id", null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
    t.string "uploaded_by", null: false

    t.unique_constraint ["file_s3_key"], name: "inbound_delivery_attachments_file_s3_key_key"
  end

  create_table "inbound_delivery_lines", id: :serial, force: :cascade do |t|
    t.integer "component_category_id", null: false
    t.string "component_category_name", null: false
    t.integer "component_id", null: false
    t.string "component_name", null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.decimal "damaged_quantity", precision: 20, scale: 6, null: false
    t.boolean "deleted", null: false
    t.decimal "expected_quantity", precision: 20, scale: 6, null: false
    t.integer "inbound_delivery_id", null: false
    t.string "notes"
    t.decimal "price_per_unit", precision: 20, scale: 6, null: false
    t.integer "purchase_invoice_line_id", null: false
    t.decimal "received_quantity", precision: 20, scale: 6, null: false
    t.decimal "total_line_amount", precision: 20, scale: 6, null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
  end

  create_table "inventories", id: :serial, force: :cascade do |t|
    t.decimal "buy_price", precision: 20, scale: 6
    t.integer "component_id", null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.decimal "in_stock", precision: 20, scale: 6
    t.decimal "out_stock", precision: 20, scale: 6
    t.integer "resource_id", null: false
    t.integer "resource_line_id", null: false
    t.string "resource_line_type", null: false
    t.string "resource_type", null: false
    t.date "stock_date", null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
    t.index ["resource_type", "resource_id"], name: "ix_resource_type_id"
  end

  create_table "journal_entries", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.integer "created_by_id"
    t.string "entry_number", null: false
    t.integer "fiscal_period"
    t.integer "fiscal_year"
    t.integer "reference_id", null: false
    t.string "reference_type"
    t.bigint "reversed_by_id"
    t.integer "status", null: false
    t.datetime "updated_at", null: false
    t.index ["reversed_by_id"], name: "index_journal_entries_on_reversed_by_id"
  end

  create_table "journal_entry_lines", force: :cascade do |t|
    t.bigint "account_id"
    t.datetime "created_at", null: false
    t.decimal "credit", precision: 20, scale: 6, default: "0.0", null: false
    t.decimal "debit", precision: 20, scale: 6, default: "0.0", null: false
    t.string "description"
    t.bigint "journal_entry_id"
    t.integer "line_number", null: false
    t.datetime "updated_at", null: false
    t.index ["account_id"], name: "index_journal_entry_lines_on_account_id"
    t.index ["journal_entry_id"], name: "index_journal_entry_lines_on_journal_entry_id"
    t.check_constraint "debit > 0::numeric AND credit = 0::numeric OR credit > 0::numeric AND debit = 0::numeric OR debit = 0::numeric AND credit = 0::numeric", name: "check_debit_credit"
  end

  create_table "payment_methods", id: :serial, force: :cascade do |t|
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.string "name", null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
  end

  create_table "payments", id: :serial, force: :cascade do |t|
    t.integer "account_id", null: false
    t.decimal "amount", precision: 20, scale: 6, null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.integer "currency", null: false
    t.integer "debit_account_id", null: false
    t.integer "payment_method", null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
    t.integer "user_id", null: false
    t.index ["account_id"], name: "index_payments_on_account_id"
    t.index ["debit_account_id"], name: "index_payments_on_debit_account_id"
    t.index ["user_id"], name: "index_payments_on_user_id"
  end

  create_table "purchase_invoice_lines", id: :serial, force: :cascade do |t|
    t.integer "component_category_id", null: false
    t.string "component_category_name", null: false
    t.integer "component_id", null: false
    t.string "component_name", null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.decimal "price_per_unit", precision: 20, scale: 6, null: false
    t.integer "purchase_invoice_id", null: false
    t.decimal "quantity", precision: 20, scale: 6, null: false
    t.decimal "total_line_amount", precision: 20, scale: 6, null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
  end

  create_table "purchase_invoices", id: :serial, force: :cascade do |t|
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.boolean "deleted", null: false
    t.date "expected_delivery_date"
    t.datetime "invoice_date", precision: nil, null: false
    t.string "notes"
    t.string "purchase_invoice_no", null: false
    t.integer "status", default: 0, null: false
    t.decimal "sum_total_line_amounts", precision: 20, scale: 6, null: false
    t.string "supplier_name", null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false

    t.unique_constraint ["purchase_invoice_no"], name: "purchase_invoices_purchase_invoice_no_key"
  end

  create_table "sales_deliveries", id: :serial, force: :cascade do |t|
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.string "sales_delivery_no", null: false
    t.integer "sales_invoice_id", null: false
    t.integer "status", default: 0, null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false

    t.unique_constraint ["sales_delivery_no"], name: "sales_deliveries_sales_delivery_no_key"
  end

  create_table "sales_delivery_lines", id: :serial, force: :cascade do |t|
    t.integer "component_id", null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.decimal "quantity", precision: 20, scale: 6, null: false
    t.integer "sales_delivery_id", null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
  end

  create_table "sales_invoice_lines", id: :serial, force: :cascade do |t|
    t.integer "component_id", null: false
    t.string "component_name", null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.decimal "price_per_unit", precision: 20, scale: 6, null: false
    t.decimal "quantity", precision: 20, scale: 6, null: false
    t.integer "sales_invoice_id", null: false
    t.decimal "total_line_amount", precision: 20, scale: 6, null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
  end

  create_table "sales_invoices", id: :serial, force: :cascade do |t|
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.string "credit_card_bank_name"
    t.string "credit_card_customer_address"
    t.string "credit_card_customer_name"
    t.integer "customer_id", null: false
    t.string "customer_name", null: false
    t.string "paylater_account_reference"
    t.integer "payment_method_id", null: false
    t.string "payment_method_name", null: false
    t.string "sales_invoice_no", null: false
    t.string "sales_quote_no", null: false
    t.string "shipping_address", null: false
    t.integer "status", default: 0, null: false
    t.decimal "sum_total_line_amounts", precision: 20, scale: 6, null: false
    t.decimal "total_payable_amount", precision: 20, scale: 6, null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
    t.string "virtual_account_no"

    t.unique_constraint ["sales_invoice_no"], name: "sales_invoices_sales_invoice_no_key"
    t.unique_constraint ["sales_quote_no"], name: "sales_invoices_sales_quote_no_key"
  end

  create_table "sales_quote_lines", id: :serial, force: :cascade do |t|
    t.integer "component_id", null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.decimal "price_per_unit", precision: 20, scale: 6, null: false
    t.decimal "quantity", precision: 20, scale: 6, null: false
    t.integer "sales_quote_id", null: false
    t.decimal "total_line_amount", precision: 20, scale: 6, null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
  end

  create_table "sales_quotes", id: :serial, force: :cascade do |t|
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.string "credit_card_bank_name"
    t.string "credit_card_customer_address"
    t.string "credit_card_customer_name"
    t.integer "customer_id", null: false
    t.string "customer_name", null: false
    t.string "paylater_account_reference"
    t.integer "payment_method_id", null: false
    t.string "payment_method_name", null: false
    t.string "sales_quote_no", null: false
    t.string "shipping_address", null: false
    t.decimal "sum_total_line_amounts", precision: 20, scale: 6, null: false
    t.decimal "total_payable_amount", precision: 20, scale: 6, null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
    t.string "virtual_account_no"

    t.unique_constraint ["sales_quote_no"], name: "sales_quotes_sales_quote_no_key"
  end

  create_table "tax_codes", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "name", null: false
    t.decimal "rate", precision: 20, scale: 6, default: "0.0", null: false
    t.datetime "updated_at", null: false
  end

  create_table "users", id: :serial, force: :cascade do |t|
    t.datetime "created_at", precision: nil, default: -> { "now()" }, null: false
    t.string "fullname", null: false
    t.string "hashed_password"
    t.string "password_digest"
    t.string "refresh_token"
    t.datetime "refresh_token_expiry_at", precision: nil, default: -> { "now()" }, null: false
    t.integer "role", default: 0, null: false
    t.datetime "updated_at", precision: nil, default: -> { "now()" }, null: false
    t.string "username"
    t.index ["id"], name: "ix_users_id", unique: true
    t.index ["refresh_token"], name: "index_users_on_refresh_token", unique: true
    t.index ["username"], name: "index_users_on_username", unique: true
    t.index ["username"], name: "ix_users_username", unique: true
    t.unique_constraint ["refresh_token"], name: "users_refresh_token_key"
  end

  add_foreign_key "cart_lines", "computer_components", column: "component_id", name: "cart_lines_component_id_fkey"
  add_foreign_key "cart_lines", "users", column: "customer_id", name: "cart_lines_customer_id_fkey"
  add_foreign_key "computer_component_reviews", "computer_components", column: "component_id", name: "computer_component_reviews_component_id_fkey"
  add_foreign_key "computer_component_reviews", "users", name: "computer_component_reviews_user_id_fkey"
  add_foreign_key "computer_component_sell_price_settings", "computer_components", column: "component_id", name: "computer_component_sell_price_settings_component_id_fkey"
  add_foreign_key "computer_components", "computer_component_categories", column: "component_category_id", name: "computer_components_component_category_id_fkey"
  add_foreign_key "inbound_deliveries", "purchase_invoices", name: "inbound_deliveries_purchase_invoice_id_fkey"
  add_foreign_key "inbound_delivery_attachments", "inbound_deliveries", name: "inbound_delivery_attachments_inbound_delivery_id_fkey"
  add_foreign_key "inbound_delivery_lines", "computer_component_categories", column: "component_category_id", name: "inbound_delivery_lines_component_category_id_fkey"
  add_foreign_key "inbound_delivery_lines", "computer_components", column: "component_id", name: "inbound_delivery_lines_component_id_fkey"
  add_foreign_key "inbound_delivery_lines", "inbound_deliveries", name: "inbound_delivery_lines_inbound_delivery_id_fkey"
  add_foreign_key "inbound_delivery_lines", "purchase_invoice_lines", name: "inbound_delivery_lines_purchase_invoice_line_id_fkey"
  add_foreign_key "inventories", "computer_components", column: "component_id", name: "inventories_component_id_fkey"
  add_foreign_key "journal_entries", "journal_entries", column: "reversed_by_id"
  add_foreign_key "journal_entry_lines", "accounts"
  add_foreign_key "payments", "accounts", column: "debit_account_id", name: "payments_debit_account_id_fkey"
  add_foreign_key "payments", "accounts", name: "payments_account_id_fkey"
  add_foreign_key "purchase_invoice_lines", "computer_component_categories", column: "component_category_id", name: "purchase_invoice_lines_component_category_id_fkey"
  add_foreign_key "purchase_invoice_lines", "computer_components", column: "component_id", name: "purchase_invoice_lines_component_id_fkey"
  add_foreign_key "purchase_invoice_lines", "purchase_invoices", name: "purchase_invoice_lines_purchase_invoice_id_fkey"
  add_foreign_key "sales_deliveries", "sales_invoices", name: "sales_deliveries_sales_invoice_id_fkey"
  add_foreign_key "sales_delivery_lines", "computer_components", column: "component_id", name: "sales_delivery_lines_component_id_fkey"
  add_foreign_key "sales_delivery_lines", "sales_deliveries", name: "sales_delivery_lines_sales_delivery_id_fkey"
  add_foreign_key "sales_invoice_lines", "computer_components", column: "component_id", name: "sales_invoice_lines_component_id_fkey"
  add_foreign_key "sales_invoice_lines", "sales_invoices", name: "sales_invoice_lines_sales_invoice_id_fkey"
  add_foreign_key "sales_invoices", "payment_methods", name: "sales_invoices_payment_method_id_fkey"
  add_foreign_key "sales_invoices", "users", column: "customer_id", name: "sales_invoices_customer_id_fkey"
  add_foreign_key "sales_quote_lines", "computer_components", column: "component_id", name: "sales_quote_lines_component_id_fkey"
  add_foreign_key "sales_quote_lines", "sales_quotes", name: "sales_quote_lines_sales_quote_id_fkey"
  add_foreign_key "sales_quotes", "payment_methods", name: "sales_quotes_payment_method_id_fkey"
  add_foreign_key "sales_quotes", "users", column: "customer_id", name: "sales_quotes_customer_id_fkey"
end
