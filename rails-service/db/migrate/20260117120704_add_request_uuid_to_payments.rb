class AddRequestUuidToPayments < ActiveRecord::Migration[8.1]
  def change
    add_column :payments, :request_uuid, :string
  end
end
