class CreateImportPaymentEntries < ActiveRecord::Migration[8.1]
  def change
    create_table :import_payment_entries, if_not_exists: true do |t|
      t.integer :total_payments
      t.datetime :start_time
      t.datetime :end_time
      t.string :request_uuid
      t.timestamps
    end
  end
end
