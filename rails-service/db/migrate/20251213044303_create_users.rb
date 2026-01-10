class CreateUsers < ActiveRecord::Migration[8.1]
  def change
    create_table :users, if_not_exists: true do |t|
      t.string "fullname", null: false
      t.string "username"
      t.integer "role", null: false, default: 0
      t.string "hashed_password"
      t.string "refresh_token"
      t.datetime "refresh_token_expiry_at", null: false, default: -> { "CURRENT_TIMESTAMP" }
      t.timestamps null: false, default: -> { "CURRENT_TIMESTAMP" }
    end

    add_index :users, :username, unique: true, if_not_exists: true
    add_index :users, :refresh_token, unique: true, if_not_exists: true
  end
end
