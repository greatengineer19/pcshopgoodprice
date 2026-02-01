class AddRequestUuidIndex < ActiveRecord::Migration[8.1]
  def change
    add_index :payments, :request_uuid
  end
end
