class EditAccountIdAtJournalEntryLines < ActiveRecord::Migration[8.1]
  def change
    remove_column :journal_entry_lines, :accounts_id, if_exists: true
    add_reference :journal_entry_lines, :account, foreign_key: { to_table: :accounts }, if_not_exists: true
  end
end
