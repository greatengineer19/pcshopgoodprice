class AddReversedByToJournalEntries < ActiveRecord::Migration[8.1]
  def change
    remove_column :journal_entries, :reversed_by_id
    add_reference :journal_entries,
                  :reversed_by,
                  foreign_key: { to_table: :journal_entries }
  end
end
