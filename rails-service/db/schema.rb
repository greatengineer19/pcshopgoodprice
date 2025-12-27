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

  create_table "accounts", force: :cascade do |t|
    t.integer "account_code", null: false
    t.string "account_name", null: false
    t.integer "account_type", null: false
    t.datetime "created_at", null: false
    t.boolean "is_active"
    t.integer "normal_balance", null: false
    t.bigint "parent_id"
    t.integer "subtype", null: false
    t.bigint "tax_codes_id"
    t.datetime "updated_at", null: false
    t.index ["account_code"], name: "index_accounts_on_account_code", unique: true
    t.index ["parent_id"], name: "index_accounts_on_parent_id"
    t.index ["tax_codes_id"], name: "index_accounts_on_tax_codes_id"
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

  create_table "payments", force: :cascade do |t|
    t.bigint "account_id", null: false
    t.decimal "amount", precision: 20, scale: 6, default: "0.0", null: false
    t.datetime "created_at", null: false
    t.integer "currency", null: false
    t.bigint "debit_account_id"
    t.integer "payment_method", null: false
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.index ["account_id"], name: "index_payments_on_account_id"
    t.index ["debit_account_id"], name: "index_payments_on_debit_account_id"
    t.index ["user_id"], name: "index_payments_on_user_id"
  end

  create_table "tax_codes", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "name", null: false
    t.decimal "rate", precision: 20, scale: 6, default: "0.0", null: false
    t.datetime "updated_at", null: false
  end

  create_table "users", force: :cascade do |t|
    t.datetime "created_at", default: -> { "CURRENT_TIMESTAMP" }, null: false
    t.string "fullname", null: false
    t.string "hashed_password"
    t.string "password_digest", null: false
    t.string "refresh_token"
    t.datetime "refresh_token_expiry_at", default: -> { "CURRENT_TIMESTAMP" }, null: false
    t.integer "role", default: 0, null: false
    t.datetime "updated_at", default: -> { "CURRENT_TIMESTAMP" }, null: false
    t.string "username"
    t.index ["refresh_token"], name: "index_users_on_refresh_token", unique: true
    t.index ["username"], name: "index_users_on_username", unique: true
  end

  add_foreign_key "accounts", "accounts", column: "parent_id"
  add_foreign_key "journal_entries", "journal_entries", column: "reversed_by_id"
  add_foreign_key "payments", "accounts", column: "debit_account_id"
end
