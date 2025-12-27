class EditAccountIdAtJournalEntryLines < ActiveRecord::Migration[8.1]
  def change
    remove_column :journal_entry_lines, :accounts_id
    add_reference :journal_entry_lines, :account
  end
end
