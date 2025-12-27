class CreateJournalEntries < ActiveRecord::Migration[8.1]
  def change
    create_table :journal_entries do |t|
      t.string :entry_number, null: false
      # Polymorphic, reference is transaction id + type
      t.integer :reference_id, null: false
      t.string :reference_type
      t.integer :created_by_id
      t.integer :status, null: false
      t.references :reversed_by, { to_table: :journal_entries }
      t.integer :fiscal_year
      t.integer :fiscal_period
      t.timestamps
    end

    create_table :journal_entry_lines do |t|
      t.references :journal_entry
      t.integer :line_number, null: false
      t.references :accounts
      t.decimal :debit, precision: 20, scale: 6, default: "0.0", null: false
      t.decimal :credit, precision: 20, scale: 6, default: "0.0", null: false
      t.string :description
      t.timestamps
    end

    # Add CHECK constraint
    execute <<-SQL
      ALTER TABLE journal_entry_lines
      ADD CONSTRAINT check_debit_credit CHECK (
        (debit > 0 AND credit = 0) OR 
        (credit > 0 AND debit = 0) OR 
        (debit = 0 AND credit = 0)
      )
    SQL
  end
end
